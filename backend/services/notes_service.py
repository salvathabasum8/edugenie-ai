from ..gemini_client import gemini_client
from ..prompts import get_notes_prompt
from ..database import save_notes, get_all_notes, get_note_by_id

class NotesService:
    @staticmethod
    def generate_notes(topic, format_style="comprehensive", context_text=None, title=None):
        prompt = get_notes_prompt(topic, format_style, context_text)
        content_markdown = gemini_client.generate_text(prompt)
        
        note_title = title or f"{topic} ({format_style.capitalize()} Notes)"
        
        # Save to database
        note_id = save_notes(
            title=note_title,
            topic=topic,
            format_style=format_style,
            content_markdown=content_markdown
        )

        return {
            "id": note_id,
            "title": note_title,
            "topic": topic,
            "format_style": format_style,
            "content": content_markdown
        }

    @staticmethod
    def list_notes(limit=20):
        return get_all_notes(limit=limit)

    @staticmethod
    def get_note(note_id):
        return get_note_by_id(note_id)
