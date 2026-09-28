// Flashcards & Spaced Repetition (SM-2) Module with Sound FX & Keyboard Shortcuts
(function () {
  let currentDeck = null;
  let currentCardIndex = 0;
  let isFlipped = false;

  const topicInput = document.getElementById('flashcards-topic-input');
  const countSelect = document.getElementById('flashcards-count-select');
  const genBtn = document.getElementById('generate-flashcards-btn');
  const deckSelect = document.getElementById('deck-selector');

  const cardViewer = document.getElementById('flashcard-viewer');
  const cardInner = document.getElementById('card-inner');
  const cardFrontText = document.getElementById('card-front-text');
  const cardBackText = document.getElementById('card-back-text');
  const cardHintText = document.getElementById('card-hint-text');
  const cardBloomTag = document.getElementById('card-bloom-tag');
  const cardCounter = document.getElementById('card-counter');
  const ratingControls = document.getElementById('rating-controls');

  async function loadDecks() {
    try {
      const res = await apiCall('/api/flashcards/decks');
      if (deckSelect) {
        deckSelect.innerHTML = '<option value="">-- Select Saved Deck --</option>';
        res.decks.forEach(d => {
          const opt = document.createElement('option');
          opt.value = d.id;
          opt.textContent = `${d.title} (${d.card_count || 0} cards)`;
          deckSelect.appendChild(opt);
        });
      }
    } catch (err) {
      console.warn('Failed to load decks:', err);
    }
  }
  window.loadDecks = loadDecks;

  async function generateDeck() {
    if (window.SoundFX) SoundFX.click();
    const topic = topicInput ? topicInput.value.trim() : 'Computer Science Foundations';
    const num = countSelect ? parseInt(countSelect.value) : 6;

    genBtn.disabled = true;
    genBtn.innerHTML = `
      <svg class="animate-spin -ml-1 mr-2 h-4 w-4 text-white inline" fill="none" viewBox="0 0 24 24">
        <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
        <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8H4z"></path>
      </svg>
      Synthesizing Flashcard Deck...
    `;

    try {
      const data = await apiCall('/api/flashcards/generate', 'POST', {
        topic,
        num_cards: num
      });
      currentDeck = data;
      currentCardIndex = 0;
      renderCurrentCard();
      loadDecks();
      if (window.SoundFX) SoundFX.correct();
    } catch (err) {
      alert('Error creating flashcard deck: ' + err.message);
      if (window.SoundFX) SoundFX.wrong();
    } finally {
      genBtn.disabled = false;
      genBtn.innerHTML = '🗂️ Generate Spaced Repetition Deck';
    }
  }

  async function selectDeck(deckId) {
    if (!deckId) return;
    if (window.SoundFX) SoundFX.click();
    try {
      const data = await apiCall(`/api/flashcards/deck?id=${deckId}`);
      currentDeck = data;
      currentCardIndex = 0;
      renderCurrentCard();
    } catch (err) {
      alert('Error loading deck: ' + err.message);
    }
  }

  function renderCurrentCard() {
    if (!currentDeck || !currentDeck.cards || currentDeck.cards.length === 0) {
      if (cardViewer) cardViewer.classList.add('hidden');
      return;
    }

    if (cardViewer) cardViewer.classList.remove('hidden');
    isFlipped = false;
    if (cardInner) cardInner.classList.remove('flipped');
    if (ratingControls) ratingControls.classList.add('hidden');

    const card = currentDeck.cards[currentCardIndex];
    if (cardFrontText) cardFrontText.textContent = card.front;
    if (cardBackText) cardBackText.textContent = card.back;
    if (cardHintText) {
      cardHintText.textContent = card.hint ? `💡 Hint: ${card.hint}` : '';
    }
    if (cardBloomTag) {
      cardBloomTag.textContent = `Bloom: ${(card.bloom_level || 'concept').toUpperCase()}`;
    }
    if (cardCounter) {
      cardCounter.textContent = `Card ${currentCardIndex + 1} of ${currentDeck.cards.length}`;
    }
  }

  function flipCard() {
    if (window.SoundFX) SoundFX.flip();
    isFlipped = !isFlipped;
    if (cardInner) {
      cardInner.classList.toggle('flipped', isFlipped);
    }
    if (ratingControls && isFlipped) {
      ratingControls.classList.remove('hidden');
    }
  }

  async function handleRate(quality) {
    if (window.SoundFX) SoundFX.click();
    if (!currentDeck || !currentDeck.cards[currentCardIndex]) return;
    const card = currentDeck.cards[currentCardIndex];

    try {
      await apiCall('/api/flashcards/review', 'POST', {
        card_id: card.id,
        quality: quality
      });
    } catch (e) {
      console.warn('Failed to update SM-2 schedule:', e);
    }

    // Check if deck finished
    if (currentCardIndex === currentDeck.cards.length - 1) {
      if (window.Confetti) Confetti.burst();
      if (window.SoundFX) SoundFX.celebrate();
    }

    // Move to next card
    currentCardIndex = (currentCardIndex + 1) % currentDeck.cards.length;
    renderCurrentCard();
  }

  if (genBtn) genBtn.addEventListener('click', generateDeck);
  if (deckSelect) {
    deckSelect.addEventListener('change', (e) => selectDeck(e.target.value));
  }

  const flipBtn = document.getElementById('flip-card-btn');
  if (flipBtn) flipBtn.addEventListener('click', flipCard);
  if (cardInner) cardInner.addEventListener('click', flipCard);

  // Rating buttons
  document.querySelectorAll('.rate-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      const q = parseInt(btn.getAttribute('data-quality') || '4');
      handleRate(q);
    });
  });

  const nextCardBtn = document.getElementById('next-card-btn');
  if (nextCardBtn) {
    nextCardBtn.addEventListener('click', () => {
      if (window.SoundFX) SoundFX.click();
      if (!currentDeck) return;
      currentCardIndex = (currentCardIndex + 1) % currentDeck.cards.length;
      renderCurrentCard();
    });
  }

  const prevCardBtn = document.getElementById('prev-card-btn');
  if (prevCardBtn) {
    prevCardBtn.addEventListener('click', () => {
      if (window.SoundFX) SoundFX.click();
      if (!currentDeck) return;
      currentCardIndex = (currentCardIndex - 1 + currentDeck.cards.length) % currentDeck.cards.length;
      renderCurrentCard();
    });
  }

  // Keyboard navigation for power users: Space to flip, 1-4 for ratings
  window.addEventListener('keydown', (e) => {
    if (state.currentTab !== 'flashcards') return;
    // Don't trigger if user is typing inside an input or textarea
    if (['INPUT', 'TEXTAREA'].includes(document.activeElement.tagName)) return;

    if (e.code === 'Space') {
      e.preventDefault();
      flipCard();
    } else if (['Digit1', 'Digit2', 'Digit3', 'Digit4'].includes(e.code)) {
      e.preventDefault();
      const qualityMap = { Digit1: 1, Digit2: 2, Digit3: 4, Digit4: 5 };
      handleRate(qualityMap[e.code]);
    }
  });

  // Load initial decks
  loadDecks();
})();
