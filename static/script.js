/**
 * Q-SENTINEL: CYBERSECURITY DASHBOARD CONTROLLER
 */

// Web Audio Alert Synthesizer
function playAlarmSound(severity = 'Critical') {
  try {
    const AudioContext = window.AudioContext || window.webkitAudioContext;
    if (!AudioContext) return;
    const ctx = new AudioContext();
    const now = ctx.currentTime;
    const osc = ctx.createOscillator();
    const gain = ctx.createGain();

    osc.type = severity === 'Critical' ? 'sawtooth' : 'sine';

    if (severity === 'Critical') {
      osc.frequency.setValueAtTime(880, now);
      osc.frequency.exponentialRampToValueAtTime(440, now + 0.15);
      osc.frequency.exponentialRampToValueAtTime(880, now + 0.3);
      osc.frequency.exponentialRampToValueAtTime(440, now + 0.45);

      gain.gain.setValueAtTime(0.25, now);
      gain.gain.exponentialRampToValueAtTime(0.01, now + 0.55);

      osc.connect(gain);
      gain.connect(ctx.destination);
      osc.start(now);
      osc.stop(now + 0.55);
    } else {
      osc.frequency.setValueAtTime(550, now);
      osc.frequency.exponentialRampToValueAtTime(750, now + 0.2);

      gain.gain.setValueAtTime(0.18, now);
      gain.gain.exponentialRampToValueAtTime(0.01, now + 0.3);

      osc.connect(gain);
      gain.connect(ctx.destination);
      osc.start(now);
      osc.stop(now + 0.3);
    }
  } catch (e) {
    console.warn("Audio note:", e);
  }
}

// Global API Helper
async function apiPost(url, data = {}) {
  const isFormData = data instanceof FormData;
  const options = {
    method: 'POST',
    body: isFormData ? data : JSON.stringify(data)
  };
  if (!isFormData) {
    options.headers = { 'Content-Type': 'application/json' };
  }
  const res = await fetch(url, options);
  return await res.json();
}

// Preset Attack Simulation Injector
const ATTACK_PRESETS = {
  ddos: {
    source_ip: "185.220.101.44",
    destination_port: 80,
    flow_duration: 480.5,
    flow_packets_per_sec: 8750.0,
    flow_bytes_per_sec: 3200000.0,
    total_fwd_packets: 420,
    total_bwd_packets: 1,
    syn_flag_count: 280,
    ack_flag_count: 0,
    packet_length_mean: 64.0,
    packet_length_std: 12.0,
    protocol_type: "TCP"
  },
  portscan: {
    source_ip: "45.143.221.8",
    destination_port: 445,
    flow_duration: 12.4,
    flow_packets_per_sec: 2400.0,
    flow_bytes_per_sec: 1200.0,
    total_fwd_packets: 2,
    total_bwd_packets: 0,
    syn_flag_count: 1,
    ack_flag_count: 0,
    packet_length_mean: 44.0,
    packet_length_std: 0.0,
    protocol_type: "TCP"
  },
  bruteforce: {
    source_ip: "194.26.29.112",
    destination_port: 22,
    flow_duration: 7200.0,
    flow_packets_per_sec: 75.0,
    flow_bytes_per_sec: 24500.0,
    total_fwd_packets: 54,
    total_bwd_packets: 48,
    syn_flag_count: 4,
    ack_flag_count: 52,
    packet_length_mean: 140.0,
    packet_length_std: 38.0,
    protocol_type: "TCP"
  },
  botnet: {
    source_ip: "91.240.118.17",
    destination_port: 6667,
    flow_duration: 42000.0,
    flow_packets_per_sec: 12.0,
    flow_bytes_per_sec: 4800.0,
    total_fwd_packets: 18,
    total_bwd_packets: 14,
    syn_flag_count: 1,
    ack_flag_count: 12,
    packet_length_mean: 320.0,
    packet_length_std: 145.0,
    protocol_type: "TCP"
  },
  normal: {
    source_ip: "10.0.4.52",
    destination_port: 443,
    flow_duration: 18500.0,
    flow_packets_per_sec: 85.0,
    flow_bytes_per_sec: 68000.0,
    total_fwd_packets: 16,
    total_bwd_packets: 22,
    syn_flag_count: 1,
    ack_flag_count: 21,
    packet_length_mean: 820.0,
    packet_length_std: 180.0,
    protocol_type: "TCP"
  }
};

function loadPreset(key) {
  const p = ATTACK_PRESETS[key];
  if (!p) return;
  for (const [k, v] of Object.entries(p)) {
    const el = document.getElementById(k);
    if (el) el.value = v;
  }
}

