from ..gemini_client import gemini_client
from ..prompts import get_roadmap_prompt
from ..database import save_roadmap, get_all_roadmaps

class RoadmapService:
    @staticmethod
    def generate_roadmap(goal, duration_days=14, weekly_hours=10):
        prompt = get_roadmap_prompt(goal, duration_days, weekly_hours)
        data = gemini_client.generate_json(prompt)

        if not isinstance(data, dict) or "phases" not in data:
            data = {
                "title": f"{goal} Learning Path",
                "goal": goal,
                "duration_days": duration_days,
                "weekly_hours": weekly_hours,
                "phases": [
                    {
                        "phase_number": 1,
                        "phase_name": "Phase 1: Foundations",
                        "days_range": f"Days 1-{max(2, duration_days // 3)}",
                        "key_objectives": ["Grasp fundamental principles", "Understand core terminology"],
                        "daily_milestones": [
                            {"day": 1, "task": "Overview of concepts and terminology", "checkpoint": "Active recall check", "estimated_minutes": 60}
                        ]
                    }
                ],
                "capstone_challenge": f"Build a practical synthesis artifact demonstrating mastery in {goal}.",
                "expert_tips": ["Review notes with spaced intervals", "Test yourself before looking at answers"]
            }

        title = data.get("title", f"{goal} Mastery Roadmap")
        roadmap_id = save_roadmap(title, goal, duration_days, weekly_hours, data)
        data["roadmap_id"] = roadmap_id
        return data

    @staticmethod
    def list_roadmaps(limit=10):
        return get_all_roadmaps(limit=limit)
