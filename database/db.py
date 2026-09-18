import sqlite3
import os
import json
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(__file__), "qsentinel.db")

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    cursor = conn.cursor()
    
    # Alerts table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS alerts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            source_ip TEXT DEFAULT '192.168.1.105',
            destination_port INTEGER DEFAULT 80,
            attack_type TEXT NOT NULL,
            threat_level TEXT NOT NULL,
            confidence REAL NOT NULL,
            model_type TEXT NOT NULL,
            status TEXT DEFAULT 'New',
            explanation TEXT DEFAULT '',
            feature_summary TEXT DEFAULT ''
        )
    """)
    
    # Model metrics history table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS model_metrics (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            model_name TEXT NOT NULL,
            accuracy REAL NOT NULL,
            precision REAL NOT NULL,
            recall REAL NOT NULL,
            f1_score REAL NOT NULL,
            details_json TEXT DEFAULT '{}'
        )
    """)

    # Dataset history table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS dataset_records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            dataset_name TEXT NOT NULL,
            record_count INTEGER NOT NULL,
            feature_count INTEGER NOT NULL,
            class_distribution TEXT NOT NULL
        )
    """)
    
    conn.commit()
    conn.close()

def log_alert(attack_type, threat_level, confidence, model_type="Quantum VQC", 
              source_ip="192.168.1.120", destination_port=80, explanation="", feature_summary=""):
    conn = get_db()
    cursor = conn.cursor()
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute("""
        INSERT INTO alerts (timestamp, source_ip, destination_port, attack_type, threat_level, 
                            confidence, model_type, status, explanation, feature_summary)
        VALUES (?, ?, ?, ?, ?, ?, ?, 'New', ?, ?)
    """, (timestamp, source_ip, destination_port, attack_type, threat_level, 
          round(confidence, 4), model_type, explanation, feature_summary))
    conn.commit()
    alert_id = cursor.lastrowid
    conn.close()
    return alert_id

def get_alerts(limit=50, status=None):
    conn = get_db()
    cursor = conn.cursor()
    if status:
        cursor.execute("SELECT * FROM alerts WHERE status = ? ORDER BY id DESC LIMIT ?", (status, limit))
    else:
        cursor.execute("SELECT * FROM alerts ORDER BY id DESC LIMIT ?", (limit,))
    rows = cursor.fetchall()
    alerts = [dict(r) for r in rows]
    conn.close()
    return alerts

def update_alert_status(alert_id, new_status):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("UPDATE alerts SET status = ? WHERE id = ?", (new_status, alert_id))
    conn.commit()
    conn.close()

def log_model_metrics(model_name, accuracy, precision, recall, f1_score, details=None):
    conn = get_db()
    cursor = conn.cursor()
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute("""
        INSERT INTO model_metrics (timestamp, model_name, accuracy, precision, recall, f1_score, details_json)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (timestamp, model_name, round(accuracy, 4), round(precision, 4), 
          round(recall, 4), round(f1_score, 4), json.dumps(details or {})))
    conn.commit()
    conn.close()

def get_latest_metrics():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT * FROM model_metrics ORDER BY id DESC LIMIT 10
    """)
    rows = cursor.fetchall()
    metrics = [dict(r) for r in rows]
    conn.close()
    return metrics
