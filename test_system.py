import os
import sys
import unittest
import json

# Ensure app directory in sys.path
sys.path.insert(0, os.path.dirname(__file__))

from app import app
from database.db import init_db, log_alert, get_alerts
from ml.preprocessor import preprocessor
from ml.classical_model import classical_model
from quantum.vqc_classifier import quantum_model

class TestQSentinel(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        init_db()
        cls.client = app.test_client()

    def test_01_preprocessor_and_dataset(self):
        csv_path = os.path.join(os.path.dirname(__file__), 'data', 'sample_network_traffic.csv')
        self.assertTrue(os.path.exists(csv_path), "Sample dataset CSV does not exist")
        
        summary = preprocessor.load_dataset(csv_path)
        self.assertGreater(summary['total_records'], 1000)
        self.assertGreater(summary['attack_count'], 0)
        self.assertIn('Normal', summary['class_distribution'])
        
        prep_info = preprocessor.prepare_and_split(n_quantum_features=4)
        self.assertEqual(len(prep_info['quantum_features']), 4)
        self.assertEqual(preprocessor.X_train_quantum.shape[1], 4)
        print("[PASS] Preprocessor and dataset test passed.")

    def test_02_classical_model(self):
        metrics = classical_model.train(
            preprocessor.X_train_classical, preprocessor.y_train_binary, preprocessor.y_train_multi,
            preprocessor.X_test_classical, preprocessor.y_test_binary, preprocessor.y_test_multi,
            preprocessor.classes_, preprocessor.feature_cols
        )
        self.assertGreater(metrics['accuracy'], 0.80)
        self.assertIn('confusion_matrix_binary', metrics)
        print(f"[PASS] Classical model trained successfully (Accuracy: {metrics['accuracy'] * 100:.1f}%).")

    def test_03_quantum_vqc_model(self):
        metrics = quantum_model.train(
            preprocessor.X_train_quantum, preprocessor.y_train_binary,
            preprocessor.X_test_quantum, preprocessor.y_test_binary,
            preprocessor.selected_feature_names, preprocessor.classes_,
            maxiter=20
        )
        self.assertGreater(metrics['accuracy'], 0.55)
        self.assertIn('confusion_matrix', metrics)
        
        circuit = quantum_model.get_circuit_representation()
        self.assertIn('ascii_diagram', circuit)
        self.assertGreater(len(circuit['ascii_diagram']), 20)
        print(f"[PASS] Quantum VQC trained successfully with Qiskit Statevector (Accuracy: {metrics['accuracy'] * 100:.1f}%).")

    def test_04_flask_routes(self):
        # Dashboard page
        res = self.client.get('/')
        self.assertEqual(res.status_code, 200)
        self.assertIn(b'Q-SENTINEL', res.data)

        # Dataset page
        res = self.client.get('/dataset')
        self.assertEqual(res.status_code, 200)

        # Quantum page
        res = self.client.get('/quantum')
        self.assertEqual(res.status_code, 200)

        # Detection page
        res = self.client.get('/detection')
        self.assertEqual(res.status_code, 200)

        # Comparison page
        res = self.client.get('/comparison')
        self.assertEqual(res.status_code, 200)

        # Alerts page
        res = self.client.get('/alerts')
        self.assertEqual(res.status_code, 200)

        # About page
        res = self.client.get('/about')
        self.assertEqual(res.status_code, 200)

        print("[PASS] All Flask web pages returned HTTP 200.")

    def test_05_prediction_api_and_alert_trigger(self):
        # Test DDoS attack packet prediction
        ddos_payload = {
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
        }

        res = self.client.post('/api/predict', json=ddos_payload)
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertTrue(data['success'])
        self.assertTrue(data['is_attack'])
        self.assertIn(data['threat_level'], ['High', 'Critical', 'Medium'])
        self.assertIsNotNone(data['alert_id'])
        self.assertIn('quantum_prediction', data)
        self.assertIn('explanation_list', data)
        print(f"[PASS] Attack prediction API passed. Verdict: {data['attack_type']}, Alert ID: #{data['alert_id']}")

        # Verify alert appears in database
        alerts = get_alerts(limit=5)
        self.assertGreater(len(alerts), 0)
        print("[PASS] SQLite alert ledger verification passed.")

if __name__ == '__main__':
    unittest.main()
