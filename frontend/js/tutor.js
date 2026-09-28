// AI Tutor Module with Sound FX, Code Copying & Session Clearing
(function () {
  const chatMessages = document.getElementById('chat-messages');
  const chatInput = document.getElementById('chat-input');
  const sendBtn = document.getElementById('send-chat-btn');
  const personaSelect = document.getElementById('persona-select');
  const contextInput = document.getElementById('chat-context');
  const clearChatBtn = document.getElementById('clear-chat-btn');
  const exportChatBtn = document.getElementById('export-chat-btn');

  let currentChatTurns = [];

  function renderMessage(role, text, isLive = false, apiError = null) {
    if (!chatMessages) return;

    currentChatTurns.push({ role, text, isLive, timestamp: new Date().toLocaleTimeString() });

    const isUser = role === 'user';
    const msgDiv = document.createElement('div');
    msgDiv.className = `flex ${isUser ? 'justify-end' : 'justify-start'} mb-4 animate-fade-in`;

    const bubble = document.createElement('div');
    bubble.className = `max-w-[85%] rounded-2xl p-4 shadow-lg ${
      isUser
        ? 'bg-gradient-to-r from-indigo-600 to-indigo-700 text-white rounded-br-none border border-indigo-500/30'
        : 'glass-panel text-slate-100 rounded-bl-none border border-slate-700/60'
    }`;

    // Header info
    const header = document.createElement('div');
    header.className = 'flex items-center justify-between gap-3 text-xs mb-2 opacity-85';
    
    let badgeHtml = '';
    if (!isUser) {
      if (isLive) {
        badgeHtml = '<span class="text-[10px] px-2 py-0.5 rounded-full bg-emerald-500/20 text-emerald-300 border border-emerald-500/35 font-semibold">Gemini Live</span>';
      } else {
        badgeHtml = '<span class="text-[10px] px-2 py-0.5 rounded-full bg-indigo-500/20 text-indigo-300 border border-indigo-500/35 font-semibold">Educational Engine</span>';
      }
    }

    header.innerHTML = `
      <div class="flex items-center gap-2">
        <span class="font-semibold flex items-center gap-1.5">
          ${isUser ? '👤 Student' : '✨ EduGenie AI'}
        </span>
        ${badgeHtml}
      </div>
      ${!isUser ? `
        <button class="hover:text-indigo-300 tts-btn px-2 py-1 rounded bg-slate-800/60 hover:bg-slate-700/60 border border-slate-700/50 transition text-xs flex items-center gap-1" title="Read Aloud">
          🔊 Listen
        </button>
      ` : ''}
    `;

    const contentDiv = document.createElement('div');
    contentDiv.className = isUser ? 'text-xs md:text-sm font-normal' : 'text-xs md:text-sm prose-dark';

    if (isUser) {
      contentDiv.textContent = text;
    } else {
      if (window.marked) {
        contentDiv.innerHTML = window.marked.parse(text);
      } else {
        contentDiv.innerHTML = text.replace(/\n/g, '<br/>');
      }
    }

    bubble.appendChild(header);
    bubble.appendChild(contentDiv);
    msgDiv.appendChild(bubble);
    chatMessages.appendChild(msgDiv);

    // Enhance code blocks with copy buttons
    if (!isUser) {
      enhanceCodeBlocks(contentDiv);
    }

    // TTS click handler
    if (!isUser) {
      const ttsBtn = header.querySelector('.tts-btn');
      if (ttsBtn) {
        ttsBtn.addEventListener('click', () => {
          if (window.SoundFX) SoundFX.click();
          speakText(text, ttsBtn);
        });
      }
    }

    chatMessages.scrollTop = chatMessages.scrollHeight;
  }

  async function handleSend() {
    if (!chatInput) return;
    const msg = chatInput.value.trim();
    if (!msg) return;

    if (window.SoundFX) SoundFX.click();
    chatInput.value = '';
    renderMessage('user', msg);

    // Show typing loader
    const loaderDiv = document.createElement('div');
    loaderDiv.id = 'chat-loader';
    loaderDiv.className = 'flex justify-start mb-4';
    loaderDiv.innerHTML = `
      <div class="glass-panel text-slate-300 rounded-2xl rounded-bl-none p-4 flex items-center gap-2">
        <span class="w-2 h-2 rounded-full bg-indigo-400 animate-bounce"></span>
        <span class="w-2 h-2 rounded-full bg-indigo-400 animate-bounce" style="animation-delay: 0.2s"></span>
        <span class="w-2 h-2 rounded-full bg-indigo-400 animate-bounce" style="animation-delay: 0.4s"></span>
        <span class="text-xs text-slate-400 ml-1.5 font-medium">EduGenie is reasoning...</span>
      </div>
    `;
    chatMessages.appendChild(loaderDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;

    const persona = personaSelect ? personaSelect.value : 'socratic';
    const context = contextInput ? contextInput.value.trim() : null;

    try {
      const res = await apiCall('/api/tutor/chat', 'POST', {
        session_id: state.activeSessionId,
        message: msg,
        persona: persona,
        context: context
      });
      loaderDiv.remove();
      renderMessage('assistant', res.response, res.live_gemini, res.api_error);
      if (window.SoundFX) SoundFX.correct();
    } catch (err) {
      loaderDiv.remove();
      renderMessage('assistant', `⚠️ Error communicating with EduGenie: ${err.message}. Please verify your API key or network.`);
      if (window.SoundFX) SoundFX.wrong();
    }
  }

  // Clear Chat History
  async function clearChat() {
    if (!confirm('Are you sure you want to clear this conversation history?')) return;
    if (window.SoundFX) SoundFX.click();
    try {
      await apiCall('/api/tutor/clear', 'POST', { session_id: state.activeSessionId });
      currentChatTurns = [];
      chatMessages.innerHTML = `
        <div class="flex justify-start mb-4">
          <div class="glass-panel text-slate-100 rounded-2xl rounded-bl-none p-5 shadow-md max-w-[85%] border border-slate-700/50">
            <div class="flex items-center gap-2 text-xs text-indigo-400 font-semibold mb-2">
              <span>✨</span> EduGenie Assistant
            </div>
            <div class="text-xs md:text-sm prose-dark">
              <p>Conversation history cleared! How can I assist you with your studies today?</p>
            </div>
          </div>
        </div>
      `;
    } catch (e) {
      alert('Failed to clear chat: ' + e.message);
    }
  }

  // Export Chat Transcript
  function exportTranscript() {
    if (currentChatTurns.length === 0) {
      alert('No messages to export yet.');
      return;
    }
    if (window.SoundFX) SoundFX.click();
    let md = `# 🎓 EduGenie AI: Study Session Transcript\n`;
    md += `*Exported on ${new Date().toLocaleString()}*\n\n---\n\n`;
    currentChatTurns.forEach(t => {
      md += `### ${t.role === 'user' ? '👤 Student' : '✨ EduGenie AI'} (${t.timestamp})\n`;
      md += `${t.text}\n\n---\n\n`;
    });

    const blob = new Blob([md], { type: 'text/markdown;charset=utf-8' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `edugenie_study_session_${Date.now()}.md`;
    a.click();
    URL.revokeObjectURL(url);
  }

  if (sendBtn) sendBtn.addEventListener('click', handleSend);
  if (chatInput) {
    chatInput.addEventListener('keydown', (e) => {
      if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        handleSend();
      }
    });
  }
  if (clearChatBtn) clearChatBtn.addEventListener('click', clearChat);
  if (exportChatBtn) exportChatBtn.addEventListener('click', exportChatBtn);

  // Quick Prompt Chips
  document.querySelectorAll('.prompt-chip').forEach(chip => {
    chip.addEventListener('click', () => {
      if (chatInput) {
        if (window.SoundFX) SoundFX.click();
        chatInput.value = chip.getAttribute('data-prompt') || chip.innerText.trim();
        handleSend();
      }
    });
  });
})();
