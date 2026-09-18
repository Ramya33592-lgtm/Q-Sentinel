/**
 * Q-SENTINEL: 10-STEP SEMINAR DEMO ORCHESTRATOR
 * Step 1: Open Dashboard
 * Step 2: Upload / Load Network Traffic Dataset
 * Step 3: Show Dataset Analysis & Class Balance
 * Step 4: Train Classical ML Model (Random Forest / SVM)
 * Step 5: Train Quantum ML Model (VQC with Qiskit 2.5)
 * Step 6: Show Quantum Circuit & Entanglement Gates
 * Step 7: Compare Classical ML vs QML (Accuracy, F1, Confusion Matrix)
 * Step 8: Enter Suspicious Traffic (Inject Attack Vector Preset)
 * Step 9: Detect the Attack (Hybrid Classical-Quantum Evaluation)
 * Step 10: Display Red Security Alert & Concluding Quantum Defense Motto
 */

const DEMO_STEPS = [
  {
    step: 1,
    title: "1. Open Security Operations Dashboard",
    page: "/dashboard",
    desc: "Observe the real-time SOC dashboard displaying live packet volume, attack distribution, current threat level gauge, and historical incursion alerts.",
    actionName: "Go to Dashboard"
  },
  {
    step: 2,
    title: "2. Load Network Traffic Dataset",
    page: "/dataset",
    desc: "Ingest network flow telemetry records. You can upload a custom CSV or load the pre-bundled multi-class dataset (Normal, DDoS, Port Scan, Brute Force, Botnet).",
    actionName: "Load Sample Dataset",
    execute: async () => {
      if (window.loadSampleDataset) {
        await window.loadSampleDataset();
      }
    }
  },
  {
    step: 3,
    title: "3. Dataset Analysis & Preprocessing",
    page: "/dataset",
    desc: "Inspect missing values, feature distributions, class balance, and the ANOVA F-value feature selection engine scaling top features to [0, π] for quantum encoding.",
    actionName: "Review Preprocessing"
  },
  {
    step: 4,
    title: "4. Train Classical ML Model",
    page: "/comparison",
    desc: "Train the Classical Random Forest classifier on the training split. Evaluate its decision trees, multi-class boundary, and training latency.",
    actionName: "Train Classical Model",
    execute: async () => {
      if (window.trainClassicalModel) {
        await window.trainClassicalModel();
      }
    }
  },
  {
    step: 5,
    title: "5. Train Quantum ML Model (VQC)",
    page: "/quantum",
    desc: "Execute the Variational Quantum Classifier (VQC) parameterized optimization using Qiskit 2.5 Statevector simulation and SciPy COBYLA optimizer.",
    actionName: "Train Quantum VQC",
    execute: async () => {
      if (window.trainQuantumModel) {
        await window.trainQuantumModel();
      }
    }
  },
  {
    step: 6,
    title: "6. Inspect Quantum Circuit & Gates",
    page: "/quantum",
    desc: "Visualize the Quantum Circuit: Hadamard superposition gates, Angle encoding Ry(x_i), Phase Rz(2x_i), CNOT circular entanglement rings, and Pauli-Z measurement operator.",
    actionName: "View Circuit Architecture"
  },
  {
    step: 7,
    title: "7. Compare Classical ML vs QML",
    page: "/comparison",
    desc: "Examine side-by-side performance benchmarks: Real Accuracy, Precision, Recall, F1-Score, and dual Confusion Matrices on the held-out test split.",
    actionName: "Analyze Benchmarks"
  },
  {
    step: 8,
    title: "8. Inject Suspicious Traffic Packet",
    page: "/detection",
    desc: "Inject an anomalous network traffic packet into the live detection console using the DDoS Volumetric Flood or Stealth Port Scan preset.",
    actionName: "Inject DDoS Attack Preset",
    execute: async () => {
      if (window.injectAttackPreset) {
        await window.injectAttackPreset('ddos');
      }
    }
  },
  {
    step: 9,
    title: "9. Detect the Attack (Hybrid Inference)",
    page: "/detection",
    desc: "Evaluate the packet through the hybrid pipeline. Observe the Quantum Expectation Value <Z_0> shift, confidence level, and Explainable AI reasoning.",
    actionName: "Run Threat Detection",
    execute: async () => {
      if (window.runPrediction) {
        await window.runPrediction();
      }
    }
  },
  {
    step: 10,
    title: "10. Prominent Red Security Alert & Motto",
    page: "/detection",
    desc: "A red incursion alert is generated with audible alarm and logged into the SOC incident ledger. Concluding with the Quantum Cybersecurity Motto!",
    actionName: "Finish Demo",
    execute: () => {
      if (window.socAudio) {
        window.socAudio.playAlarm('Critical');
      }
      showConcludingMotto();
    }
  }
];

