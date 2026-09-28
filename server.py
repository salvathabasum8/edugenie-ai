#!/usr/bin/env python3
import os
import sys
import json
import mimetypes
import urllib.parse
from pathlib import Path
from http.server import HTTPServer, SimpleHTTPRequestHandler
from socketserver import ThreadingMixIn

# Add base directory to sys.path
BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))

from backend.config import DEFAULT_PORT, DEFAULT_HOST, FRONTEND_DIR, BLOOMS_LEVELS, TUTOR_PERSONAS, DEFAULT_MODEL
from backend.gemini_client import gemini_client
from backend.services import (
    TutorService,
    QuizService,
    NotesService,
    FlashcardService,
    RoadmapService,
    PDFService,
    AnalyticsService
)

class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
    daemon_threads = True

class EduGenieHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(FRONTEND_DIR), **kwargs)

    def log_message(self, format, *args):
        # Clean terminal logging
        cmd = getattr(self, "command", "-")
        path = getattr(self, "path", "-")
        code = args[1] if len(args) > 1 else (args[0] if args else "-")
        sys.stderr.write(f"[EduGenie] {cmd} {path} - {code}\n")

    def _send_json(self, data, status_code=200):
        body = json.dumps(data).encode("utf-8")
        self.send_response(status_code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.end_headers()
        self.wfile.write(body)

    def _read_json_body(self):
        content_length = int(self.headers.get("Content-Length", 0))
        if content_length == 0:
            return {}
        raw = self.rfile.read(content_length).decode("utf-8")
        try:
            return json.loads(raw)
        except Exception:
            return {}

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.end_headers()

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path
        query = urllib.parse.parse_qs(parsed.query)

        # Favicon handler
        if path == "/favicon.ico":
            svg = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><text y=".9em" font-size="90">🎓</text></svg>'.encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "image/svg+xml")
            self.send_header("Content-Length", str(len(svg)))
            self.send_header("Cache-Control", "public, max-age=86400")
            self.end_headers()
            self.wfile.write(svg)
            return

        # API Routes
        if path == "/api/status":
            has_key = gemini_client.has_api_key()
            self._send_json({
                "status": "healthy",
                "app": "EduGenie AI: Learning Assistant",
                "gemini_model": gemini_client.model,
                "has_gemini_api_key": has_key,
                "mode": "Live Google Gemini AI" if has_key else "Local Educational Simulator (Add API Key to activate live Gemini 3.8 Flash)",
                "blooms_levels": BLOOMS_LEVELS,
                "tutor_personas": TUTOR_PERSONAS
            })
            return

        elif path == "/api/analytics":
            metrics = AnalyticsService.get_dashboard_metrics()
            self._send_json(metrics)
            return

        elif path == "/api/quiz/history":
            history = QuizService.get_history(limit=20)
            self._send_json({"history": history})
            return

        elif path == "/api/quiz/recent":
            recent = QuizService.get_recent(limit=10)
            self._send_json({"quizzes": recent})
            return

        elif path == "/api/notes/list":
            notes = NotesService.list_notes(limit=30)
            self._send_json({"notes": notes})
            return

        elif path == "/api/notes/get":
            note_id = query.get("id", [None])[0]
            if note_id:
                note = NotesService.get_note(int(note_id))
                self._send_json({"note": note} if note else {"error": "Note not found"}, 200 if note else 404)
            else:
                self._send_json({"error": "Missing id parameter"}, 400)
            return

        elif path == "/api/flashcards/decks":
            decks = FlashcardService.list_decks()
            self._send_json({"decks": decks})
            return

        elif path == "/api/flashcards/deck":
            deck_id = query.get("id", [None])[0]
            if deck_id:
                deck = FlashcardService.get_deck(int(deck_id))
                self._send_json(deck)
            else:
                self._send_json({"error": "Missing id parameter"}, 400)
            return

        elif path == "/api/roadmap/list":
            roadmaps = RoadmapService.list_roadmaps(limit=10)
            self._send_json({"roadmaps": roadmaps})
            return

        elif path == "/api/tutor/history":
            session_id = query.get("session_id", ["default"])[0]
            history = TutorService.get_history(session_id)
            self._send_json({"history": history})
            return

        # Serve frontend static assets
        if path == "/" or path == "":
            self.path = "/index.html"
        return super().do_GET()

    def do_POST(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path
        body = self._read_json_body()

        # Update API key
        if path == "/api/config/key":
            key = body.get("api_key", "").strip()
            gemini_client.set_api_key(key)
            # Persist key to .env
            env_file = BASE_DIR / ".env"
            try:
                lines = []
                if env_file.exists():
                    lines = [l for l in env_file.read_text().splitlines() if not l.startswith("GEMINI_API_KEY=")]
                lines.append(f"GEMINI_API_KEY={key}")
                env_file.write_text("\n".join(lines) + "\n")
            except Exception as e:
                print(f"[EduGenie] Could not write to .env: {e}")

            self._send_json({
                "success": True,
                "has_key": gemini_client.has_api_key(),
                "model": gemini_client.model
            })
            return

        # Clear Tutor Session History
        elif path == "/api/tutor/clear":
            session_id = body.get("session_id", "default_session")
            TutorService.clear_history(session_id)
            self._send_json({"success": True})
            return

        # AI Tutor Chat
        elif path == "/api/tutor/chat":
            session_id = body.get("session_id", "default_session")
            message = body.get("message", "").strip()
            persona = body.get("persona", "socratic")
            context = body.get("context", None)

            if not message:
                self._send_json({"error": "Message cannot be empty"}, 400)
                return

            res = TutorService.chat(session_id, message, persona, context)
            self._send_json(res)
            return

        # Generate Adaptive Quiz
        elif path == "/api/quiz/generate":
            topic = body.get("topic", "Machine Learning Fundamentals").strip()
            difficulty = body.get("difficulty", "intermediate")
            bloom_level = body.get("bloom_level", "all")
            num_questions = int(body.get("num_questions", 5))
            context = body.get("context", None)

            quiz = QuizService.generate_quiz(topic, difficulty, bloom_level, num_questions, context)
            self._send_json(quiz)
            return

        # Submit & Evaluate Quiz
        elif path == "/api/quiz/submit":
            quiz_id = body.get("quiz_id")
            quiz_title = body.get("quiz_title", "Assessment")
            questions = body.get("questions", [])
            answers = body.get("answers", {})
            time_spent = int(body.get("time_spent", 0))

            results = QuizService.evaluate_quiz(quiz_id, quiz_title, questions, answers, time_spent)
            self._send_json(results)
            return

        # Generate Study Notes
        elif path == "/api/notes/generate":
            topic = body.get("topic", "").strip()
            format_style = body.get("format_style", "comprehensive")
            context = body.get("context", None)

            if not topic:
                self._send_json({"error": "Topic is required"}, 400)
                return

            notes = NotesService.generate_notes(topic, format_style, context)
            self._send_json(notes)
            return

        # Generate Flashcard Deck
        elif path == "/api/flashcards/generate":
            topic = body.get("topic", "").strip()
            num_cards = int(body.get("num_cards", 6))
            context = body.get("context", None)

            if not topic:
                self._send_json({"error": "Topic is required"}, 400)
                return

            deck = FlashcardService.generate_deck(topic, num_cards, context)
            self._send_json(deck)
            return

        # Review Flashcard (SM-2)
        elif path == "/api/flashcards/review":
            card_id = body.get("card_id")
            quality = int(body.get("quality", 4))

            if not card_id:
                self._send_json({"error": "Card ID required"}, 400)
                return

            progress = FlashcardService.review_card(card_id, quality)
            self._send_json({"success": True, "progress": progress})
            return

        # Generate Study Roadmap
        elif path == "/api/roadmap/generate":
            goal = body.get("goal", "").strip()
            duration_days = int(body.get("duration_days", 14))
            weekly_hours = int(body.get("weekly_hours", 10))

            if not goal:
                self._send_json({"error": "Goal/Topic is required"}, 400)
                return

            roadmap = RoadmapService.generate_roadmap(goal, duration_days, weekly_hours)
            self._send_json(roadmap)
            return

        # Extract Document Text
        elif path == "/api/document/extract":
            text = body.get("text", "")
            # If base64 or raw text
            if not text:
                self._send_json({"error": "No content provided"}, 400)
                return
            summary = PDFService.summarize_document(text)
            self._send_json({"extracted_text": text, "summary": summary, "char_count": len(text)})
            return

        else:
            self._send_json({"error": "Endpoint not found"}, 404)

def run_server(port=DEFAULT_PORT, host=DEFAULT_HOST):
    server_address = (host, port)
    httpd = ThreadedHTTPServer(server_address, EduGenieHandler)
    print(f"================================================================")
    print(f" 🚀 EduGenie AI: Google Gemini Powered Learning Assistant Server")
    print(f" 🌐 Running at: http://localhost:{port}")
    print(f" 💡 Model: {gemini_client.model}")
    print(f" 🔑 API Key Status: {'Configured' if gemini_client.has_api_key() else 'Local Demo Engine Active (Set key anytime)'}")
    print(f"================================================================")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down EduGenie server...")
        httpd.server_close()

if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_PORT
    run_server(port=port)
