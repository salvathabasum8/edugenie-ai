from ..gemini_client import gemini_client
from ..prompts import get_flashcards_prompt
from ..database import save_flashcard_deck, get_flashcard_decks, get_deck_cards, update_card_spaced_repetition

class FlashcardService:
    @staticmethod
    def generate_deck(topic, num_cards=8, context_text=None):
        prompt = get_flashcards_prompt(topic, num_cards, context_text)
        data = gemini_client.generate_json(prompt)

        cards = data.get("cards", [])
        if not cards:
            # Fallback cards
            cards = [
                {
                    "front": f"What is the core definition of {topic}?",
                    "back": f"{topic} involves the systematic study and application of core analytical principles to solve complex problems.",
                    "hint": "Recall the textbook definition.",
                    "bloom_level": "remember"
                },
                {
                    "front": f"How do you apply {topic} in practice?",
                    "back": "By establishing clear input objectives, validating hypotheses, and iterating against measurable performance criteria.",
                    "hint": "Think of execution workflow.",
                    "bloom_level": "apply"
                }
            ]

        deck_title = data.get("deck_title", f"{topic} Mastery Deck")
        deck_id = save_flashcard_deck(deck_title, topic, cards)
        
        saved_cards = get_deck_cards(deck_id)

        return {
            "deck_id": deck_id,
            "title": deck_title,
            "topic": topic,
            "card_count": len(saved_cards),
            "cards": saved_cards
        }

    @staticmethod
    def list_decks():
        return get_flashcard_decks()

    @staticmethod
    def get_deck(deck_id):
        cards = get_deck_cards(deck_id)
        return {
            "deck_id": deck_id,
            "cards": cards
        }

    @staticmethod
    def review_card(card_id, quality):
        """
        quality: 0 (blackout) to 5 (perfect recall)
        """
        return update_card_spaced_repetition(card_id, quality)
