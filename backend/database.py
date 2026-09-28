import sqlite3
import json
import time
from datetime import datetime, date
from .config import DB_PATH

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    with get_db() as conn:
        cursor = conn.cursor()
        
        # Quizzes
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS quizzes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                topic TEXT NOT NULL,
                difficulty TEXT DEFAULT 'intermediate',
                bloom_level TEXT DEFAULT 'all',
                num_questions INTEGER DEFAULT 5,
                content_json TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Quiz Attempts
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS quiz_attempts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                quiz_id INTEGER,
                quiz_title TEXT,
                score INTEGER NOT NULL,
                total_questions INTEGER NOT NULL,
                percentage REAL NOT NULL,
                answers_json TEXT,
                bloom_breakdown_json TEXT,
                time_spent_seconds INTEGER DEFAULT 0,
                attempted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (quiz_id) REFERENCES quizzes(id)
            )
        """)

        # Flashcard Decks
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS flashcard_decks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                topic TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Flashcards (with SM-2 spaced repetition columns)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS flashcards (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                deck_id INTEGER NOT NULL,
                front TEXT NOT NULL,
                back TEXT NOT NULL,
                hint TEXT,
                bloom_level TEXT DEFAULT 'remember',
                repetitions INTEGER DEFAULT 0,
                interval_days INTEGER DEFAULT 1,
                ease_factor REAL DEFAULT 2.5,
                next_review_timestamp REAL DEFAULT 0,
                last_reviewed_at TIMESTAMP,
                FOREIGN KEY (deck_id) REFERENCES flashcard_decks(id) ON DELETE CASCADE
            )
        """)

        # Study Notes
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS study_notes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                topic TEXT NOT NULL,
                format_style TEXT DEFAULT 'comprehensive',
                content_markdown TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Roadmaps
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS roadmaps (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                goal TEXT NOT NULL,
                duration_days INTEGER DEFAULT 14,
                weekly_hours INTEGER DEFAULT 10,
                content_json TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Chat History
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS chat_messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT NOT NULL,
                role TEXT NOT NULL,
                persona TEXT DEFAULT 'socratic',
                content TEXT NOT NULL,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # User Profile & Activity
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_activity (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                activity_type TEXT NOT NULL,
                details_json TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        conn.commit()

# --- Quiz DB Operations ---
def save_quiz(title, topic, difficulty, bloom_level, num_questions, content_dict):
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO quizzes (title, topic, difficulty, bloom_level, num_questions, content_json)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (title, topic, difficulty, bloom_level, num_questions, json.dumps(content_dict)))
        conn.commit()
        return cursor.lastrowid

def get_recent_quizzes(limit=10):
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM quizzes ORDER BY id DESC LIMIT ?", (limit,))
        rows = cursor.fetchall()
        result = []
        for r in rows:
            d = dict(r)
            d["content"] = json.loads(d["content_json"])
            result.append(d)
        return result

def save_quiz_attempt(quiz_id, quiz_title, score, total_questions, answers, bloom_breakdown, time_spent):
    percentage = round((score / max(total_questions, 1)) * 100, 1)
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO quiz_attempts (quiz_id, quiz_title, score, total_questions, percentage, answers_json, bloom_breakdown_json, time_spent_seconds)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            quiz_id,
            quiz_title,
            score,
            total_questions,
            percentage,
            json.dumps(answers),
            json.dumps(bloom_breakdown),
            time_spent
        ))
        conn.commit()
        return cursor.lastrowid

def get_quiz_attempts(limit=20):
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM quiz_attempts ORDER BY id DESC LIMIT ?", (limit,))
        rows = cursor.fetchall()
        result = []
        for r in rows:
            d = dict(r)
            d["answers"] = json.loads(d["answers_json"]) if d["answers_json"] else []
            d["bloom_breakdown"] = json.loads(d["bloom_breakdown_json"]) if d["bloom_breakdown_json"] else {}
            result.append(d)
        return result