class SeminarDemoManager {
  constructor() {
    this.currentStep = parseInt(sessionStorage.getItem('qsentinel_demo_step') || '1');
    this.isOpen = sessionStorage.getItem('qsentinel_demo_active') === 'true';
    this.initUI();
  }

  initUI() {
    // If demo mode is active on page load, update floating guide
    if (this.isOpen) {
      this.renderFloatingWidget();
    }
  }

  startDemo() {
    this.currentStep = 1;
    this.isOpen = true;
    sessionStorage.setItem('qsentinel_demo_active', 'true');
    sessionStorage.setItem('qsentinel_demo_step', '1');
    this.goToStep(1);
  }

  closeDemo() {
    this.isOpen = false;
    sessionStorage.setItem('qsentinel_demo_active', 'false');
    const widget = document.getElementById('demo-floating-widget');
    if (widget) widget.remove();
  }

  async goToStep(stepNum) {
    if (stepNum < 1 || stepNum > 10) return;
    this.currentStep = stepNum;
    sessionStorage.setItem('qsentinel_demo_step', stepNum);

    const step = DEMO_STEPS[stepNum - 1];
    const currentPath = window.location.pathname;

    // If step requires navigating to a different page
    if (step.page && currentPath !== step.page && !(currentPath === '/' && step.page === '/dashboard')) {
      window.location.href = step.page;
      return;
    }

    this.renderFloatingWidget();

    // Execute step action if applicable
    if (step.execute) {
      try {
        await step.execute();
      } catch (e) {
        console.error("Step execution note:", e);
      }
    }
  }

  nextStep() {
    if (this.currentStep < 10) {
      this.goToStep(this.currentStep + 1);
    } else {
      showConcludingMotto();
    }
  }

  prevStep() {
    if (this.currentStep > 1) {
      this.goToStep(this.currentStep - 1);
    }
  }

