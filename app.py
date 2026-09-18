import os
import json
import time
from flask import Flask, render_template, request, jsonify, redirect, url_for
from werkzeug.utils import secure_filename
import pandas as pd
import numpy as np

from database.db import init_db, log_alert, get_alerts, update_alert_status, log_model_metrics, get_latest_metrics
from ml.preprocessor import preprocessor
from ml.classical_model import classical_model
from quantum.vqc_classifier import quantum_model

app = Flask(__name__)
app.config['SECRET_KEY'] = 'q-sentinel-cyber-quantum-secret-key-2026'
app.config['UPLOAD_FOLDER'] = os.path.join(os.path.dirname(__file__), 'data')
app.config['MAX_CONTENT_LENGTH'] = 32 * 1024 * 1024  # 32MB max

# Ensure folders exist and initialize SQLite DB
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
init_db()

# Preload sample dataset on application bootstrap
SAMPLE_DATASET_PATH = os.path.join(app.config['UPLOAD_FOLDER'], 'sample_network_traffic.csv')

def bootstrap_application():
    """Preloads sample dataset and initializes models if available."""
    try:
        if os.path.exists(SAMPLE_DATASET_PATH):
            preprocessor.load_dataset(SAMPLE_DATASET_PATH)
            prep_info = preprocessor.prepare_and_split(n_quantum_features=4)
            # Train classical model on startup
            classical_model.train(
                preprocessor.X_train_classical, preprocessor.y_train_binary, preprocessor.y_train_multi,
                preprocessor.X_test_classical, preprocessor.y_test_binary, preprocessor.y_test_multi,
                preprocessor.classes_, preprocessor.feature_cols
            )
            # Train quantum model with quick convergence
            quantum_model.train(
                preprocessor.X_train_quantum, preprocessor.y_train_binary,
                preprocessor.X_test_quantum, preprocessor.y_test_binary,
                preprocessor.selected_feature_names, preprocessor.classes_,
                maxiter=20
            )
            print("Q-Sentinel bootstrapped successfully with sample dataset and models trained.")
    except Exception as e:
        print(f"Bootstrap note: {e}")

# Call bootstrap
bootstrap_application()

@app.context_processor
def inject_global_summary():
    summary = preprocessor.get_summary() if preprocessor.raw_df is not None else {}
    return dict(summary=summary)

# ----------------- PAGE ROUTES ----------------- #

@app.route('/')
@app.route('/dashboard')
def index_page():
    summary = preprocessor.get_summary() if preprocessor.raw_df is not None else {}
    circuit_data = quantum_model.get_circuit_representation()
    alerts = get_alerts(limit=8)
    return render_template('index.html', summary=summary, circuit_data=circuit_data, 
                           quantum_model=quantum_model, classical_model=classical_model, alerts=alerts)

@app.route('/soc')
def dashboard_soc_page():
    summary = preprocessor.get_summary() if preprocessor.raw_df is not None else {}
    alerts = get_alerts(limit=8)
    return render_template('dashboard.html', summary=summary, alerts=alerts, active_page='dashboard')

@app.route('/dataset')
def dataset_page():
    summary = preprocessor.get_summary() if preprocessor.raw_df is not None else {}
    return render_template('dataset.html', summary=summary, active_page='dataset')

@app.route('/quantum')
def quantum_page():
    summary = preprocessor.get_summary() if preprocessor.raw_df is not None else {}
    circuit_data = quantum_model.get_circuit_representation()
    return render_template('quantum.html', summary=summary, circuit_data=circuit_data, 
                           quantum_model=quantum_model, active_page='quantum')

@app.route('/detection')
def detection_page():
    summary = preprocessor.get_summary() if preprocessor.raw_df is not None else {}
    features = preprocessor.feature_cols if preprocessor.is_fitted else []
    return render_template('detection.html', summary=summary, features=features, active_page='detection')

@app.route('/comparison')
def comparison_page():
    summary = preprocessor.get_summary() if preprocessor.raw_df is not None else {}
    return render_template('comparison.html', 
                           summary=summary,
                           classical_metrics=classical_model.metrics,
                           quantum_metrics=quantum_model.metrics,
                           active_page='comparison')

