from ..database import compute_analytics, get_quiz_attempts, get_all_notes, get_flashcard_decks
from ..config import BLOOMS_LEVELS

class AnalyticsService:
    @staticmethod
    def get_dashboard_metrics():
        metrics = compute_analytics()
        recent_attempts = get_quiz_attempts(limit=5)
        recent_notes = get_all_notes(limit=5)
        decks = get_flashcard_decks()

        # Format Bloom's radar/bar chart data
        bloom_data = []
        for key, info in BLOOMS_LEVELS.items():
            stat = metrics["bloom_mastery"].get(key, {"score_pct": 0, "correct": 0, "total": 0})
            stats_total = stat["total"]
            bloom_data.append({
                "level_key": key,
                "name": info["name"],
                "color": info["color"],
                "score_pct": stat["score_pct"],
                "correct": stat["correct"],
                "total": stats_total,
                "status": "Mastered" if stat["score_pct"] >= 80 and stats_total >= 3 else ("In Progress" if stats_total > 0 else "Not Started")
            })

        metrics["bloom_details"] = bloom_data
        metrics["recent_attempts"] = recent_attempts
        metrics["recent_notes"] = recent_notes
        metrics["decks"] = decks
        return metrics