  renderFloatingWidget() {
    let widget = document.getElementById('demo-floating-widget');
    if (!widget) {
      widget = document.createElement('div');
      widget.id = 'demo-floating-widget';
      widget.style.cssText = `
        position: fixed;
        bottom: 24px;
        right: 24px;
        width: 380px;
        background: rgba(8, 14, 28, 0.95);
        border: 1px solid #00f0ff;
        border-radius: 16px;
        box-shadow: 0 10px 40px rgba(0,0,0,0.7), 0 0 25px rgba(0, 240, 255, 0.25);
        backdrop-filter: blur(16px);
        padding: 20px;
        z-index: 9990;
        font-family: 'Inter', sans-serif;
        color: #ffffff;
      `;
      document.body.appendChild(widget);
    }

    const step = DEMO_STEPS[this.currentStep - 1];

    widget.innerHTML = `
      <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 12px; border-bottom: 1px solid rgba(0, 240, 255, 0.2); padding-bottom: 10px;">
        <div style="display: flex; align-items: center; gap: 8px;">
          <span style="background: rgba(0, 240, 255, 0.2); color: #00f0ff; border: 1px solid #00f0ff; border-radius: 6px; padding: 2px 8px; font-size: 0.72rem; font-weight: 700;">
            STEP ${this.currentStep}/10
          </span>
          <span style="font-weight: 700; font-size: 0.85rem; color: #ffffff;">Seminar Demo Guide</span>
        </div>
        <button onclick="window.demoTour.closeDemo()" style="background: none; border: none; color: #64748b; font-size: 1.1rem; cursor: pointer;">&times;</button>
      </div>
      
      <h4 style="color: #38bdf8; font-size: 0.95rem; margin-bottom: 6px;">${step.title}</h4>
      <p style="color: #94a3b8; font-size: 0.8rem; line-height: 1.45; margin-bottom: 16px;">${step.desc}</p>
      
      <div style="display: flex; align-items: center; justify-content: space-between; gap: 8px;">
        <button onclick="window.demoTour.prevStep()" class="btn btn-outline btn-sm" ${this.currentStep === 1 ? 'disabled style="opacity: 0.4; cursor: not-allowed;"' : ''}>
          <i class="fas fa-chevron-left"></i> Prev
        </button>
        
        <button onclick="window.demoTour.goToStep(${this.currentStep})" class="btn btn-primary btn-sm" style="flex: 1;">
          <i class="fas fa-play"></i> ${step.actionName}
        </button>
        
        <button onclick="window.demoTour.nextStep()" class="btn btn-outline btn-sm" style="border-color: #00f0ff; color: #00f0ff;">
          Next <i class="fas fa-chevron-right"></i>
        </button>
      </div>
    `;
  }
}

function showConcludingMotto() {
  let modal = document.getElementById('concluding-motto-modal');
  if (!modal) {
    modal = document.createElement('div');
    modal.id = 'concluding-motto-modal';
    modal.style.cssText = `
      position: fixed;
      top: 0; left: 0; right: 0; bottom: 0;
      background: rgba(3, 7, 18, 0.85);
      backdrop-filter: blur(12px);
      z-index: 99999;
      display: flex;
      align-items: center;
      justify-content: center;
      padding: 24px;
    `;
    document.body.appendChild(modal);
  }

  modal.innerHTML = `
    <div style="max-width: 650px; background: #070d1d; border: 2px solid #00f0ff; border-radius: 20px; padding: 40px; text-align: center; box-shadow: 0 0 50px rgba(0, 240, 255, 0.4); animation: pulse-border 3s infinite;">
      <div style="width: 70px; height: 70px; border-radius: 50%; background: rgba(0, 240, 255, 0.15); border: 2px solid #00f0ff; display: inline-flex; align-items: center; justify-content: center; color: #00f0ff; font-size: 2rem; margin-bottom: 20px; box-shadow: 0 0 25px rgba(0, 240, 255, 0.4);">
        <i class="fas fa-atom"></i>
      </div>
      <h2 style="font-size: 1.4rem; color: #ffffff; margin-bottom: 18px; font-weight: 700;">
        Seminar Demo Complete
      </h2>
      <div style="background: rgba(0, 240, 255, 0.06); border: 1px solid rgba(0, 240, 255, 0.3); border-radius: 12px; padding: 24px; margin-bottom: 24px;">
        <p style="font-size: 1.25rem; font-weight: 600; line-height: 1.6; background: linear-gradient(90deg, #38bdf8, #c084fc); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">
          “AI detects patterns. Quantum Machine Learning explores a new approach to detecting complex cyber threats.”
        </p>
      </div>
      <p style="color: #94a3b8; font-size: 0.86rem; margin-bottom: 28px;">
        Q-Sentinel successfully demonstrated end-to-end dataset ingestion, Qiskit 2.5 quantum feature encoding, VQC variational optimization, and instant threat neutralization with explainability.
      </p>
      <button onclick="document.getElementById('concluding-motto-modal').remove()" class="btn btn-primary" style="padding: 12px 30px; font-size: 0.95rem;">
        <i class="fas fa-check"></i> Close Seminar Showcase
      </button>
    </div>
  `;
}

window.demoTour = new SeminarDemoManager();
