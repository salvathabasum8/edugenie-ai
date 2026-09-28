import json
from .config import BLOOMS_LEVELS, TUTOR_PERSONAS

def get_tutor_system_prompt(persona_key="socratic"):
    persona = TUTOR_PERSONAS.get(persona_key, TUTOR_PERSONAS["socratic"])
    return f"""You are EduGenie, an advanced AI Learning Assistant powered by Google Gemini.
Your Persona: {persona['name']}
Style Instruction: {persona['system_instruction']}

Core Guidelines:
1. Always be supportive, pedagogically sound, and engaging.
2. Structure your answers with clear headings, bullet points, and code/math blocks where appropriate.
3. Use LaTeX formatting for mathematical expressions: inline $...$ and display $$...$$.
4. Whenever explaining a difficult concept, connect it to an intuitive real-world analogy.
5. End your response with a quick 'Quick Check Question' or reflection prompt to verify student understanding.
"""

def get_quiz_prompt(topic, difficulty="intermediate", bloom_level="all", num_questions=5, context_text=None):
    bloom_instruction = ""
    if bloom_level in BLOOMS_LEVELS:
        lvl = BLOOMS_LEVELS[bloom_level]
        bloom_instruction = f"Target specifically Bloom's Taxonomy Level: {lvl['name']} ({lvl['description']}). Questions should use action verbs like {', '.join(lvl['verbs'])}."
    else:
        bloom_instruction = "Distribute the questions across Bloom's Revised Taxonomy levels (Remembering, Understanding, Applying, Analyzing, Evaluating, Creating) to evaluate balanced cognitive mastery."

    context_block = ""
    if context_text and context_text.strip():
        context_block = f"""
Source Study Material / Reference Context:
\"\"\"
{context_text.strip()[:4000]}
\"\"\"
Generate questions primarily based on the reference context above.
"""

    return f"""You are EduGenie's Adaptive Assessment Engine.
Create a structured diagnostic quiz on the topic: "{topic}".
Difficulty: {difficulty}
Number of questions: {num_questions}
Cognitive Targeting: {bloom_instruction}
{context_block}

CRITICAL: Return ONLY valid JSON format matching this exact schema (no markdown fences, no surrounding commentary):
{{
  "title": "{topic} Quiz",
  "topic": "{topic}",
  "difficulty": "{difficulty}",
  "bloom_level_focus": "{bloom_level}",
  "questions": [
    {{
      "id": 1,
      "question": "Clear, challenging question prompt",
      "options": ["Option A text", "Option B text", "Option C text", "Option D text"],
      "correct_index": 0,
      "bloom_level": "remember|understand|apply|analyze|evaluate|create",
      "bloom_name": "Remembering|Understanding|Applying|Analyzing|Evaluating|Creating",
      "explanation": "Detailed pedagogical explanation of why this answer is correct and why other options are incorrect.",
      "hint": "Subtle hint without revealing the direct answer"
    }}
  ]
}}
"""

def get_notes_prompt(topic, format_style="comprehensive", context_text=None):
    context_block = ""
    if context_text and context_text.strip():
        context_block = f"""
Source Document Content:
\"\"\"
{context_text.strip()[:5000]}
\"\"\"
Synthesize the study notes based on the provided material.
"""

    return f"""You are EduGenie's Smart Study Notes Generator.
Create high-retention study notes for: "{topic}".
Format Style: {format_style}
{context_block}

Format the response using clean Markdown with the following structured sections:
1. # 🎓 {topic}: Core Summary (High-level overview in 3-4 sentences)
2. ## 💡 Key Concepts & Definitions (Bullet points with bold terms and crisp explanations)
3. ## 🔍 Real-World Analogy / Mental Model (How to intuitively visualize this)
4. ## ⚙️ Step-by-Step Breakdown / Architecture / Mechanism (Structured breakdown, diagrams in ASCII or bullet flows)
5. ## 📐 Formulae / Code Snippets / Theorems (If applicable, with clear variable definitions)
6. ## ⚠️ Common Misconceptions & Exam Pitfalls (What students usually get wrong)
7. ## 📝 Quick Review Checklist (5 bullet points every student must know before test day)
"""

def get_flashcards_prompt(topic, num_cards=8, context_text=None):
    context_block = ""
    if context_text and context_text.strip():
        context_block = f"""
Context:
\"\"\"
{context_text.strip()[:4000]}
\"\"\"
"""
    return f"""You are EduGenie's Spaced Repetition Flashcard Generator.
Generate {num_cards} high-impact flashcards for: "{topic}".
{context_block}

CRITICAL: Return ONLY valid JSON matching this schema:
{{
  "deck_title": "{topic} Mastery Deck",
  "topic": "{topic}",
  "cards": [
    {{
      "id": 1,
      "front": "Front question / prompt or concept to test",
      "back": "Back answer / concise explanation / key fact",
      "hint": "Memory trigger hint or mnemonic",
      "bloom_level": "remember|understand|apply|analyze"
    }}
  ]
}}
"""

def get_roadmap_prompt(goal, duration_days=14, weekly_hours=10):
    return f"""You are EduGenie's Adaptive Learning Planner.
Create a personalized, milestone-driven study roadmap for:
Goal / Exam / Subject: "{goal}"
Available Timeline: {duration_days} days
Estimated Study Time: {weekly_hours} hours per week

CRITICAL: Return ONLY valid JSON matching this exact schema:
{{
  "title": "{goal} Learning Roadmap",
  "goal": "{goal}",
  "duration_days": {duration_days},
  "weekly_hours": {weekly_hours},
  "phases": [
    {{
      "phase_number": 1,
      "phase_name": "Phase Name (e.g. Foundations & Core Mechanics)",
      "days_range": "Days 1-4",
      "key_objectives": ["Objective 1", "Objective 2"],
      "daily_milestones": [
        {{
          "day": 1,
          "task": "Specific actionable learning task",
          "checkpoint": "Practical milestone check",
          "estimated_minutes": 90
        }}
      ]
    }}
  ],
  "capstone_challenge": "A culminating practical project or mock exam to prove mastery",
  "expert_tips": ["Tip 1", "Tip 2"]
}}
"""
