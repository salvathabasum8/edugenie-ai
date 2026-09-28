// Learning Analytics & Cognitive Mastery Module with Badges & Dynamic Visualizations
(function () {
  async function loadAnalytics() {
    try {
      const data = await apiCall('/api/analytics');

      // Metric cards
      const qEl = document.getElementById('stat-total-quizzes');
      if (qEl) qEl.textContent = data.total_quizzes || 0;

      const sEl = document.getElementById('stat-avg-score');
      if (sEl) sEl.textContent = `${data.average_score || 0}%`;

      const strEl = document.getElementById('stat-streak');
      if (strEl) strEl.textContent = `${data.study_streak_days || 0} Days 🔥`;

      const cEl = document.getElementById('stat-cards-count');
      if (cEl) cEl.textContent = data.total_cards || 0;

      // Bloom's Mastery Bars
      const bloomContainer = document.getElementById('bloom-mastery-grid');
      if (bloomContainer && data.bloom_details) {
        bloomContainer.innerHTML = '';
        data.bloom_details.forEach(item => {
          const card = document.createElement('div');
          card.className = 'glass-card p-4 rounded-xl border border-slate-700/60 shadow-sm';
          card.innerHTML = `
            <div class="flex items-center justify-between text-xs font-semibold mb-2">
              <span class="flex items-center gap-1.5 font-bold" style="color: ${item.color}">
                <span class="w-2.5 h-2.5 rounded-full shadow-sm" style="background-color: ${item.color}"></span>
                ${item.name}
              </span>
              <span class="text-white font-extrabold text-sm">${item.score_pct}%</span>
            </div>
            <div class="w-full bg-slate-800/80 rounded-full h-2.5 mb-2.5 overflow-hidden border border-slate-700/40">
              <div class="h-2.5 rounded-full transition-all duration-700 ease-out" style="width: ${item.score_pct}%; background-color: ${item.color}; box-shadow: 0 0 10px ${item.color}80;"></div>
            </div>
            <div class="flex items-center justify-between text-[11px] text-slate-400">
              <span>${item.correct}/${item.total} answered</span>
              <span class="px-2 py-0.5 rounded-full text-[10px] font-bold ${item.status === 'Mastered' ? 'bg-emerald-500/20 text-emerald-300 border border-emerald-500/30' : (item.status === 'In Progress' ? 'bg-amber-500/20 text-amber-300' : 'bg-slate-800 text-slate-500')}">
                ${item.status}
              </span>
            </div>
          `;
          bloomContainer.appendChild(card);
        });
      }

      // Achievement Badges
      renderBadges(data);

      // Recent attempts table
      const attemptsBody = document.getElementById('recent-attempts-body');
      if (attemptsBody) {
        if (!data.recent_attempts || data.recent_attempts.length === 0) {
          attemptsBody.innerHTML = `<tr><td colspan="5" class="py-6 text-center text-xs text-slate-500">No quiz attempts recorded yet. Launch an assessment to track cognitive growth!</td></tr>`;
        } else {
          attemptsBody.innerHTML = data.recent_attempts.map(a => `
            <tr class="border-b border-slate-800/60 text-xs hover:bg-slate-800/20 transition-all">
              <td class="py-3.5 font-semibold text-slate-200">${a.quiz_title}</td>
              <td class="py-3.5 text-slate-400 font-mono">${a.score}/${a.total_questions}</td>
              <td class="py-3.5">
                <span class="px-2.5 py-1 rounded-full text-xs font-extrabold shadow-sm ${a.percentage >= 80 ? 'bg-emerald-500/20 text-emerald-300 border border-emerald-500/30' : (a.percentage >= 60 ? 'bg-amber-500/20 text-amber-300 border border-amber-500/30' : 'bg-rose-500/20 text-rose-300 border border-rose-500/30')}">
                  ${a.percentage}%
                </span>
              </td>
              <td class="py-3.5 text-slate-400 font-mono">${Math.floor(a.time_spent_seconds / 60)}m ${a.time_spent_seconds % 60}s</td>
              <td class="py-3.5 text-slate-500">${a.attempted_at ? a.attempted_at.slice(0, 16) : 'Recently'}</td>
            </tr>
          `).join('');
        }
      }
    } catch (err) {
      console.warn('Analytics loading error:', err);
    }
  }

  function renderBadges(data) {
    const container = document.getElementById('achievements-grid');
    if (!container) return;

    const badges = [
      {
        id: 'first_quiz',
        name: 'Initiate Learner',
        desc: 'Complete your first diagnostic assessment',
        icon: '🎯',
        unlocked: data.total_quizzes >= 1
      },
      {
        id: 'high_score',
        name: 'Excellence Honor',
        desc: 'Achieve an average score of 80% or higher',
        icon: '🏆',
        unlocked: data.average_score >= 80 && data.total_quizzes >= 1
      },
      {
        id: 'streak',
        name: 'Deep Focus Streak',
        desc: 'Maintain an active daily study streak',
        icon: '🔥',
        unlocked: data.study_streak_days >= 2
      },
      {
        id: 'cards',
        name: 'Active Recall Master',
        desc: 'Build or review flashcard decks with SM-2',
        icon: '🗂️',
        unlocked: data.total_cards >= 4
      }
    ];

    container.innerHTML = badges.map(b => `
      <div class="glass-card p-3.5 rounded-xl border ${b.unlocked ? 'border-indigo-500/40 bg-indigo-950/20' : 'border-slate-800/80 bg-slate-900/40 opacity-50'} flex items-center gap-3">
        <span class="text-2xl">${b.icon}</span>
        <div>
          <div class="text-xs font-bold text-white flex items-center gap-1.5">
            ${b.name}
            ${b.unlocked ? '<span class="text-[9px] px-1.5 py-0.2 rounded bg-emerald-500/20 text-emerald-300 font-bold">UNLOCKED</span>' : '<span class="text-[9px] text-slate-500">LOCKED</span>'}
          </div>
          <div class="text-[11px] text-slate-400 mt-0.5">${b.desc}</div>
        </div>
      </div>
    `).join('');
  }

  window.loadAnalytics = loadAnalytics;
  loadAnalytics();
})();
