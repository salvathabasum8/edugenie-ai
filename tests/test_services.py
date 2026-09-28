import sys
from pathlib import Path

# Add project root to sys.path
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from backend.services import (
    TutorService,
    QuizService,
    NotesService,
    FlashcardService,
    RoadmapService,
    AnalyticsService
)

def test_tutor_service():
    print("Testing TutorService...")
    res = TutorService.chat("test_session_1", "What is the primary role of an activation function in neural networks?", persona="socratic")
    assert "response" in res, "Tutor response missing"
    assert len(res["response"]) > 20, "Tutor response too short"
    print("✓ TutorService passed")

def test_quiz_service():
    print("Testing QuizService generation & evaluation...")
    quiz = QuizService.generate_quiz("Linear Regression", difficulty="intermediate", bloom_level="all", num_questions=3)
    assert "questions" in quiz, "Questions missing in quiz"
    assert len(quiz["questions"]) >= 1, "No questions returned"
    
    # Test evaluation
    answers = {"1": quiz["questions"][0]["correct_index"]}
    eval_res = QuizService.evaluate_quiz(
        quiz.get("quiz_id", 1),
        quiz.get("title", "Assessment"),
        quiz["questions"],
        answers,
        time_spent=45
    )
    assert eval_res["score"] >= 1, "Evaluation score error"
    assert "bloom_breakdown" in eval_res, "Bloom breakdown missing"
    assert "recommendations" in eval_res, "Recommendations missing"
    print("✓ QuizService passed")

def test_notes_service():
    print("Testing NotesService...")
    notes = NotesService.generate_notes("Backpropagation Calculus", format_style="comprehensive")
    assert "content" in notes, "Notes content missing"
    assert "id" in notes, "Note ID missing"
    assert "#" in notes["content"], "Markdown headings missing"
    print("✓ NotesService passed")

def test_flashcard_service():
    print("Testing FlashcardService...")
    deck = FlashcardService.generate_deck("Cloud Networking", num_cards=4)
    assert "cards" in deck, "Cards missing"
    assert len(deck["cards"]) >= 1, "Deck cards empty"

    # Test SM-2 spaced repetition review
    card_id = deck["cards"][0]["id"]
    progress = FlashcardService.review_card(card_id, quality=5)
    assert progress is not None, "SM-2 progress return is None"
    assert progress["repetitions"] >= 1, "Repetitions did not increment"
    print("✓ FlashcardService passed")

def test_roadmap_service():
    print("Testing RoadmapService...")
    roadmap = RoadmapService.generate_roadmap("TensorFlow Developer Certificate", duration_days=14, weekly_hours=8)
    assert "phases" in roadmap, "Roadmap phases missing"
    assert len(roadmap["phases"]) >= 1, "Phases list empty"
    print("✓ RoadmapService passed")

def test_analytics_service():
    print("Testing AnalyticsService...")
    metrics = AnalyticsService.get_dashboard_metrics()
    assert "total_quizzes" in metrics, "Total quizzes metric missing"
    assert "bloom_details" in metrics, "Bloom details missing"
    assert len(metrics["bloom_details"]) == 6, "Expected 6 Bloom's levels"
    print("✓ AnalyticsService passed")

if __name__ == "__main__":
    print("--- Running EduGenie Backend Unit Tests ---")
    test_tutor_service()
    test_quiz_service()
    test_notes_service()
    test_flashcard_service()
    test_roadmap_service()
    test_analytics_service()
    print("All service tests passed successfully! 🎉")
