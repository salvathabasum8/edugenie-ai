// Adaptive Quiz Engine Module with Sound FX, Confetti & Bloom Analytics
(function () {
  let activeQuiz = null;
  let userAnswers = {};
  let timerInterval = null;
  let elapsedSeconds = 0;

  const quizSetup = document.getElementById('quiz-setup');
  const quizRunner = document.getElementById('quiz-runner');
  const quizResults = document.getElementById('quiz-results');

  const topicInput = document.getElementById('quiz-topic-input');
  const diffSelect = document.getElementById('quiz-difficulty');
  const bloomSelect = document.getElementById('quiz-bloom-select');
  const numSelect = document.getElementById('quiz-num-questions');
  const genBtn = document.getElementById('generate-quiz-btn');

  const bloomColors = {
    remember: '#3B82F6',
    understand: '#10B981',
    apply: '#F59E0B',
    analyze: '#8B5CF6',
    evaluate: '#EC4899',
    create: '#EF4444'
  };

  async function generateQuiz() {
    if (window.SoundFX) SoundFX.click();
    const topic = topicInput ? topicInput.value.trim() : 'Machine Learning Foundations';
    const difficulty = diffSelect ? diffSelect.value : 'intermediate';
    const bloom = bloomSelect ? bloomSelect.value : 'all';
    const num = numSelect ? parseInt(numSelect.value) : 5;

    genBtn.disabled = true;
    genBtn.innerHTML = `
      <svg class="animate-spin -ml-1 mr-2 h-4 w-4 text-white inline" fill="none" viewBox="0 0 24 24">
        <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
        <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8H4z"></path>
      </svg>
      Formulating Bloom's Taxonomy Assessment...
    `;

    try {
      const data = await apiCall('/api/quiz/generate', 'POST', {
        topic,
        difficulty,
        bloom_level: bloom,
        num_questions: num
      });
      activeQuiz = data;
      userAnswers = {};
      startQuizRunner(data);
      if (window.SoundFX) SoundFX.correct();
    } catch (err) {
      alert('Error generating quiz: ' + err.message);
      if (window.SoundFX) SoundFX.wrong();
    } finally {
      genBtn.disabled = false;
      genBtn.innerHTML = '🚀 Generate Adaptive Quiz';
    }
  }

  function startQuizRunner(quiz) {
    if (!quizRunner) return;
    quizSetup.classList.add('hidden');
    quizResults.classList.add('hidden');
    quizRunner.classList.remove('hidden');

    document.getElementById('runner-quiz-title').textContent = quiz.title || `${quiz.topic} Assessment`;
    document.getElementById('runner-quiz-topic').textContent = quiz.topic;
    document.getElementById('runner-quiz-diff').textContent = quiz.difficulty.toUpperCase();

    updateProgressBar();

    elapsedSeconds = 0;
    if (timerInterval) clearInterval(timerInterval);
    timerInterval = setInterval(() => {
      elapsedSeconds++;
      const mins = String(Math.floor(elapsedSeconds / 60)).padStart(2, '0');
      const secs = String(elapsedSeconds % 60).padStart(2, '0');
      const tEl = document.getElementById('quiz-timer');
      if (tEl) {
        tEl.textContent = `${mins}:${secs}`;
        if (elapsedSeconds > 300) {
          tEl.className = 'text-lg font-mono font-bold text-rose-400 animate-pulse';
        }
      }
    }, 1000);

    renderQuestions(quiz.questions);
  }

  function updateProgressBar() {
    if (!activeQuiz) return;
    const total = activeQuiz.questions.length;
    const answered = Object.keys(userAnswers).length;
    const pct = Math.round((answered / total) * 100);
    
    const bar = document.getElementById('quiz-progress-bar');
    const label = document.getElementById('quiz-progress-label');
    if (bar) bar.style.width = `${pct}%`;
    if (label) label.textContent = `${answered} of ${total} answered (${pct}%)`;
  }

  function renderQuestions(questions) {
    const container = document.getElementById('questions-container');
    if (!container) return;
    container.innerHTML = '';

    questions.forEach((q, idx) => {
      const qCard = document.createElement('div');
      qCard.className = 'glass-card p-6 mb-5 rounded-2xl border border-slate-700/60 transition-all';

      const color = bloomColors[q.bloom_level] || '#6366F1';
      const bloomName = q.bloom_name || (q.bloom_level ? q.bloom_level.toUpperCase() : 'Cognitive');

      qCard.innerHTML = `
        <div class="flex items-center justify-between gap-2 mb-3">
          <span class="text-xs font-semibold text-slate-400 uppercase tracking-wider">Question ${idx + 1} of ${questions.length}</span>
          <span class="text-xs font-bold px-2.5 py-0.5 rounded-full text-white shadow-sm" style="background-color: ${color}">
            ● Bloom: ${bloomName}
          </span>
        </div>
        <h4 class="text-sm md:text-base font-semibold text-white mb-4 leading-relaxed">${q.question}</h4>
        <div class="options-group space-y-2.5" data-qid="${q.id}">
          ${q.options.map((opt, optIdx) => `
            <label class="flex items-start gap-3 p-3.5 rounded-xl border border-slate-700/70 hover:border-indigo-500/60 hover:bg-indigo-950/25 cursor-pointer transition-all option-label">
              <input type="radio" name="q_${q.id}" value="${optIdx}" class="mt-1 text-indigo-600 focus:ring-indigo-500">
              <span class="text-xs md:text-sm text-slate-200">${opt}</span>
            </label>
          `).join('')}
        </div>
        ${q.hint ? `
          <div class="mt-4 pt-3 border-t border-slate-800">
            <details class="text-xs text-slate-400 cursor-pointer">
              <summary class="hover:text-indigo-300 font-medium select-none">💡 Need a Hint?</summary>
              <p class="mt-2 pl-4 text-slate-300 italic border-l-2 border-indigo-500">${q.hint}</p>
            </details>
          </div>
        ` : ''}
      `;

      // Track choice with sound
      qCard.querySelectorAll('input[type="radio"]').forEach(radio => {
        radio.addEventListener('change', (e) => {
          if (window.SoundFX) SoundFX.click();
          userAnswers[String(q.id)] = parseInt(e.target.value);
          updateProgressBar();

          // Highlight selected label
          qCard.querySelectorAll('.option-label').forEach(lbl => lbl.classList.remove('bg-indigo-900/30', 'border-indigo-500'));
          radio.closest('label').classList.add('bg-indigo-900/30', 'border-indigo-500');
        });
      });

      container.appendChild(qCard);
    });
  }

  async function submitQuiz() {
    if (!activeQuiz) return;
    if (timerInterval) clearInterval(timerInterval);

    const submitBtn = document.getElementById('submit-quiz-btn');
    submitBtn.disabled = true;
    submitBtn.innerHTML = 'Scoring & Calculating Bloom Mastery...';

    try {
      const evalRes = await apiCall('/api/quiz/submit', 'POST', {
        quiz_id: activeQuiz.quiz_id,
        quiz_title: activeQuiz.title,
        questions: activeQuiz.questions,
        answers: userAnswers,
        time_spent: elapsedSeconds
      });
      displayResults(evalRes);
      
      // Sound & Confetti trigger
      if (evalRes.percentage >= 80) {
        if (window.Confetti) Confetti.burst();
        if (window.SoundFX) SoundFX.celebrate();
      } else {
        if (window.SoundFX) SoundFX.correct();
      }
    } catch (err) {
      alert('Error submitting quiz: ' + err.message);
    } finally {
      submitBtn.disabled = false;
      submitBtn.innerHTML = 'Submit Assessment & View Diagnostic Report 🏁';
    }
  }

  function displayResults(res) {
    quizRunner.classList.add('hidden');
    quizResults.classList.remove('hidden');

    document.getElementById('result-score-num').textContent = `${res.score} / ${res.total_questions}`;
    document.getElementById('result-pct').textContent = `${res.percentage}%`;
    document.getElementById('result-time').textContent = `${Math.floor(res.time_spent / 60)}m ${res.time_spent % 60}s`;

    // Bloom breakdown render
    const breakdownContainer = document.getElementById('bloom-breakdown-results');
    if (breakdownContainer) {
      breakdownContainer.innerHTML = '';
      for (const [key, stats] of Object.entries(res.bloom_breakdown)) {
        if (stats.total > 0) {
          const pct = Math.round((stats.correct / stats.total) * 100);
          const color = bloomColors[key] || '#6366F1';
          const card = document.createElement('div');
          card.className = 'glass-card p-3.5 rounded-xl text-center border border-slate-700/50 shadow-sm';
          card.innerHTML = `
            <div class="text-[11px] font-bold uppercase mb-1" style="color:${color}">${key}</div>
            <div class="text-xl font-extrabold text-white">${pct}%</div>
            <div class="text-[10px] text-slate-400 mt-0.5">${stats.correct}/${stats.total} correct</div>
          `;
          breakdownContainer.appendChild(card);
        }
      }
    }

    // Recommendations
    const recContainer = document.getElementById('result-recommendations');
    if (recContainer) {
      recContainer.innerHTML = res.recommendations.map(r => `
        <li class="flex items-start gap-2.5 text-xs text-slate-300">
          <span class="text-indigo-400 font-bold mt-0.5">●</span>
          <span>${r}</span>
        </li>
      `).join('');
    }

    // Detailed Review
    const reviewContainer = document.getElementById('detailed-review-container');
    if (reviewContainer) {
      reviewContainer.innerHTML = res.detailed_results.map((item, idx) => `
        <div class="glass-card p-5 mb-4 rounded-xl border ${item.is_correct ? 'border-emerald-500/40 bg-emerald-950/15' : 'border-rose-500/40 bg-rose-950/15'}">
          <div class="flex items-center justify-between gap-2 mb-2.5">
            <span class="text-xs font-bold ${item.is_correct ? 'text-emerald-400' : 'text-rose-400'} flex items-center gap-1.5">
              ${item.is_correct ? '✅ Correct' : '❌ Incorrect'} • Question ${idx + 1}
            </span>
            <span class="text-xs px-2.5 py-0.5 rounded-full text-slate-300 bg-slate-800 font-medium">
              Bloom: ${item.bloom_name}
            </span>
          </div>
          <p class="text-sm font-semibold text-white mb-3.5 leading-relaxed">${item.question}</p>
          <div class="text-xs space-y-1.5 text-slate-300 mb-4 bg-slate-900/60 p-3 rounded-lg border border-slate-800">
            <div><strong class="text-slate-400">Your selection:</strong> ${item.user_selected !== null ? item.options[item.user_selected] : '<span class="text-amber-400">Unanswered</span>'}</div>
            ${!item.is_correct ? `<div class="text-emerald-300 font-medium"><strong class="text-slate-400">Correct answer:</strong> ${item.options[item.correct_index]}</div>` : ''}
          </div>
          <div class="p-3.5 bg-slate-900/80 rounded-xl text-xs text-slate-300 border border-slate-800/80 leading-relaxed">
            <strong class="text-indigo-300 block mb-1">Pedagogical Explanation:</strong>
            ${item.explanation}
          </div>
        </div>
      `).join('');
      enhanceCodeBlocks(reviewContainer);
    }
  }

  function resetQuiz() {
    if (window.SoundFX) SoundFX.click();
    quizResults.classList.add('hidden');
    quizRunner.classList.add('hidden');
    quizSetup.classList.remove('hidden');
  }

  if (genBtn) genBtn.addEventListener('click', generateQuiz);
  const submitBtn = document.getElementById('submit-quiz-btn');
  if (submitBtn) submitBtn.addEventListener('click', submitQuiz);
  const retakeBtn = document.getElementById('retake-quiz-btn');
  if (retakeBtn) retakeBtn.addEventListener('click', resetQuiz);
})();
