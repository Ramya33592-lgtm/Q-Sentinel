/**
 * Q-SENTINEL: CORE JAVASCRIPT & SOC TELEMETRY CONTROLLER
 */

// Audio Alert Synthesizer using Web Audio API
class SocAudioAlertSystem {
  constructor() {
    this.audioCtx = null;
    this.isMuted = localStorage.getItem('qsentinel_muted') === 'true';
    this.updateUI();
  }

  initContext() {
    if (!this.audioCtx) {
      const AudioContext = window.AudioContext || window.webkitAudioContext;
      if (AudioContext) {
        this.audioCtx = new AudioContext();
      }
    }
  }

  toggleMute() {
    this.isMuted = !this.isMuted;
    localStorage.setItem('qsentinel_muted', this.isMuted);
    this.updateUI();
    if (!this.isMuted) {
      this.playChirp();
    }
  }

  updateUI() {
    const btn = document.getElementById('audioToggleBtn');
    if (btn) {
      btn.innerHTML = this.isMuted 
        ? '<i class="fas fa-volume-mute"></i> Muted' 
        : '<i class="fas fa-volume-up"></i> Sound Active';
      btn.style.color = this.isMuted ? '#64748b' : '#00f0ff';
    }
  }

  playAlarm(severity = 'Critical') {
    if (this.isMuted) return;
    this.initContext();
    if (!this.audioCtx) return;

    if (this.audioCtx.state === 'suspended') {
      this.audioCtx.resume();
    }

    const now = this.audioCtx.currentTime;
    const osc = this.audioCtx.createOscillator();
    const gain = this.audioCtx.createGain();

    osc.type = severity === 'Critical' ? 'sawtooth' : 'sine';
    
    // Siren frequency sweep
    if (severity === 'Critical') {
      osc.frequency.setValueAtTime(880, now);
      osc.frequency.exponentialRampToValueAtTime(440, now + 0.15);
      osc.frequency.exponentialRampToValueAtTime(880, now + 0.3);
      osc.frequency.exponentialRampToValueAtTime(440, now + 0.45);
      
      gain.gain.setValueAtTime(0.25, now);
      gain.gain.exponentialRampToValueAtTime(0.01, now + 0.55);
      
      osc.connect(gain);
      gain.connect(this.audioCtx.destination);
      osc.start(now);
      osc.stop(now + 0.55);
    } else {
      osc.frequency.setValueAtTime(550, now);
      osc.frequency.exponentialRampToValueAtTime(750, now + 0.2);
      
      gain.gain.setValueAtTime(0.18, now);
      gain.gain.exponentialRampToValueAtTime(0.01, now + 0.3);
      
      osc.connect(gain);
      gain.connect(this.audioCtx.destination);
      osc.start(now);
      osc.stop(now + 0.3);
    }
  }

  playChirp() {
    if (this.isMuted) return;
    this.initContext();
    if (!this.audioCtx) return;
    
    const now = this.audioCtx.currentTime;
    const osc = this.audioCtx.createOscillator();
    const gain = this.audioCtx.createGain();
    
    osc.type = 'sine';
    osc.frequency.setValueAtTime(1200, now);
    osc.frequency.exponentialRampToValueAtTime(1800, now + 0.08);
    
    gain.gain.setValueAtTime(0.12, now);
    gain.gain.exponentialRampToValueAtTime(0.001, now + 0.08);
    
    osc.connect(gain);
    gain.connect(this.audioCtx.destination);
    osc.start(now);
    osc.stop(now + 0.08);
  }
}

window.socAudio = new SocAudioAlertSystem();

// Toast Notifications
function showToast(message, type = 'info', duration = 4500) {
  let container = document.getElementById('toast-container');
  if (!container) {
    container = document.createElement('div');
    container.id = 'toast-container';
    container.style.cssText = `
      position: fixed;
      top: 24px;
      right: 24px;
      z-index: 9999;
      display: flex;
      flex-direction: column;
      gap: 12px;
      pointer-events: none;
    `;
    document.body.appendChild(container);
  }

  const toast = document.createElement('div');
  const colors = {
    info: { border: '#00f0ff', bg: 'rgba(10, 20, 38, 0.95)', icon: 'fa-info-circle', text: '#38bdf8' },
    success: { border: '#10b981', bg: 'rgba(6, 26, 20, 0.95)', icon: 'fa-check-circle', text: '#34d399' },
    warning: { border: '#f59e0b', bg: 'rgba(30, 20, 8, 0.95)', icon: 'fa-exclamation-triangle', text: '#fbbf24' },
    danger: { border: '#ef4444', bg: 'rgba(35, 10, 15, 0.95)', icon: 'fa-shield-virus', text: '#f87171' }
  };
  const c = colors[type] || colors.info;

  toast.style.cssText = `
    min-width: 300px;
    max-width: 420px;
    padding: 14px 18px;
    background: ${c.bg};
    border: 1px solid ${c.border};
    border-radius: 10px;
    color: #ffffff;
    box-shadow: 0 10px 30px rgba(0,0,0,0.6), 0 0 15px ${c.border}44;
    display: flex;
    align-items: center;
    gap: 12px;
    font-size: 0.86rem;
    backdrop-filter: blur(12px);
    pointer-events: auto;
    animation: slideIn 0.25s ease-out;
    font-family: 'Inter', sans-serif;
  `;

  toast.innerHTML = `
    <i class="fas ${c.icon}" style="color: ${c.text}; font-size: 1.2rem;"></i>
    <div style="flex: 1; line-height: 1.4;">${message}</div>
    <button style="background: none; border: none; color: #64748b; cursor: pointer; font-size: 1rem;" onclick="this.parentElement.remove()">&times;</button>
  `;

  container.appendChild(toast);
  setTimeout(() => {
    toast.style.opacity = '0';
    toast.style.transform = 'translateY(-10px)';
    toast.style.transition = 'all 0.3s ease';
    setTimeout(() => toast.remove(), 300);
  }, duration);
}

// Chart.js Cyber Palette Configurator
const CyberChartDefaults = {
  font: { family: "'Inter', sans-serif", size: 11 },
  color: '#94a3b8',
  borderColor: 'rgba(56, 189, 248, 0.1)',
  grid: { color: 'rgba(255, 255, 255, 0.04)', tickColor: 'transparent' }
};

// Global API Helper
async function apiCall(endpoint, method = 'GET', body = null) {
  const options = {
    method,
    headers: {}
  };
  if (body && !(body instanceof FormData)) {
    options.headers['Content-Type'] = 'application/json';
    options.body = JSON.stringify(body);
  } else if (body instanceof FormData) {
    options.body = body;
  }

  try {
    const res = await fetch(endpoint, options);
    const data = await res.json();
    return data;
  } catch (err) {
    console.error(`API Error on ${endpoint}:`, err);
    throw err;
  }
}

// Alert Resolution Handler
async function resolveAlert(alertId, newStatus = 'Resolved') {
  try {
    const res = await apiCall('/api/alerts/status', 'POST', { alert_id: alertId, status: newStatus });
    if (res.success) {
      showToast(res.message, 'success');
      const badge = document.getElementById(`alert-status-${alertId}`);
      if (badge) {
        badge.className = 'badge badge-emerald';
        badge.textContent = newStatus;
      }
    }
  } catch (err) {
    showToast('Failed to update alert status', 'danger');
  }
}
