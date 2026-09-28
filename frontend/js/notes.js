// Smart Notes Generator Module with Sound FX & Code Enhancements
(function () {
  const topicInput = document.getElementById('notes-topic-input');
  const styleSelect = document.getElementById('notes-style-select');
  const contextInput = document.getElementById('notes-context-input');
  const genBtn = document.getElementById('generate-notes-btn');
  const outputContainer = document.getElementById('notes-output-container');
  const emptyState = document.getElementById('notes-empty-state');
  const notesBody = document.getElementById('notes-markdown-body');
  const copyBtn = document.getElementById('copy-notes-btn');
  const downloadBtn = document.getElementById('download-notes-btn');

  let currentNotesContent = '';

  async function generateNotes() {
    const topic = topicInput ? topicInput.value.trim() : '';
    if (!topic) {
      alert('Please enter a topic or chapter title.');
      return;
    }

    if (window.SoundFX) SoundFX.click();
    const style = styleSelect ? styleSelect.value : 'comprehensive';
    const context = contextInput ? contextInput.value.trim() : null;

    genBtn.disabled = true;
    genBtn.innerHTML = `
      <svg class="animate-spin -ml-1 mr-2 h-4 w-4 text-white inline" fill="none" viewBox="0 0 24 24">
        <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
        <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8H4z"></path>
      </svg>
      Synthesizing High-Retention Notes...
    `;

    try {
      const res = await apiCall('/api/notes/generate', 'POST', {
        topic,
        format_style: style,
        context: context
      });
      currentNotesContent = res.content;

      if (emptyState) emptyState.classList.add('hidden');
      if (outputContainer) outputContainer.classList.remove('hidden');
      if (notesBody) {
        if (window.marked) {
          notesBody.innerHTML = window.marked.parse(res.content);
        } else {
          notesBody.textContent = res.content;
        }
        enhanceCodeBlocks(notesBody);
      }
      if (window.SoundFX) SoundFX.correct();
    } catch (err) {
      alert('Failed to generate notes: ' + err.message);
      if (window.SoundFX) SoundFX.wrong();
    } finally {
      genBtn.disabled = false;
      genBtn.innerHTML = '✨ Generate High-Retention Notes';
    }
  }

  if (genBtn) genBtn.addEventListener('click', generateNotes);

  if (copyBtn) {
    copyBtn.addEventListener('click', () => {
      if (!currentNotesContent) return;
      if (window.SoundFX) SoundFX.click();
      navigator.clipboard.writeText(currentNotesContent).then(() => {
        const orig = copyBtn.innerHTML;
        copyBtn.innerHTML = '✅ Copied!';
        setTimeout(() => { copyBtn.innerHTML = orig; }, 2000);
      });
    });
  }

  if (downloadBtn) {
    downloadBtn.addEventListener('click', () => {
      if (!currentNotesContent) return;
      if (window.SoundFX) SoundFX.click();
      const topic = (topicInput ? topicInput.value.trim() : 'notes').replace(/\s+/g, '_');
      const blob = new Blob([currentNotesContent], { type: 'text/markdown;charset=utf-8' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `${topic}_study_notes.md`;
      a.click();
      URL.revokeObjectURL(url);
    });
  }
})();
