import sys
import io
import json
from pathlib import Path

# Add project root to sys.path
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from server import EduGenieHandler

class MockSocket:
    def __init__(self, data=b""):
        self.rfile = io.BytesIO(data)
        self.wfile = io.BytesIO()

    def makefile(self, mode, *args, **kwargs):
        if "b" in mode:
            if "r" in mode:
                return self.rfile
            else:
                return self.wfile
        return self.rfile

class MockEduGenieHandler(EduGenieHandler):
    def __init__(self, method, path, body=None):
        self.command = method
        self.path = path
        self.request_version = "HTTP/1.1"
        self.headers = {}
        if body:
            raw_body = json.dumps(body).encode("utf-8")
            self.headers["Content-Length"] = str(len(raw_body))
            self.rfile = io.BytesIO(raw_body)
        else:
            self.rfile = io.BytesIO(b"")
        self.wfile = io.BytesIO()

    def send_response(self, code, message=None):
        self.status_code = code

    def send_header(self, keyword, value):
        pass

    def end_headers(self):
        pass

def test_handler_endpoints():
    print("Testing EduGenieHandler routes (socketless in-memory test)...")

    # 1. GET /api/status
    h_status = MockEduGenieHandler("GET", "/api/status")
    h_status.do_GET()
    assert h_status.status_code == 200
    res = json.loads(h_status.wfile.getvalue().decode())
    assert res["status"] == "healthy"
    assert "EduGenie" in res["app"]
    print("✓ GET /api/status passed")

    # 2. GET /api/analytics
    h_analytics = MockEduGenieHandler("GET", "/api/analytics")
    h_analytics.do_GET()
    assert h_analytics.status_code == 200
    res = json.loads(h_analytics.wfile.getvalue().decode())
    assert "bloom_mastery" in res
    print("✓ GET /api/analytics passed")

    # 3. POST /api/tutor/chat
    h_tutor = MockEduGenieHandler("POST", "/api/tutor/chat", {
        "session_id": "test_session_mock",
        "message": "Explain vectors in 2 sentences",
        "persona": "eli5"
    })
    h_tutor.do_POST()
    assert h_tutor.status_code == 200
    res = json.loads(h_tutor.wfile.getvalue().decode())
    assert "response" in res
    print("✓ POST /api/tutor/chat passed")

    # 4. POST /api/quiz/generate
    h_quiz = MockEduGenieHandler("POST", "/api/quiz/generate", {
        "topic": "Python Programming",
        "difficulty": "intermediate",
        "bloom_level": "all",
        "num_questions": 3
    })
    h_quiz.do_POST()
    assert h_quiz.status_code == 200
    res = json.loads(h_quiz.wfile.getvalue().decode())
    assert "questions" in res
    print("✓ POST /api/quiz/generate passed")

    # 5. POST /api/notes/generate
    h_notes = MockEduGenieHandler("POST", "/api/notes/generate", {
        "topic": "Sorting Algorithms",
        "format_style": "comprehensive"
    })
    h_notes.do_POST()
    assert h_notes.status_code == 200
    res = json.loads(h_notes.wfile.getvalue().decode())
    assert "content" in res
    print("✓ POST /api/notes/generate passed")

    # 6. POST /api/flashcards/generate
    h_fc = MockEduGenieHandler("POST", "/api/flashcards/generate", {
        "topic": "Databases",
        "num_cards": 4
    })
    h_fc.do_POST()
    assert h_fc.status_code == 200
    res = json.loads(h_fc.wfile.getvalue().decode())
    assert "cards" in res
    print("✓ POST /api/flashcards/generate passed")

    # 7. POST /api/roadmap/generate
    h_rm = MockEduGenieHandler("POST", "/api/roadmap/generate", {
        "goal": "Machine Learning Engineer",
        "duration_days": 14,
        "weekly_hours": 10
    })
    h_rm.do_POST()
    assert h_rm.status_code == 200
    res = json.loads(h_rm.wfile.getvalue().decode())
    assert "phases" in res
    print("✓ POST /api/roadmap/generate passed")

    print("All HTTP route handlers verified successfully! 🎉")

if __name__ == "__main__":
    test_handler_endpoints()