# --- Flashcards DB Operations ---
def save_flashcard_deck(title, topic, cards):
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO flashcard_decks (title, topic) VALUES (?, ?)", (title, topic))
        deck_id = cursor.lastrowid

        now = time.time()
        for c in cards:
            cursor.execute("""
                INSERT INTO flashcards (deck_id, front, back, hint, bloom_level, repetitions, interval_days, ease_factor, next_review_timestamp)
                VALUES (?, ?, ?, ?, ?, 0, 1, 2.5, ?)
            """, (deck_id, c.get("front", ""), c.get("back", ""), c.get("hint", ""), c.get("bloom_level", "remember"), now))
        conn.commit()
        return deck_id

def get_flashcard_decks():
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT d.*, COUNT(f.id) as card_count
            FROM flashcard_decks d
            LEFT JOIN flashcards f ON f.deck_id = d.id
            GROUP BY d.id
            ORDER BY d.id DESC
        """)
        return [dict(r) for r in cursor.fetchall()]

def get_deck_cards(deck_id):
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM flashcards WHERE deck_id = ? ORDER BY id ASC", (deck_id,))
        return [dict(r) for r in cursor.fetchall()]

def update_card_spaced_repetition(card_id, quality):
    """
    SuperMemo-2 (SM-2) Spaced Repetition Algorithm
    quality: 0-5 (0=blackout, 3=pass with effort, 5=perfect recall)
    """
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT repetitions, interval_days, ease_factor FROM flashcards WHERE id = ?", (card_id,))
        row = cursor.fetchone()
        if not row:
            return None
        
        reps, interval, ef = row["repetitions"], row["interval_days"], row["ease_factor"]
        
        if quality >= 3:
            if reps == 0:
                interval = 1
            elif reps == 1:
                interval = 6
            else:
                interval = round(interval * ef)
            reps += 1
        else:
            reps = 0
            interval = 1

        # EF formula: EF' = EF + (0.1 - (5 - quality) * (0.08 + (5 - quality) * 0.02))
        ef = ef + (0.1 - (5 - quality) * (0.08 + (5 - quality) * 0.02))
        if ef < 1.3:
            ef = 1.3

        next_review = time.time() + (interval * 86400)
        
        cursor.execute("""
            UPDATE flashcards
            SET repetitions = ?, interval_days = ?, ease_factor = ?, next_review_timestamp = ?, last_reviewed_at = CURRENT_TIMESTAMP
            WHERE id = ?
        """, (reps, interval, round(ef, 2), next_review, card_id))
        conn.commit()
        return {"reps": reps, "repetitions": reps, "interval_days": interval, "ease_factor": round(ef, 2)}

# --- Notes DB Operations ---
def save_notes(title, topic, format_style, content_markdown):
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO study_notes (title, topic, format_style, content_markdown)
            VALUES (?, ?, ?, ?)
        """, (title, topic, format_style, content_markdown))
        conn.commit()
        return cursor.lastrowid

def get_all_notes(limit=20):
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, title, topic, format_style, created_at, SUBSTR(content_markdown, 1, 200) as preview FROM study_notes ORDER BY id DESC LIMIT ?", (limit,))
        return [dict(r) for r in cursor.fetchall()]

def get_note_by_id(note_id):
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM study_notes WHERE id = ?", (note_id,))
        row = cursor.fetchone()
        return dict(row) if row else None

# --- Roadmaps DB Operations ---
def save_roadmap(title, goal, duration_days, weekly_hours, content_dict):
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO roadmaps (title, goal, duration_days, weekly_hours, content_json)
            VALUES (?, ?, ?, ?, ?)
        """, (title, goal, duration_days, weekly_hours, json.dumps(content_dict)))
        conn.commit()
        return cursor.lastrowid

def get_all_roadmaps(limit=10):
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM roadmaps ORDER BY id DESC LIMIT ?", (limit,))
        rows = cursor.fetchall()
        result = []
        for r in rows:
            d = dict(r)
            d["content"] = json.loads(d["content_json"])
            result.append(d)
        return result

# --- Chat Messages DB Operations ---
def save_chat_message(session_id, role, persona, content):
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO chat_messages (session_id, role, persona, content)
            VALUES (?, ?, ?, ?)
        """, (session_id, role, persona, content))
        conn.commit()
        return cursor.lastrowid