// Run Detection Execution
async function runDetection() {
  const btn = document.getElementById('runDetectionBtn');
  const originalText = btn.innerHTML;
  btn.innerHTML = 'Evaluating Quantum Circuit...';
  btn.disabled = true;

  const payload = {
    source_ip: document.getElementById('source_ip').value,
    features: {
      flow_duration: parseFloat(document.getElementById('flow_duration').value),
      flow_packets_per_sec: parseFloat(document.getElementById('flow_packets_per_sec').value),
      flow_bytes_per_sec: parseFloat(document.getElementById('flow_bytes_per_sec').value),
      total_fwd_packets: parseInt(document.getElementById('total_fwd_packets').value),
      total_bwd_packets: parseInt(document.getElementById('total_bwd_packets').value),
      syn_flag_count: parseInt(document.getElementById('syn_flag_count').value),
      ack_flag_count: parseInt(document.getElementById('ack_flag_count').value),
      urg_flag_count: 0,
      packet_length_mean: parseFloat(document.getElementById('packet_length_mean').value),
      packet_length_std: parseFloat(document.getElementById('packet_length_std').value),
      destination_port: parseInt(document.getElementById('destination_port').value),
      protocol_type: document.getElementById('protocol_type').value
    }
  };

  try {
    const res = await apiPost('/api/predict', payload);
    if (res.success) {
      document.getElementById('detectionPlaceholder').style.display = 'none';
      document.getElementById('detectionResults').style.display = 'block';

      const isAttack = res.is_attack;
      const verdictEl = document.getElementById('verdictText');
      verdictEl.textContent = isAttack ? `ATTACK DETECTED: ${res.attack_type}` : 'NORMAL BENIGN TRAFFIC';
      verdictEl.style.color = isAttack ? 'var(--crimson)' : 'var(--emerald)';

      const threatBadge = document.getElementById('threatBadge');
      threatBadge.textContent = `THREAT LEVEL: ${res.threat_level.toUpperCase()}`;
      threatBadge.className = isAttack 
        ? (res.threat_level === 'Critical' ? 'badge badge-crimson' : 'badge badge-amber')
        : 'badge badge-emerald';

      // Quantum VQC details
      const q = res.quantum_prediction;
      document.getElementById('qResultBadge').textContent = q.is_attack ? 'MALICIOUS' : 'BENIGN';
      document.getElementById('qResultBadge').className = q.is_attack ? 'badge badge-crimson' : 'badge badge-emerald';
      document.getElementById('qConfidenceVal').textContent = `${(q.confidence * 100).toFixed(1)}%`;
      document.getElementById('qExpectationVal').textContent = `<Z_0> = ${q.expectation_value_z0}`;

      // Classical details
      const c = res.classical_prediction;
      document.getElementById('cResultBadge').textContent = c.is_attack ? 'MALICIOUS' : 'BENIGN';
      document.getElementById('cResultBadge').className = c.is_attack ? 'badge badge-crimson' : 'badge badge-emerald';
      document.getElementById('cConfidenceVal').textContent = `${(c.confidence * 100).toFixed(1)}%`;
      document.getElementById('cAttackClassVal').textContent = `Class: ${c.attack_type}`;

      // XAI Explanations
      const expList = document.getElementById('xaiList');
      expList.innerHTML = '';
      (res.explanation_list || []).forEach(text => {
        const li = document.createElement('li');
        li.style.cssText = 'display: flex; gap: 8px; align-items: flex-start; margin-bottom: 6px;';
        li.innerHTML = `<span style="color: ${isAttack ? '#ef4444' : '#10b981'}; font-weight: bold;">▶</span> <span>${text}</span>`;
        expList.appendChild(li);
      });

      // Red Banner
      const redBanner = document.getElementById('redAlertBanner');
      if (isAttack) {
        redBanner.style.display = 'flex';
        document.getElementById('alertTitle').textContent = `Malicious Incursion Detected: ${res.attack_type}`;
        document.getElementById('alertSummary').textContent = res.explanation;
        playAlarmSound(res.threat_level);
      } else {
        redBanner.style.display = 'none';
      }
    } else {
      alert('Prediction Error: ' + res.error);
    }
  } catch (err) {
    alert('Failed to run detection: ' + err.message);
  } finally {
    btn.innerHTML = originalText;
    btn.disabled = false;
  }
}

// Upload CSV Dataset
async function handleDatasetUpload(input) {
  if (!input.files.length) return;
  const formData = new FormData();
  formData.append('dataset', input.files[0]);

  try {
    const res = await apiPost('/api/dataset/upload', formData);
    if (res.success) {
      alert(res.message);
      window.location.reload();
    } else {
      alert('Upload failed: ' + res.error);
    }
  } catch (err) {
    alert('Upload error: ' + err.message);
  }
}

// Load Default Demo Dataset
async function loadDemoDataset() {
  try {
    const res = await apiPost('/api/dataset/load-sample');
    if (res.success) {
      alert(res.message);
      window.location.reload();
    } else {
      alert('Error: ' + res.error);
    }
  } catch (err) {
    alert('Failed to load sample dataset: ' + err.message);
  }
}

// Train Quantum VQC
async function trainQuantumVqc() {
  const btn = document.getElementById('trainVqcBtn');
  btn.innerHTML = 'Optimizing Qubits...';
  btn.disabled = true;

  try {
    const res = await apiPost('/api/train/quantum', { maxiter: 25 });
    if (res.success) {
      alert(`Quantum Model Retrained! Accuracy: ${(res.metrics.accuracy * 100).toFixed(1)}%`);
      window.location.reload();
    } else {
      alert('Error: ' + res.error);
    }
  } catch (err) {
    alert('Training error: ' + err.message);
  } finally {
    btn.innerHTML = 'Train Quantum VQC';
    btn.disabled = false;
  }
}
