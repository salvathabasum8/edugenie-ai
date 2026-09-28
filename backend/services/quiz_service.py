from ..gemini_client import gemini_client
from ..prompts import get_quiz_prompt
from ..database import save_quiz, save_quiz_attempt, get_recent_quizzes, get_quiz_attempts
from ..config import BLOOMS_LEVELS

class QuizService:
    @staticmethod
    def generate_quiz(topic, difficulty="intermediate", bloom_level="all", num_questions=5, context_text=None):
        prompt = get_quiz_prompt(topic, difficulty, bloom_level, num_questions, context_text)
        data = gemini_client.generate_json(prompt)
        
        # Validate data structure
        if not isinstance(data, dict) or "questions" not in data or not data["questions"]:
            # Fallback format protection
            data = {
                "title": f"{topic} Diagnostic Assessment",
                "topic": topic,
                "difficulty": difficulty,
                "bloom_level_focus": bloom_level,
                "questions": [
                    {
                        "id": 1,
                        "question": f"Which foundational concept is most essential when understanding {topic}?",
                        "options": [
                            "Understanding the core mathematical/theoretical principles",
                            "Memorizing random facts without conceptual structure",
                            "Ignoring edge case constraints",
                            "Relying solely on intuition without testing"
                        ],
                        "correct_index": 0,
                        "bloom_level": "remember",
                        "bloom_name": "Remembering",
                        "explanation": f"Foundational principles form the cognitive anchor for mastering {topic}.",
                        "hint": "Focus on the systematic building blocks."
                    }
                ]
            }

        # Normalize questions list
        questions = data.get("questions", [])
        for i, q in enumerate(questions):
            q["id"] = i + 1
            if "bloom_level" not in q or q["bloom_level"] not in BLOOMS_LEVELS:
                q["bloom_level"] = "understand"
            q["bloom_name"] = BLOOMS_LEVELS[q["bloom_level"]]["name"]

        # Persist generated quiz
        quiz_id = save_quiz(
            title=data.get("title", f"{topic} Quiz"),
            topic=topic,
            difficulty=difficulty,
            bloom_level=bloom_level,
            num_questions=len(questions),
            content_dict=data
        )
        data["quiz_id"] = quiz_id
        return data

    @staticmethod
    def evaluate_quiz(quiz_id, quiz_title, questions, user_answers, time_spent=0):
        """
        user_answers: dict {question_id: selected_option_index}
        """
        score = 0
        total = len(questions)
        detailed_results = []
        
        bloom_breakdown = {
            "remember": {"correct": 0, "total": 0},
            "understand": {"correct": 0, "total": 0},
            "apply": {"correct": 0, "total": 0},
            "analyze": {"correct": 0, "total": 0},
            "evaluate": {"correct": 0, "total": 0},
            "create": {"correct": 0, "total": 0}
        }

        for q in questions:
            q_id = q.get("id")
            # user answer can be int or string
            user_ans = user_answers.get(str(q_id), user_answers.get(q_id, None))
            correct_ans = q.get("correct_index", 0)
            bloom_lvl = q.get("bloom_level", "understand")
            if bloom_lvl not in bloom_breakdown:
                bloom_lvl = "understand"

            bloom_breakdown[bloom_lvl]["total"] += 1
            is_correct = (user_ans is not None and int(user_ans) == int(correct_ans))

            if is_correct:
                score += 1
                bloom_breakdown[bloom_lvl]["correct"] += 1

            detailed_results.append({
                "id": q_id,
                "question": q.get("question"),
                "options": q.get("options", []),
                "user_selected": user_ans,
                "correct_index": correct_ans,
                "is_correct": is_correct,
                "bloom_level": bloom_lvl,
                "bloom_name": BLOOMS_LEVELS.get(bloom_lvl, {}).get("name", bloom_lvl.capitalize()),
                "explanation": q.get("explanation", ""),
                "hint": q.get("hint", "")
            })

        percentage = round((score / max(total, 1)) * 100, 1)

        # Save attempt to database
        attempt_id = save_quiz_attempt(
            quiz_id=quiz_id,
            quiz_title=quiz_title,
            score=score,
            total_questions=total,
            answers=detailed_results,
            bloom_breakdown=bloom_breakdown,
            time_spent=time_spent
        )

        # Generate cognitive feedback summary
        recommendations = []
        for lvl, stats in bloom_breakdown.items():
            if stats["total"] > 0:
                pct = (stats["correct"] / stats["total"]) * 100
                if pct < 60:
                    lvl_info = BLOOMS_LEVELS.get(lvl, {})
                    recommendations.append(f"Strengthen **{lvl_info.get('name', lvl)}** skills: Focus on {lvl_info.get('description', '')}.")

        if not recommendations:
            recommendations.append("Excellent mastery demonstrated across all cognitive taxonomy tiers!")

        return {
            "attempt_id": attempt_id,
            "quiz_id": quiz_id,
            "quiz_title": quiz_title,
            "score": score,
            "total_questions": total,
            "percentage": percentage,
            "bloom_breakdown": bloom_breakdown,
            "recommendations": recommendations,
            "detailed_results": detailed_results,
            "time_spent": time_spent
        }

    @staticmethod
    def get_history(limit=20):
        return get_quiz_attempts(limit=limit)

    @staticmethod
    def get_recent(limit=10):
        return get_recent_quizzes(limit=limit)