def get_chat_history(session_id, limit=30):
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT role, content, persona, timestamp
            FROM chat_messages
            WHERE session_id = ?
            ORDER BY id ASC
            LIMIT ?
        """, (session_id, limit))
        return [dict(r) for r in cursor.fetchall()]

def clear_chat_history(session_id):
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM chat_messages WHERE session_id = ?", (session_id,))
        conn.commit()
        return True

# --- Analytics Computations ---
def compute_analytics():
    with get_db() as conn:
        cursor = conn.cursor()
        
        # Total quizzes & average score
        cursor.execute("SELECT COUNT(*) as total_attempts, AVG(percentage) as avg_score FROM quiz_attempts")
        q_row = cursor.fetchone()
        total_quizzes = q_row["total_attempts"] or 0
        avg_score = round(q_row["avg_score"] or 0.0, 1)

        # Total notes created
        cursor.execute("SELECT COUNT(*) as total_notes FROM study_notes")
        total_notes = cursor.fetchone()["total_notes"] or 0

        # Total flashcards & decks
        cursor.execute("SELECT COUNT(*) as total_cards FROM flashcards")
        total_cards = cursor.fetchone()["total_cards"] or 0
        
        cursor.execute("SELECT COUNT(*) as total_decks FROM flashcard_decks")
        total_decks = cursor.fetchone()["total_decks"] or 0

        # Bloom's Taxonomy Cognitive Mastery calculation across quiz attempts
        bloom_scores = {
            "remember": {"correct": 0, "total": 0},
            "understand": {"correct": 0, "total": 0},
            "apply": {"correct": 0, "total": 0},
            "analyze": {"correct": 0, "total": 0},
            "evaluate": {"correct": 0, "total": 0},
            "create": {"correct": 0, "total": 0}
        }

        cursor.execute("SELECT bloom_breakdown_json FROM quiz_attempts WHERE bloom_breakdown_json IS NOT NULL")
        for row in cursor.fetchall():
            try:
                bd = json.loads(row["bloom_breakdown_json"])
                for lvl, stats in bd.items():
                    if lvl in bloom_scores:
                        bloom_scores[lvl]["correct"] += stats.get("correct", 0)
                        bloom_scores[lvl]["total"] += stats.get("total", 0)
            except Exception:
                pass

        bloom_mastery = {}
        for lvl, stats in bloom_scores.items():
            if stats["total"] > 0:
                pct = round((stats["correct"] / stats["total"]) * 100, 1)
            else:
                pct = 0.0
            bloom_mastery[lvl] = {
                "score_pct": pct,
                "correct": stats["correct"],
                "total": stats["total"]
            }

        # Daily streak calculation
        cursor.execute("SELECT DISTINCT DATE(attempted_at) as attempt_date FROM quiz_attempts ORDER BY attempt_date DESC LIMIT 30")
        dates = [r["attempt_date"] for r in cursor.fetchall()]
        
        streak = 0
        today_str = date.today().isoformat()
        current_check = date.today()
        
        for d_str in dates:
            if d_str == current_check.isoformat():
                streak += 1
                from datetime import timedelta
                current_check -= timedelta(days=1)
            elif streak == 0 and d_str == (date.today() - timedelta(days=1)).isoformat():
                # Yesterday was active
                streak += 1
                current_check = date.today() - timedelta(days=2)
            else:
                break

        return {
            "total_quizzes": total_quizzes,
            "average_score": avg_score,
            "total_notes": total_notes,
            "total_cards": total_cards,
            "total_decks": total_decks,
            "study_streak_days": max(streak, 1 if total_quizzes > 0 else 0),
            "bloom_mastery": bloom_mastery
        }

# Initialize on module load
init_db()
