from ..gemini_client import gemini_client
from ..prompts import get_tutor_system_prompt
from ..database import save_chat_message, get_chat_history

class TutorService:
    @staticmethod
    def chat(session_id, user_message, persona="socratic", context_text=None):
        system_instruction = get_tutor_system_prompt(persona)
        
        # Fetch previous history for conversation context
        history = get_chat_history(session_id, limit=6)
        
        history_prompt = ""
        if history:
            history_prompt = "Previous conversation turns:\n"
            for turn in history:
                role_label = "Student" if turn["role"] == "user" else "EduGenie"
                history_prompt += f"{role_label}: {turn['content']}\n"
            history_prompt += "\n"

        context_prompt = ""
        if context_text and context_text.strip():
            context_prompt = f"Reference Material Provided by Student:\n\"\"\"{context_text.strip()[:3000]}\"\"\"\n\n"

        full_prompt = f"{context_prompt}{history_prompt}Student Question: {user_message}\n\nPlease respond according to your persona ({persona}) and pedagogical guidelines."

        response_text = gemini_client.generate_text(
            full_prompt,
            system_instruction=system_instruction,
            user_question=user_message,
            persona=persona
        )

        # Save to database
        save_chat_message(session_id, "user", persona, user_message)
        save_chat_message(session_id, "assistant", persona, response_text)

        return {
            "session_id": session_id,
            "persona": persona,
            "response": response_text,
            "live_gemini": gemini_client.last_call_live,
            "api_error": gemini_client.last_error
        }

    @staticmethod
    def get_history(session_id):
        return get_chat_history(session_id)

    @staticmethod
    def clear_history(session_id):
        from ..database import clear_chat_history
        return clear_chat_history(session_id)

