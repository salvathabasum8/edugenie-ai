// EduGenie AI Global Application Logic
const state = {
  currentTab: 'tutor',
  hasApiKey: false,
  geminiModel: 'gemini-2.5-flash',
  activeSessionId: localStorage.getItem('edugenie_session_id') || ('session_' + Math.random().toString(36).substr(2, 9)),
  bloomsLevels: {},
  tutorPersonas: {}
};

localStorage.setItem('edugenie_session_id', state.activeSessionId);

// API Fetch Wrapper
async function apiCall(endpoint, method = 'GET', body = null) {
  const options = {
    method,
    headers: { 'Content-Type': 'application/json' }
  };
  if (body) {
    options.body = JSON.stringify(body);
  }
  try {
    const res = await fetch(endpoint, options);
    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.error || `HTTP ${res.status}`);
    }
    return await res.json();
  } catch (err) {
    console.error(`API Error on ${endpoint}:`, err);
    throw err;
  }
}

// Check Backend Status
async function checkStatus() {
  try {
    const data = await apiCall('/api/status');
    state.hasApiKey = data.has_gemini_api_key;
    state.geminiModel = data.gemini_model;
    state.bloomsLevels = data.blooms_levels || {};
    state.tutorPersonas = data.tutor_personas || {};

    const statusBadge = document.getElementById('status-badge');
    if (statusBadge) {
      if (state.hasApiKey) {
        statusBadge.innerHTML = `
          <span class="inline-flex items-center px-3 py-1 rounded-full text-xs font-semibold bg-emerald-500/20 text-emerald-300 border border-emerald-500/35 shadow-sm shadow-emerald-500/10 cursor-pointer" onclick="openKeyModal()">
            <span class="w-2 h-2 mr-2 rounded-full bg-emerald-400 animate-pulse"></span>
            Gemini Live: ${state.geminiModel}
          </span>
        `;
      } else {
        statusBadge.innerHTML = `
          <span class="inline-flex items-center px-3 py-1 rounded-full text-xs font-semibold bg-amber-500/20 text-amber-300 border border-amber-500/35 shadow-sm shadow-amber-500/10 cursor-pointer" onclick="openKeyModal()">
            <span class="w-2 h-2 mr-2 rounded-full bg-amber-400"></span>
            Educational Engine (Click to Add Key)
          </span>
        `;
      }
    }
  } catch (e) {
    console.warn('Backend status check failed:', e);
  }
}

// Tab Switching with Sound FX
function switchTab(tabName) {
  if (window.SoundFX) SoundFX.click();
  state.currentTab = tabName;
  document.querySelectorAll('.tab-content').forEach(el => el.classList.add('hidden'));
  document.querySelectorAll('.nav-tab').forEach(el => el.classList.remove('active'));

  const targetTab = document.getElementById(`tab-${tabName}`);
  const targetNav = document.getElementById(`nav-${tabName}`);
  if (targetTab) targetTab.classList.remove('hidden');
  if (targetNav) targetNav.classList.add('active');

  // Trigger sub-module updates
  if (tabName === 'analytics' && window.loadAnalytics) {
    window.loadAnalytics();
  } else if (tabName === 'flashcards' && window.loadDecks) {
    window.loadDecks();
  }
}

// Modal handling
function openKeyModal() {
  if (window.SoundFX) SoundFX.click();
  const modal = document.getElementById('key-modal');
  if (modal) modal.classList.remove('hidden');
}

function closeKeyModal() {
  if (window.SoundFX) SoundFX.click();
  const modal = document.getElementById('key-modal');
  if (modal) modal.classList.add('hidden');
}

async function saveApiKey() {
  const input = document.getElementById('api-key-input');
  if (!input) return;
  const key = input.value.trim();
  try {
    const res = await apiCall('/api/config/key', 'POST', { api_key: key });
    closeKeyModal();
    checkStatus();
    if (window.SoundFX) SoundFX.correct();
    alert('API Key updated successfully! ' + (res.has_key ? 'Live Gemini mode enabled.' : 'Set to demo mode.'));
  } catch (e) {
    alert('Failed to save API key: ' + e.message);
  }
}

// Speech Synthesis Helper
let activeSpeech = null;
function speakText(text, buttonElement = null) {
  if (!('speechSynthesis' in window)) {
    alert('Text-to-speech is not supported in this browser.');
    return;
  }

  // If already speaking, cancel
  if (window.speechSynthesis.speaking) {
    window.speechSynthesis.cancel();
    if (buttonElement) buttonElement.innerHTML = '🔊 Listen';
    return;
  }

  const clean = text.replace(/[*_#`~>\[\]\(\)]/g, '').replace(/```[\s\S]*?```/g, 'Code block omitted.');
  const utterance = new SpeechSynthesisUtterance(clean);
  utterance.rate = 1.05;
  utterance.pitch = 1.0;

  if (buttonElement) {
    buttonElement.innerHTML = `
      <span class="speaking-wave mr-1">
        <span class="wave-bar"></span>
        <span class="wave-bar"></span>
        <span class="wave-bar"></span>
      </span>
      Stop
    `;
  }

  utterance.onend = () => {
    if (buttonElement) buttonElement.innerHTML = '🔊 Listen';
  };
  utterance.onerror = () => {
    if (buttonElement) buttonElement.innerHTML = '🔊 Listen';
  };

  window.speechSynthesis.speak(utterance);
}

// Process Code Blocks to add Copy Buttons & Language Headers
function enhanceCodeBlocks(container) {
  if (!container) return;
  const preElements = container.querySelectorAll('pre');
  preElements.forEach(pre => {
    if (pre.parentElement && pre.parentElement.classList.contains('code-block-wrapper')) return;

    const code = pre.querySelector('code');
    const textToCopy = code ? code.innerText : pre.innerText;
    
    // Detect language class if any
    let lang = 'CODE';
    if (code && code.className) {
      const match = code.className.match(/language-([a-zA-Z0-9]+)/);
      if (match) lang = match[1].toUpperCase();
    }

    const wrapper = document.createElement('div');
    wrapper.className = 'code-block-wrapper';

    const header = document.createElement('div');
    header.className = 'code-block-header';
    header.innerHTML = `
      <span>⚡ ${lang}</span>
      <button class="code-copy-btn">📋 Copy</button>
    `;

    const copyBtn = header.querySelector('.code-copy-btn');
    copyBtn.addEventListener('click', () => {
      navigator.clipboard.writeText(textToCopy).then(() => {
        copyBtn.innerText = '✅ Copied!';
        if (window.SoundFX) SoundFX.click();
        setTimeout(() => { copyBtn.innerText = '📋 Copy'; }, 2000);
      });
    });

    pre.parentNode.insertBefore(wrapper, pre);
    wrapper.appendChild(header);
    wrapper.appendChild(pre);
  });
}

// Document Ready Initialization
document.addEventListener('DOMContentLoaded', () => {
  checkStatus();
  
  // Set up nav event listeners
  document.querySelectorAll('.nav-tab').forEach(btn => {
    btn.addEventListener('click', () => {
      const tab = btn.getAttribute('data-tab');
      if (tab) switchTab(tab);
    });
  });

  // Sound FX toggle button
  const soundToggleBtn = document.getElementById('sound-toggle-btn');
  if (soundToggleBtn) {
    soundToggleBtn.addEventListener('click', () => {
      SoundFX.toggle();
    });
  }

  // Modal close on backdrop click
  const modal = document.getElementById('key-modal');
  if (modal) {
    modal.addEventListener('click', (e) => {
      if (e.target === modal) closeKeyModal();
    });
  }
});
