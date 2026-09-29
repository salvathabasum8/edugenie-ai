import os
from pathlib import Path

# Base paths
BASE_DIR = Path(__file__).resolve().parent.parent
FRONTEND_DIR = BASE_DIR / "frontend"
DATA_DIR = BASE_DIR / "sample_data"
DB_PATH = BASE_DIR / "edugenie.db"

# Automatically load .env if present
env_path = BASE_DIR / ".env"
if env_path.exists():
    try:
        for line in env_path.read_text().splitlines():
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                k = k.strip()
                v = v.strip().strip('"').strip("'")
                if k and k not in os.environ:
                    os.environ[k] = v
    except Exception:
        pass

# Server configuration
DEFAULT_PORT = int(os.environ.get("PORT", 8085))
DEFAULT_HOST = os.environ.get("HOST", "0.0.0.0")

# Google Gemini API configuration
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")
DEFAULT_MODEL = os.environ.get("GEMINI_MODEL", "gemini-3.5-flash-lite")
FALLBACK_MODELS = [
    "gemini-3.5-flash-lite",
    "gemini-3.1-flash-lite",
    "gemini-3.8-flash",
    "gemini-flash-latest",
    "gemini-pro-latest"
]

# Bloom's Revised Taxonomy levels
BLOOMS_LEVELS = {
    "remember": {
        "name": "Remembering",
        "description": "Recalling facts, terms, basic concepts, and definitions",
        "verbs": ["define", "identify", "list", "name", "recall", "state"],
        "color": "#3B82F6"  # Blue
    },
    "understand": {
        "name": "Understanding",
        "description": "Explaining ideas or concepts, summarizing, interpreting",
        "verbs": ["explain", "summarize", "describe", "interpret", "classify"],
        "color": "#10B981"  # Emerald
    },
    "apply": {
        "name": "Applying",
        "description": "Using learned information in new situations and solving problems",
        "verbs": ["apply", "solve", "calculate", "demonstrate", "implement"],
        "color": "#F59E0B"  # Amber
    },
    "analyze": {
        "name": "Analyzing",
        "description": "Drawing connections among ideas, differentiating, decomposing",
        "verbs": ["analyze", "compare", "contrast", "distinguish", "examine"],
        "color": "#8B5CF6"  # Purple
    },
    "evaluate": {
        "name": "Evaluating",
        "description": "Justifying a stand or decision, critiquing, assessing evidence",
        "verbs": ["evaluate", "judge", "critique", "justify", "defend"],
        "color": "#EC4899"  # Pink
    },
    "create": {
        "name": "Creating",
        "description": "Producing new or original work, formulating, designing solutions",
        "verbs": ["create", "design", "formulate", "construct", "synthesize"],
        "color": "#EF4444"  # Red
    }
}

# Tutor personas
TUTOR_PERSONAS = {
    "socratic": {
        "name": "Socratic Mentor",
        "tagline": "Guides through thoughtful questions & intuition",
        "system_instruction": "You are a Socratic tutor. Instead of immediately giving away answers, you guide the student with thoughtful leading questions, intuitive real-world analogies, and step-by-step reasoning."
    },
    "exam_coach": {
        "name": "Exam Revision Coach",
        "tagline": "High-yield formulas, tips, & exam traps",
        "system_instruction": "You are an intense and encouraging exam preparation coach. Focus on high-yield concepts, common student mistakes, exam traps, time-saving heuristics, and concise revision summaries."
    },
    "eli5": {
        "name": "Conceptual Storyteller (ELI5)",
        "tagline": "Explains complex ideas in simple, fun analogies",
        "system_instruction": "You explain complex concepts using simple everyday analogies, visual thought experiments, and zero jargon. Suitable for complete beginners."
    },
    "academic": {
        "name": "Academic Scholar",
        "tagline": "Rigorous definitions, math proofs, & citations",
        "system_instruction": "You are a university professor. Provide mathematically rigorous explanations, formal definitions, proofs, structured theorems, and academic depth."
    }
}
