# Q-Sentinel – Quantum Machine Learning Based Network Intrusion Detection System

[![Python](https://img.shields.io/badge/Python-3.11-blue.svg)](https://python.org)
[![Qiskit](https://img.shields.io/badge/Qiskit-2.5-6929C4.svg)](https://qiskit.org)
[![Flask](https://img.shields.io/badge/Flask-3.1-black.svg)](https://flask.palletsprojects.com/)
[![Scikit-Learn](https://img.shields.io/badge/Scikit--Learn-1.9-orange.svg)](https://scikit-learn.org)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

> *“AI detects patterns. Quantum Machine Learning explores a new approach to detecting complex cyber threats.”*

---

## 🛡️ Project Overview

**Q-Sentinel** is a complete, production-grade cybersecurity application that detects malicious network intrusions (DDoS, Port Scan, Brute Force, Botnet) using a hybrid **Classical Machine Learning** and **Quantum Machine Learning (Variational Quantum Classifier - VQC)** architecture.

The application features a modern **SOC (Security Operations Center)** dark-themed web dashboard with live packet telemetry, dataset preprocessing, quantum circuit inspection, side-by-side performance benchmarks, explainable AI reasoning, audible intrusion alerts, and a structured 10-step seminar demo flow.

---

## ⚙️ Core Architecture & Workflow

```
Network Traffic Dataset (CSV)
         │
         ▼
Data Preprocessing & Cleaning (Nulls, Types, Encodings)
         │
         ▼
Feature Selection (ANOVA F-Value Score, K=4 Qubits)
         │
         ├────────────────────────────────────────┐
         ▼                                        ▼
Classical ML Model (Random Forest / SVM)    Quantum ML Model (Qiskit VQC)
• Decision Tree Ensembles                  • Angle Feature Map: Ry(x), Rz(2x)
• Multi-Class Attack Classification        • Circular Entanglement: CX Ring
• High-Speed Baseline Inference            • Variational Ansatz: W(θ) Layers
         │                                 • Pauli-Z Expectation: <Z_0>
         └───────────────────┬────────────────────┘
                             ▼
                   Live Attack Detection
            (Threat Severity, Confidence, XAI)
                             │
                             ▼
                   SOC Alerts & Dashboard
          (Audible Siren, SQLite Audit Ledger)
```

---

## 🚀 Key Features

1. **SOC Security Dashboard**:
   - Total network records, benign sessions, attack count, and attack percentage.
   - Dynamic threat posture indicator (`Nominal`, `Medium`, `High`, `Critical`).
   - Interactive Chart.js graphs for traffic balance and attack vector profiles.
   - Recent incursion alerts with instant status resolution.

2. **Dataset Analysis & Upload**:
   - Ingest custom network traffic CSV files or load pre-bundled 1,500-record dataset.
   - Automatic missing value detection and column schema summary.
   - Interactive preview table with search and pagination.
   - Dynamic class detection: automatically supports whatever attack types are present.

3. **Data Preprocessing & Feature Selection**:
   - Imputes missing numerical values and encodes categorical headers.
   - Selects top $K$ features (default 4 features for a 4-qubit circuit) via ANOVA F-value test.
   - Scales features to $[0, \pi]$ using `MinMaxScaler` for direct quantum angle parameterization.
   - Stratified train/test splitting (80/20 or 70/30).

4. **Quantum Machine Learning Model (VQC)**:
   - Built with **Qiskit 2.5** and local **Statevector Simulation** (no real quantum hardware or cloud tokens required).
   - Parameterized single-qubit rotations $R_y(\theta), R_z(\theta)$ and multi-qubit CNOT entanglement rings.
   - Pauli-Z observable measurement $\langle Z_0 \rangle \in [-1, 1]$ mapped to attack probability $P(\text{Attack}) = \frac{1 - \langle Z_0 \rangle}{2}$.
   - Real, non-faked optimization using SciPy's COBYLA algorithm with real loss convergence curve.
   - ASCII and structured circuit diagram visualizer showing every gate operation.
   - Native pure NumPy quantum simulation fallback engine for zero-dependency portability.

5. **Classical vs Quantum Comparison**:
   - Side-by-side benchmark metrics: **Accuracy, Precision, Recall, F1-Score, Inference Latency**.
   - Dual interactive **Confusion Matrices** for both Classical and Quantum models.
   - Comparative Radar profile chart across 6 operational dimensions.

6. **Live Prediction & Attack Simulation**:
   - Interactive form to input packet metrics or select 1-click attack simulation presets:
     - **DDoS Volumetric Flood**
     - **Stealth SYN Port Sweep**
     - **SSH Credential Brute Force**
     - **Mirai Botnet C2 Communication**
     - **Benign HTTPS Web Browsing**
   - Returns consolidated threat verdict, confidence percentage, risk severity, and **Explainable AI (XAI)** reasoning.

7. **SOC Security Alerts & Web Audio Siren**:
   - Automatically logs attacks to SQLite database (`database/qsentinel.db`).
   - Generates prominent pulsating red security incursion banner.
   - Synthesizes realistic SOC alert siren tones directly in the browser via Web Audio API (with mute toggle).
   - Export incident audit ledger as JSON.

8. **Seminar Demo Mode**:
   - Built-in 10-step guided walk-through overlay designed for presentations, defenses, and seminars.

---

## 📦 Project Structure

```
q-sentinel/
├── app.py                      # Flask web application & REST API
├── requirements.txt            # Python dependencies
├── README.md                   # Documentation & setup guide
├── data/
│   ├── sample_network_traffic.csv  # Pre-bundled 1500-sample IDS dataset
│   └── generate_dataset.py     # Realistic dataset generator script
├── database/
│   ├── db.py                   # SQLite schema, alert logging, and audit queries
│   └── qsentinel.db            # SQLite database file
├── ml/
│   ├── __init__.py
│   ├── preprocessor.py         # Data cleaning, scaling to [0, π], feature selection
│   └── classical_model.py      # Random Forest & SVM classifiers, confusion matrix
├── quantum/
│   ├── __init__.py
│   └── vqc_classifier.py       # Qiskit 2.5 Variational Quantum Classifier
├── static/
│   ├── css/
│   │   └── soc-theme.css       # Complete SOC cybersecurity dark theme
│   └── js/
│       ├── app.js              # Core UI interactions, Web Audio alerts, charts
│       └── demo-tour.js        # 10-step interactive seminar demo walk-through
└── templates/
    ├── base.html               # Shared layout: sidebar, topbar, audio toggle
    ├── dashboard.html          # Main SOC telemetry view & charts
    ├── dataset.html            # Dataset upload, preview & preprocessing controls
    ├── quantum.html            # Quantum circuit diagram, gate breakdown & training
    ├── detection.html          # Live attack detection console & presets
    ├── comparison.html         # Classical ML vs QML benchmarks & confusion matrices
    ├── alerts.html             # Security incident response & export
    └── about.html              # System architecture & mathematical formulation
```

---

## 💻 Installation & Quick Start

### 1. Clone or Open Workspace
```bash
cd c:/Users/ramya/Q-sentinel
```

### 2. Verify Python Dependencies
The project requires Python 3.10+ (tested on Python 3.11):
```bash
pip install -r requirements.txt
```

### 3. Run the Web Application
```bash
python app.py
```

### 4. Open in Browser
Navigate to:
```
http://127.0.0.1:5000
```
*The application automatically preloads the sample dataset and bootstraps models on launch!*

---

## 🎓 10-Step Seminar Demo Walkthrough

Click the **"Seminar Demo Flow"** button in the top navigation bar to activate the interactive guided tour:

1. **Step 1: Open Dashboard** (`/dashboard`) – Review SOC metrics, benign/attack traffic ratio, and threat posture.
2. **Step 2: Ingest Dataset** (`/dataset`) – Load the multi-class dataset or drag-and-drop a custom network CSV.
3. **Step 3: Analyze Preprocessing** (`/dataset`) – Inspect missing values and select the top 4 features for qubit mapping.
4. **Step 4: Train Classical ML** (`/comparison`) – Train Random Forest and view test accuracy and F1-score.
5. **Step 5: Train Quantum ML (VQC)** (`/quantum`) – Run variational optimization with Qiskit 2.5 Statevector simulation.
6. **Step 6: Show Quantum Circuit** (`/quantum`) – Examine the circuit diagram with Hadamard, Ry, Rz, and CX entanglement rings.
7. **Step 7: Compare Classical ML vs QML** (`/comparison`) – Compare side-by-side metrics and dual confusion matrices.
8. **Step 8: Enter Suspicious Traffic** (`/detection`) – Click **"DDoS Flood"** or **"Port Scan"** to inject malicious packet metrics.
9. **Step 9: Detect the Attack** (`/detection`) – Execute hybrid inference and examine the quantum expectation value $\langle Z_0 \rangle$ and XAI breakdown.
10. **Step 10: Prominent Red Alert** (`/detection`) – Audio siren sounds, red alert banner displays, and the concluding motto appears:

> *“AI detects patterns. Quantum Machine Learning explores a new approach to detecting complex cyber threats.”*

---

## 🔬 Mathematical Formulation of the VQC

### 1. Quantum State Preparation (Feature Map)
For input packet vector $x = [x_0, x_1, x_2, x_3]$ scaled to $[0, \pi]$:
$$|\psi_0(x)\rangle = \bigotimes_{i=0}^{n-1} R_z(2x_i) R_y(x_i) H |0\rangle$$

### 2. Entanglement Ring
Entangles adjacent qubit registers to capture non-classical correlations between packet rate and payload size:
$$U_{\text{ent}} = \prod_{i=0}^{n-1} \text{CX}(q_i, q_{(i+1) \pmod n})$$

### 3. Variational Ansatz & Expectation
$$|\psi(\theta, x)\rangle = W(\theta) U_{\Phi}(x) |0\rangle^{\otimes n}$$
$$\langle Z_0 \rangle = \langle \psi(\theta, x) | Z_0 | \psi(\theta, x) \rangle \in [-1, 1]$$
$$P(\text{Attack}) = \frac{1 - \langle Z_0 \rangle}{2}$$

---

## 📡 REST API Reference

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/dataset/summary` | Returns dataset statistics and class distribution |
| `POST` | `/api/dataset/upload` | Upload and process custom network CSV |
| `POST` | `/api/dataset/load-sample` | Reload default demo dataset |
| `POST` | `/api/preprocess` | Run feature selection and train/test split |
| `POST` | `/api/train/classical` | Train Random Forest or SVM model |
| `POST` | `/api/train/quantum` | Train Variational Quantum Classifier (VQC) |
| `GET` | `/api/circuit/diagram` | Get ASCII and structured circuit gate data |
| `POST` | `/api/predict` | Live packet inference with XAI reasoning and alert logging |
| `GET` | `/api/alerts` | Get recent security alerts from SQLite |
| `POST` | `/api/alerts/status` | Update alert status (`Investigating`, `Resolved`, `Dismissed`) |
| `GET` | `/api/demo/preset/<type>` | Get pre-configured attack vector telemetry |