@app.route('/alerts')
def alerts_page():
    summary = preprocessor.get_summary() if preprocessor.raw_df is not None else {}
    alerts = get_alerts(limit=100)
    return render_template('alerts.html', summary=summary, alerts=alerts, active_page='alerts')

@app.route('/about')
def about_page():
    summary = preprocessor.get_summary() if preprocessor.raw_df is not None else {}
    return render_template('about.html', summary=summary, active_page='about')

# ----------------- REST API ENDPOINTS ----------------- #

@app.route('/api/dataset/summary', methods=['GET'])
def api_dataset_summary():
    if preprocessor.raw_df is None:
        return jsonify({"success": False, "error": "No dataset loaded"}), 404
    return jsonify({"success": True, "data": preprocessor.get_summary()})

@app.route('/api/dataset/upload', methods=['POST'])
def api_dataset_upload():
    if 'dataset' not in request.files:
        return jsonify({"success": False, "error": "No file uploaded"}), 400
        
    file = request.files['dataset']
    if file.filename == '':
        return jsonify({"success": False, "error": "No selected file"}), 400
        
    if not file.filename.endswith('.csv'):
        return jsonify({"success": False, "error": "Only CSV files are supported"}), 400
        
    filename = secure_filename(file.filename)
    save_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(save_path)
    
    try:
        summary = preprocessor.load_dataset(save_path)
        # Re-run preprocessing
        prep_info = preprocessor.prepare_and_split(n_quantum_features=4)
        return jsonify({
            "success": True, 
            "message": f"Dataset '{filename}' uploaded and processed successfully.",
            "summary": summary,
            "preprocessing": prep_info
        })
    except Exception as e:
        return jsonify({"success": False, "error": f"Failed to process CSV: {str(e)}"}), 500

