import json
from .config import BLOOMS_LEVELS, TUTOR_PERSONAS

def get_tutor_system_prompt(persona_key="socratic"):
    persona = TUTOR_PERSONAS.get(persona_key, TUTOR_PERSONAS["socratic"])
    return f"""You are EduGenie, an advanced AI Learning Assistant powered by Google Gemini.
Your Persona: {persona['name']}
Persona Focus: {persona['system_instruction']}

CRITICAL TEACHING GUIDELINES:
1. DIRECT & EXACT ACCURACY: Always answer the student's question directly, clearly, and completely. Never dodge, answer in vague riddles, or withhold the correct answer.
2. TECHNICAL & MATHEMATICAL DEPTH:
   - For mathematical, algorithmic, or scientific questions, provide the exact mathematical formula ($...$ inline, $$...$$ display) and step-by-step update rules.
   - For coding/debugging, provide working code snippets and explain exactly why the error occurs and how to fix it.
   - For exam questions, provide a model answer with mark allocations and common traps.
3. STRUCTURE & PEDAGOGY:
   - Use structured Markdown with bold terms and clear sections.
   - Connect difficult mechanisms to an intuitive mental model or real-world analogy.
   - End with a single crisp 'Quick Recall Question' to test retention.
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
    p1_end = max(2, duration_days // 3)
    p2_end = max(p1_end + 1, (2 * duration_days) // 3)
    return f"""You are EduGenie's Fast Adaptive Learning Planner.
Generate a structured, high-impact 3-phase study roadmap for: "{goal}".
Timeline: {duration_days} days | Pacing: {weekly_hours} hrs/week.

Keep milestones focused and concise so the plan generates rapidly.
CRITICAL: Return ONLY valid JSON matching this schema:
{{
  "title": "{goal} Mastery Roadmap",
  "goal": "{goal}",
  "duration_days": {duration_days},
  "weekly_hours": {weekly_hours},
  "phases": [
    {{
      "phase_number": 1,
      "phase_name": "Phase 1: Foundations & Core Mechanics",
      "days_range": "Days 1-{p1_end}",
      "key_objectives": ["Grasp fundamental principles", "Master core terminology & mental models"],
      "daily_milestones": [
        {{"day": 1, "task": "Core concepts deep-dive & terminology", "checkpoint": "Concept recall verification", "estimated_minutes": 60}},
        {{"day": {p1_end}, "task": "Foundational exercises and problem drills", "checkpoint": "Solve 3 standard problems", "estimated_minutes": 60}}
      ]
    }},
    {{
      "phase_number": 2,
      "phase_name": "Phase 2: Applied Practice & Problem Solving",
      "days_range": "Days {p1_end + 1}-{p2_end}",
      "key_objectives": ["Apply concepts to practical scenarios", "Deconstruct edge cases & traps"],
      "daily_milestones": [
        {{"day": {p1_end + 1}, "task": "Implement and analyze key algorithms/mechanisms", "checkpoint": "Working prototype/solution", "estimated_minutes": 75}},
        {{"day": {p2_end}, "task": "High-yield exam traps and diagnostic drills", "checkpoint": "Score >= 80% on practice quiz", "estimated_minutes": 60}}
      ]
    }},
    {{
      "phase_number": 3,
      "phase_name": "Phase 3: Synthesis, Mock Testing & Mastery",
      "days_range": "Days {p2_end + 1}-{duration_days}",
      "key_objectives": ["Full exam/project readiness", "Comprehensive recall review"],
      "daily_milestones": [
        {{"day": {p2_end + 1}, "task": "Full-length timed assessment or capstone build", "checkpoint": "Complete capstone challenge", "estimated_minutes": 90}},
        {{"day": {duration_days}, "task": "Spaced repetition review of high-yield weak areas", "checkpoint": "Ready for test day", "estimated_minutes": 45}}
      ]
    }}
  ],
  "capstone_challenge": "Build a practical synthesis artifact or score 90%+ on full mock exam in {goal}.",
  "expert_tips": ["Use active recall rather than passive re-reading", "Explain core mechanisms aloud using Feynman technique"]
}}
"""
