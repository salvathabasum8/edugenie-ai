// Personalized Study Roadmap Module with Interactive Milestones & Progress Tracking
(function () {
  const goalInput = document.getElementById('roadmap-goal-input');
  const durationInput = document.getElementById('roadmap-duration-select');
  const hoursInput = document.getElementById('roadmap-hours-select');
  const genBtn = document.getElementById('generate-roadmap-btn');
  const roadmapViewer = document.getElementById('roadmap-viewer');

  let totalTasks = 0;
  let completedTasks = 0;

  async function generateRoadmap() {
    if (window.SoundFX) SoundFX.click();
    const goal = goalInput ? goalInput.value.trim() : 'Master Deep Learning';
    if (!goal) {
      alert('Please enter your study goal or exam target.');
      return;
    }

    const duration = durationInput ? parseInt(durationInput.value) : 14;
    const hours = hoursInput ? parseInt(hoursInput.value) : 10;

    genBtn.disabled = true;
    genBtn.innerHTML = `
      <svg class="animate-spin -ml-1 mr-2 h-4 w-4 text-white inline" fill="none" viewBox="0 0 24 24">
        <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
        <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8H4z"></path>
      </svg>
      Architecting Milestone Curriculum...
    `;

    try {
      const data = await apiCall('/api/roadmap/generate', 'POST', {
        goal,
        duration_days: duration,
        weekly_hours: hours
      });
      renderRoadmap(data);
      if (window.SoundFX) SoundFX.correct();
    } catch (err) {
      alert('Error creating roadmap: ' + err.message);
      if (window.SoundFX) SoundFX.wrong();
    } finally {
      genBtn.disabled = false;
      genBtn.innerHTML = '🗺️ Generate Personalized Roadmap';
    }
  }

  function updateRoadmapProgress() {
    const pct = totalTasks > 0 ? Math.round((completedTasks / totalTasks) * 100) : 0;
    const progressEl = document.getElementById('roadmap-completion-pct');
    const barEl = document.getElementById('roadmap-completion-bar');
    if (progressEl) progressEl.textContent = `${completedTasks}/${totalTasks} Tasks (${pct}%)`;
    if (barEl) barEl.style.width = `${pct}%`;

    if (pct === 100 && totalTasks > 0) {
      if (window.Confetti) Confetti.burst();
      if (window.SoundFX) SoundFX.celebrate();
    }
  }

  function renderRoadmap(data) {
    if (!roadmapViewer) return;
    roadmapViewer.classList.remove('hidden');

    totalTasks = 0;
    completedTasks = 0;

    document.getElementById('roadmap-title').textContent = data.title || `${data.goal} Learning Plan`;
    document.getElementById('roadmap-meta').textContent = `${data.duration_days} Days Timeline • ~${data.weekly_hours} Hours/Week`;

    const phasesContainer = document.getElementById('roadmap-phases-container');
    if (phasesContainer) {
      phasesContainer.innerHTML = '';
      (data.phases || []).forEach((phase, pIdx) => {
        const pCard = document.createElement('div');
        pCard.className = 'glass-card p-6 mb-6 rounded-2xl border border-slate-700/60 relative overflow-hidden';
        
        pCard.innerHTML = `
          <div class="flex items-center justify-between gap-3 mb-4">
            <div class="flex items-center gap-3">
              <span class="w-9 h-9 rounded-xl bg-gradient-to-tr from-indigo-600 to-purple-600 text-white font-bold text-sm flex items-center justify-center shadow-md">
                ${phase.phase_number || (pIdx + 1)}
              </span>
              <h3 class="text-sm md:text-base font-bold text-white">${phase.phase_name}</h3>
            </div>
            <span class="text-xs font-semibold px-3 py-1 rounded-full bg-indigo-900/60 text-indigo-300 border border-indigo-700/50">
              ${phase.days_range}
            </span>
          </div>

          <div class="mb-4">
            <h5 class="text-xs font-bold uppercase tracking-wider text-slate-400 mb-2">Key Objectives</h5>
            <ul class="space-y-1">
              ${(phase.key_objectives || []).map(obj => `
                <li class="flex items-center gap-2 text-xs text-slate-300">
                  <span class="text-emerald-400 font-bold">✓</span>
                  <span>${obj}</span>
                </li>
              `).join('')}
            </ul>
          </div>

          <div>
            <h5 class="text-xs font-bold uppercase tracking-wider text-slate-400 mb-2.5">Daily Milestones & Checkpoints</h5>
            <div class="grid grid-cols-1 md:grid-cols-2 gap-3 milestones-grid">
              ${(phase.daily_milestones || []).map(m => {
                totalTasks++;
                return `
                  <div class="p-3.5 bg-slate-900/80 rounded-xl border border-slate-800 text-xs transition-all milestone-item hover:border-slate-700">
                    <div class="flex items-center justify-between mb-1.5">
                      <div class="flex items-center gap-2 font-bold text-indigo-300">
                        <input type="checkbox" class="task-checkbox rounded border-slate-700 text-indigo-600 focus:ring-indigo-500 cursor-pointer">
                        <span>Day ${m.day}</span>
                      </div>
                      <span class="text-slate-500 font-normal">⏱️ ${m.estimated_minutes}m</span>
                    </div>
                    <p class="text-slate-200 task-text mb-2 pl-5 leading-relaxed">${m.task}</p>
                    <div class="text-emerald-400 flex items-center gap-1.5 text-[11px] pl-5 border-t border-slate-800/80 pt-1.5">
                      <span class="font-semibold">🎯 Checkpoint:</span>
                      <span class="text-slate-400">${m.checkpoint}</span>
                    </div>
                  </div>
                `;
              }).join('')}
            </div>
          </div>
        `;

        // Checkbox events
        pCard.querySelectorAll('.task-checkbox').forEach(cb => {
          cb.addEventListener('change', (e) => {
            const item = cb.closest('.milestone-item');
            const txt = item.querySelector('.task-text');
            if (cb.checked) {
              if (window.SoundFX) SoundFX.correct();
              item.classList.add('bg-emerald-950/20', 'border-emerald-500/40');
              txt.classList.add('line-through', 'text-slate-400');
              completedTasks++;
            } else {
              if (window.SoundFX) SoundFX.click();
              item.classList.remove('bg-emerald-950/20', 'border-emerald-500/40');
              txt.classList.remove('line-through', 'text-slate-400');
              completedTasks--;
            }
            updateRoadmapProgress();
          });
        });

        phasesContainer.appendChild(pCard);
      });
    }

    // Capstone
    const capstoneEl = document.getElementById('roadmap-capstone');
    if (capstoneEl && data.capstone_challenge) {
      capstoneEl.textContent = data.capstone_challenge;
    }

    // Tips
    const tipsContainer = document.getElementById('roadmap-tips');
    if (tipsContainer && data.expert_tips) {
      tipsContainer.innerHTML = data.expert_tips.map(t => `
        <li class="flex items-start gap-2.5 text-xs text-slate-300">
          <span class="text-amber-400 font-bold">★</span>
          <span>${t}</span>
        </li>
      `).join('');
    }

    updateRoadmapProgress();
  }

  if (genBtn) genBtn.addEventListener('click', generateRoadmap);
})();
