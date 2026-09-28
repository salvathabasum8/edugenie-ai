// EduGenie Web Audio API Sound Synthesizer (Zero External Dependencies)
const SoundFX = (function () {
  let audioCtx = null;
  let enabled = localStorage.getItem('edugenie_sound_enabled') !== 'false';

  function getContext() {
    if (!audioCtx) {
      const AudioContext = window.AudioContext || window.webkitAudioContext;
      if (AudioContext) {
        audioCtx = new AudioContext();
      }
    }
    if (audioCtx && audioCtx.state === 'suspended') {
      audioCtx.resume();
    }
    return audioCtx;
  }

  return {
    isEnabled: () => enabled,
    
    toggle: () => {
      enabled = !enabled;
      localStorage.setItem('edugenie_sound_enabled', enabled ? 'true' : 'false');
      SoundFX.updateIcon();
      if (enabled) SoundFX.click();
      return enabled;
    },

    updateIcon: () => {
      const btn = document.getElementById('sound-toggle-btn');
      if (btn) {
        btn.innerHTML = enabled ? '🔊' : '🔇';
        btn.title = enabled ? 'Sound Effects Enabled (Click to Mute)' : 'Sound Effects Muted (Click to Enable)';
      }
    },

    // Short soft click
    click: () => {
      if (!enabled) return;
      const ctx = getContext();
      if (!ctx) return;
      try {
        const osc = ctx.createOscillator();
        const gain = ctx.createGain();
        osc.type = 'sine';
        osc.frequency.setValueAtTime(600, ctx.currentTime);
        osc.frequency.exponentialRampToValueAtTime(150, ctx.currentTime + 0.04);
        gain.gain.setValueAtTime(0.12, ctx.currentTime);
        gain.gain.exponentialRampToValueAtTime(0.001, ctx.currentTime + 0.04);
        osc.connect(gain);
        gain.connect(ctx.destination);
        osc.start();
        osc.stop(ctx.currentTime + 0.05);
      } catch (e) {}
    },

    // Card flip tactile sound
    flip: () => {
      if (!enabled) return;
      const ctx = getContext();
      if (!ctx) return;
      try {
        const osc = ctx.createOscillator();
        const gain = ctx.createGain();
        osc.type = 'triangle';
        osc.frequency.setValueAtTime(300, ctx.currentTime);
        osc.frequency.exponentialRampToValueAtTime(500, ctx.currentTime + 0.06);
        gain.gain.setValueAtTime(0.08, ctx.currentTime);
        gain.gain.exponentialRampToValueAtTime(0.001, ctx.currentTime + 0.06);
        osc.connect(gain);
        gain.connect(ctx.destination);
        osc.start();
        osc.stop(ctx.currentTime + 0.07);
      } catch (e) {}
    },

    // Happy chime for correct answer
    correct: () => {
      if (!enabled) return;
      const ctx = getContext();
      if (!ctx) return;
      try {
        [523.25, 659.25, 783.99].forEach((freq, i) => {
          const osc = ctx.createOscillator();
          const gain = ctx.createGain();
          osc.type = 'sine';
          osc.frequency.setValueAtTime(freq, ctx.currentTime + i * 0.08);
          gain.gain.setValueAtTime(0.1, ctx.currentTime + i * 0.08);
          gain.gain.exponentialRampToValueAtTime(0.001, ctx.currentTime + i * 0.08 + 0.3);
          osc.connect(gain);
          gain.connect(ctx.destination);
          osc.start(ctx.currentTime + i * 0.08);
          osc.stop(ctx.currentTime + i * 0.08 + 0.35);
        });
      } catch (e) {}
    },

    // Subtle low note for review/miss
    wrong: () => {
      if (!enabled) return;
      const ctx = getContext();
      if (!ctx) return;
      try {
        const osc = ctx.createOscillator();
        const gain = ctx.createGain();
        osc.type = 'sawtooth';
        osc.frequency.setValueAtTime(220, ctx.currentTime);
        osc.frequency.exponentialRampToValueAtTime(140, ctx.currentTime + 0.15);
        gain.gain.setValueAtTime(0.08, ctx.currentTime);
        gain.gain.exponentialRampToValueAtTime(0.001, ctx.currentTime + 0.15);
        osc.connect(gain);
        gain.connect(ctx.destination);
        osc.start();
        osc.stop(ctx.currentTime + 0.16);
      } catch (e) {}
    },

    // Fanfare for quiz completion
    celebrate: () => {
      if (!enabled) return;
      const ctx = getContext();
      if (!ctx) return;
      try {
        const notes = [523.25, 659.25, 783.99, 1046.50];
        notes.forEach((freq, idx) => {
          const osc = ctx.createOscillator();
          const gain = ctx.createGain();
          osc.type = 'triangle';
          osc.frequency.setValueAtTime(freq, ctx.currentTime + idx * 0.12);
          gain.gain.setValueAtTime(0.15, ctx.currentTime + idx * 0.12);
          gain.gain.exponentialRampToValueAtTime(0.001, ctx.currentTime + idx * 0.12 + 0.45);
          osc.connect(gain);
          gain.connect(ctx.destination);
          osc.start(ctx.currentTime + idx * 0.12);
          osc.stop(ctx.currentTime + idx * 0.12 + 0.5);
        });
      } catch (e) {}
    }
  };
})();

document.addEventListener('DOMContentLoaded', () => {
  SoundFX.updateIcon();
});