@app.route('/api/dataset/load-sample', methods=['POST'])
def api_dataset_load_sample():
    try:
        summary = preprocessor.load_dataset(SAMPLE_DATASET_PATH)
        prep_info = preprocessor.prepare_and_split(n_quantum_features=4)
        return jsonify({
            "success": True,
            "message": "Demo sample dataset loaded successfully.",
            "summary": summary,
            "preprocessing": prep_info
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/preprocess', methods=['POST'])
def api_preprocess():
    data = request.get_json() or {}
    n_features = int(data.get('n_features', 4))
    test_size = float(data.get('test_size', 0.2))
    
    try:
        result = preprocessor.prepare_and_split(n_quantum_features=n_features, test_size=test_size)
        return jsonify({"success": True, "data": result})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/train/classical', methods=['POST'])
def api_train_classical():
    if not preprocessor.is_fitted:
        return jsonify({"success": False, "error": "Please preprocess the dataset first"}), 400
        
    data = request.get_json() or {}
    model_type = data.get('model_type', 'random_forest')
    classical_model.model_type = model_type
    
    try:
        metrics = classical_model.train(
            preprocessor.X_train_classical, preprocessor.y_train_binary, preprocessor.y_train_multi,
            preprocessor.X_test_classical, preprocessor.y_test_binary, preprocessor.y_test_multi,
            preprocessor.classes_, preprocessor.feature_cols
        )
        log_model_metrics(metrics["model_type"], metrics["accuracy"], metrics["precision"], 
                          metrics["recall"], metrics["f1_score"], metrics)
        return jsonify({"success": True, "metrics": metrics})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/train/quantum', methods=['POST'])
def api_train_quantum():
    if not preprocessor.is_fitted:
        return jsonify({"success": False, "error": "Please preprocess the dataset first"}), 400
        
    data = request.get_json() or {}
    maxiter = int(data.get('maxiter', 25))
    
    try:
        metrics = quantum_model.train(
            preprocessor.X_train_quantum, preprocessor.y_train_binary,
            preprocessor.X_test_quantum, preprocessor.y_test_binary,
            preprocessor.selected_feature_names, preprocessor.classes_,
            maxiter=maxiter
        )
        log_model_metrics(metrics["model_type"], metrics["accuracy"], metrics["precision"], 
                          metrics["recall"], metrics["f1_score"], metrics)
        circuit = quantum_model.get_circuit_representation()
        return jsonify({"success": True, "metrics": metrics, "circuit": circuit})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/circuit/diagram', methods=['GET'])
def api_circuit_diagram():
    circuit = quantum_model.get_circuit_representation()
    return jsonify({"success": True, "data": circuit})

@app.route('/api/comparison', methods=['GET'])
def api_comparison():
    return jsonify({
        "success": True,
        "classical": classical_model.metrics if classical_model.is_trained else None,
        "quantum": quantum_model.metrics if quantum_model.is_trained else None
    })

@app.route('/api/predict', methods=['POST'])
def api_predict():
    if not preprocessor.is_fitted:
        return jsonify({"success": False, "error": "Models are not initialized with data yet"}), 400
        
    data = request.get_json() or {}
    record = data.get('features', {})
    source_ip = data.get('source_ip', '192.168.1.188')
    dest_port = int(record.get('destination_port', 80))
    
    try:
        # Preprocess features
        x_class, x_quant, selected_features_dict = preprocessor.transform_single_record(record)
        
        # Classical prediction
        c_pred = classical_model.predict(x_class) if classical_model.is_trained else {
            "is_attack": False, "attack_type": "Uncertain", "confidence": 0.5, "threat_level": "Low", "risk_color": "gray"
        }
        
        # Quantum prediction
        q_pred = quantum_model.predict(x_quant)
        
        # Generate Explainable AI reasoning
        explanations = []
        if float(record.get('flow_packets_per_sec', 0)) > 2000:
            explanations.append(f"Abnormal packet velocity: {record.get('flow_packets_per_sec')} pkts/sec (typical normal < 300)")
        if int(record.get('syn_flag_count', 0)) > 15:
            explanations.append(f"High SYN flag saturation ({record.get('syn_flag_count')} SYN packets) indicates potential SYN-flood or port sweep")
        if int(record.get('total_fwd_packets', 0)) > 100 and int(record.get('total_bwd_packets', 0)) <= 2:
            explanations.append("Severe unidirectional packet asymmetry (zero or minimal return ACK traffic)")
        if dest_port in [22, 21, 3389]:
            explanations.append(f"Targeting critical management service port {dest_port} (SSH/FTP/RDP)")
        if dest_port in [6667, 1337, 4444, 9001]:
            explanations.append(f"Suspicious destination port {dest_port} associated with Command & Control (C2) / Botnet IRC")
        if float(record.get('flow_duration', 0)) < 20 and int(record.get('total_fwd_packets', 0)) <= 2:
            explanations.append(f"Micro-flow duration ({record.get('flow_duration')} ms) with single probe packet is signature of Port Reconnaissance")
        if not explanations:
            if q_pred['is_attack'] or c_pred['is_attack']:
                explanations.append(f"Quantum state observable rotation shifted into non-benign Hilbert subspace (<Z_0>={q_pred.get('expectation_value_z0')})")
            else:
                explanations.append("Traffic metrics match nominal benign HTTP/TLS operational baseline distributions.")
                
        explanation_text = " | ".join(explanations)
        
        # Consolidated threat verdict (weighted towards Quantum & Classical agreement)
        is_attack = q_pred['is_attack'] or c_pred['is_attack']
        attack_type = c_pred['attack_type'] if is_attack else "Normal"
        if attack_type == "Normal" and is_attack:
            attack_type = "Quantum-Detected Anomaly"
            
        threat_level = c_pred['threat_level'] if c_pred['threat_level'] != "Low" else q_pred['threat_level']
        confidence = round(max(c_pred['confidence'], q_pred['confidence']), 4)
        
        alert_id = None
        if is_attack:
            alert_id = log_alert(
                attack_type=attack_type,
                threat_level=threat_level,
                confidence=confidence,
                model_type=f"Hybrid QML ({quantum_model.execution_mode})",
                source_ip=source_ip,
                destination_port=dest_port,
                explanation=explanation_text,
                feature_summary=json.dumps(selected_features_dict)
            )
            
        return jsonify({
            "success": True,
            "is_attack": is_attack,
            "attack_type": attack_type,
            "threat_level": threat_level,
            "confidence": confidence,
            "alert_id": alert_id,
            "explanation": explanation_text,
            "explanation_list": explanations,
            "classical_prediction": c_pred,
            "quantum_prediction": q_pred,
            "quantum_features_used": selected_features_dict
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/alerts', methods=['GET'])
def api_alerts():
    status = request.args.get('status')
    alerts = get_alerts(limit=100, status=status)
    return jsonify({"success": True, "alerts": alerts})

@app.route('/api/alerts/status', methods=['POST'])
def api_alerts_status():
    data = request.get_json() or {}
    alert_id = data.get('alert_id')
    new_status = data.get('status', 'Resolved')
    if not alert_id:
        return jsonify({"success": False, "error": "Missing alert_id"}), 400
    update_alert_status(alert_id, new_status)
    return jsonify({"success": True, "message": f"Alert #{alert_id} updated to {new_status}"})

@app.route('/api/demo/preset/<attack_type>', methods=['GET'])
def api_demo_preset(attack_type):
    """Returns curated packet feature vectors for instant demo simulation."""
    presets = {
        "ddos": {
            "name": "DDoS Volumetric UDP/SYN Flood",
            "source_ip": "185.220.101.44",
            "features": {
                "flow_duration": 480.5,
                "total_fwd_packets": 420,
                "total_bwd_packets": 1,
                "flow_bytes_per_sec": 3200000.0,
                "flow_packets_per_sec": 8750.0,
                "packet_length_mean": 64.0,
                "packet_length_std": 12.0,
                "syn_flag_count": 280,
                "ack_flag_count": 0,
                "urg_flag_count": 0,
                "destination_port": 80,
                "protocol_type": "TCP"
            }
        },
        "portscan": {
            "name": "Stealth SYN Port Sweep",
            "source_ip": "45.143.221.8",
            "features": {
                "flow_duration": 12.4,
                "total_fwd_packets": 2,
                "total_bwd_packets": 0,
                "flow_bytes_per_sec": 1200.0,
                "flow_packets_per_sec": 2400.0,
                "packet_length_mean": 44.0,
                "packet_length_std": 0.0,
                "syn_flag_count": 1,
                "ack_flag_count": 0,
                "urg_flag_count": 0,
                "destination_port": 445,
                "protocol_type": "TCP"
            }
        },
        "bruteforce": {
            "name": "SSH Credential Brute Force Incursion",
            "source_ip": "194.26.29.112",
            "features": {
                "flow_duration": 7200.0,
                "total_fwd_packets": 54,
                "total_bwd_packets": 48,
                "flow_bytes_per_sec": 24500.0,
                "flow_packets_per_sec": 75.0,
                "packet_length_mean": 140.0,
                "packet_length_std": 38.0,
                "syn_flag_count": 4,
                "ack_flag_count": 52,
                "urg_flag_count": 0,
                "destination_port": 22,
                "protocol_type": "TCP"
            }
        },
        "botnet": {
            "name": "Mirai C2 Beaconing Communication",
            "source_ip": "91.240.118.17",
            "features": {
                "flow_duration": 42000.0,
                "total_fwd_packets": 18,
                "total_bwd_packets": 14,
                "flow_bytes_per_sec": 4800.0,
                "flow_packets_per_sec": 12.0,
                "packet_length_mean": 320.0,
                "packet_length_std": 145.0,
                "syn_flag_count": 1,
                "ack_flag_count": 12,
                "urg_flag_count": 1,
                "destination_port": 6667,
                "protocol_type": "TCP"
            }
        },
        "normal": {
            "name": "Benign HTTPS Web Browsing",
            "source_ip": "10.0.4.52",
            "features": {
                "flow_duration": 18500.0,
                "total_fwd_packets": 16,
                "total_bwd_packets": 22,
                "flow_bytes_per_sec": 68000.0,
                "flow_packets_per_sec": 85.0,
                "packet_length_mean": 820.0,
                "packet_length_std": 180.0,
                "syn_flag_count": 1,
                "ack_flag_count": 21,
                "urg_flag_count": 0,
                "destination_port": 443,
                "protocol_type": "TCP"
            }
        }
    }
    preset = presets.get(attack_type.lower(), presets["normal"])
    return jsonify({"success": True, "data": preset})

if __name__ == '__main__':
    print("Starting Q-Sentinel on http://127.0.0.1:5000")
    app.run(host='127.0.0.1', port=5000, debug=True)
