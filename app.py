"""
EduGenie: Google Gemini Powered Learning Assistant
Streamlit Application
"""

import os
import json
import streamlit as st
from backend.config import BLOOMS_LEVELS, TUTOR_PERSONAS, DEFAULT_MODEL
from backend.gemini_client import gemini_client
from backend.services import (
    TutorService,
    QuizService,
    NotesService,
    FlashcardService,
    RoadmapService,
    AnalyticsService
)

st.set_page_config(
    page_title="EduGenie: Google Gemini Learning Assistant",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.2rem;
        font-weight: 800;
        background: linear-gradient(135deg, #4F46E5 0%, #7C3AED 50%, #EC4899 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.2rem;
    }
    .sub-header {
        font-size: 1.05rem;
        color: #64748B;
        margin-bottom: 1.5rem;
    }
    .metric-card {
        background-color: #F8FAFC;
        border: 1px solid #E2E8F0;
        border-radius: 12px;
        padding: 16px;
        text-align: center;
    }
    .bloom-pill {
        display: inline-block;
        padding: 4px 10px;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 600;
        color: white;
    }
</style>
""", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.markdown("## ⚙️ Configuration")
    api_key_input = st.text_input(
        "Google Gemini API Key",
        value=os.environ.get("GEMINI_API_KEY", ""),
        type="password",
        help="Enter your Google AI Studio API Key. If empty, local educational simulation mode is used."
    )
    if api_key_input:
        gemini_client.set_api_key(api_key_input)
        st.success("API Key Active! 🟢")
    else:
        st.info("Demo / Educational Offline Mode 🟡")

    st.markdown("---")
    st.markdown("### 🧠 Bloom's Taxonomy Guide")
    for key, info in BLOOMS_LEVELS.items():
        st.markdown(f"<span style='color:{info['color']}; font-weight:bold;'>● {info['name']}</span>: {info['description']}", unsafe_allow_html=True)

    st.markdown("---")
    st.caption("EduGenie AI v2.5 • Google Cloud Generative AI")

# Main Header
st.markdown('<div class="main-header">🎓 EduGenie: Learning Assistant</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Google Gemini Powered Adaptive Learning • Bloom\'s Taxonomy Diagnostics • Smart Notes & Flashcards</div>', unsafe_allow_html=True)

# Tabs
tab_tutor, tab_quiz, tab_notes, tab_flashcards, tab_roadmap, tab_analytics = st.tabs([
    "💬 AI Tutor",
    "📝 Adaptive Quiz",
    "📚 Smart Notes",
    "🗂️ Flashcards (SM-2)",
    "🗺️ Study Roadmap",
    "📊 Cognitive Analytics"
])

# ----------------- TAB 1: AI TUTOR -----------------
with tab_tutor:
    st.markdown("### 💬 Interactive AI Study Tutor")
    col1, col2 = st.columns([1, 3])
    with col1:
        persona_choice = st.selectbox(
            "Tutor Persona",
            options=list(TUTOR_PERSONAS.keys()),
            format_func=lambda k: f"{TUTOR_PERSONAS[k]['name']}"
        )
        st.caption(TUTOR_PERSONAS[persona_choice]["tagline"])
        study_context = st.text_area("Optional Study Material / Context", placeholder="Paste excerpts from notes, code, or textbook...", height=120)

    with col2:
        if "messages" not in st.session_state:
            st.session_state.messages = []

        for msg in st.session_state.messages:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])

        if prompt := st.chat_input("Ask a doubt, request a step-by-step derivation, or explore a concept..."):
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)

            with st.chat_message("assistant"):
                with st.spinner("EduGenie is thinking..."):
                    res = TutorService.chat("streamlit_session", prompt, persona=persona_choice, context_text=study_context)
                    reply = res["response"]
                    st.markdown(reply)
                    st.session_state.messages.append({"role": "assistant", "content": reply})

# ----------------- TAB 2: ADAPTIVE QUIZ -----------------
with tab_quiz:
    st.markdown("### 📝 Adaptive Assessment Engine (Bloom's Revised Taxonomy)")
    
    col_q1, col_q2, col_q3, col_q4 = st.columns(4)
    with col_q1:
        quiz_topic = st.text_input("Quiz Subject / Topic", value="Artificial Intelligence Fundamentals")
    with col_q2:
        quiz_diff = st.selectbox("Difficulty", ["beginner", "intermediate", "advanced"])
    with col_q3:
        quiz_bloom = st.selectbox("Cognitive Target", ["all"] + list(BLOOMS_LEVELS.keys()), format_func=lambda k: "All Bloom Levels" if k == "all" else BLOOMS_LEVELS[k]["name"])
    with col_q4:
        quiz_num = st.slider("Number of Questions", 3, 10, 5)

    if st.button("🚀 Generate Adaptive Quiz", use_container_width=True):
        with st.spinner("Formulating questions mapped to cognitive taxonomy..."):
            quiz_data = QuizService.generate_quiz(quiz_topic, quiz_diff, quiz_bloom, quiz_num)
            st.session_state.current_quiz = quiz_data
            st.session_state.user_answers = {}
            st.session_state.quiz_submitted = False

    if "current_quiz" in st.session_state and st.session_state.current_quiz:
        q_data = st.session_state.current_quiz
        st.markdown(f"#### 📋 {q_data.get('title', 'Diagnostic Quiz')}")
        
        with st.form("quiz_form"):
            for q in q_data.get("questions", []):
                q_id = q["id"]
                bloom_info = BLOOMS_LEVELS.get(q.get("bloom_level", "understand"), {})
                st.markdown(f"**Q{q_id}. {q['question']}** <span style='background-color:{bloom_info.get('color', '#6366F1')}; color:white; padding:2px 8px; border-radius:12px; font-size:0.75rem;'>{bloom_info.get('name', 'Cognitive')}</span>", unsafe_allow_html=True)
                
                selected = st.radio(
                    f"Select answer for Q{q_id}",
                    options=range(len(q["options"])),
                    format_func=lambda idx, opts=q["options"]: opts[idx],
                    key=f"radio_q_{q_id}"
                )
                st.session_state.user_answers[str(q_id)] = selected
                st.markdown("---")

            submitted = st.form_submit_button("Submit Assessment & Grade")
            if submitted:
                st.session_state.quiz_submitted = True

        if st.session_state.get("quiz_submitted"):
            eval_res = QuizService.evaluate_quiz(
                q_data.get("quiz_id", 1),
                q_data.get("title", "Assessment"),
                q_data.get("questions", []),
                st.session_state.user_answers
            )
            st.success(f"### 🎉 Assessment Completed! Score: {eval_res['score']} / {eval_res['total_questions']} ({eval_res['percentage']}%)")
            
            # Bloom's Breakdown
            st.markdown("#### 🧠 Cognitive Level Performance Breakdown:")
            cols = st.columns(6)
            for idx, (b_key, b_info) in enumerate(BLOOMS_LEVELS.items()):
                b_stat = eval_res["bloom_breakdown"].get(b_key, {"correct": 0, "total": 0})
                with cols[idx]:
                    st.metric(b_info["name"], f"{b_stat['correct']}/{b_stat['total']}")

            st.markdown("#### 💡 Question-by-Question Review:")
            for item in eval_res["detailed_results"]:
                status_icon = "✅" if item["is_correct"] else "❌"
                with st.expander(f"{status_icon} Q{item['id']}: {item['question']}"):
                    st.write(f"**Your Choice**: {item['options'][item['user_selected']] if item['user_selected'] is not None else 'None'}")
                    st.write(f"**Correct Choice**: {item['options'][item['correct_index']]}")
                    st.info(f"**Pedagogical Explanation**: {item['explanation']}")

# ----------------- TAB 3: SMART NOTES -----------------
with tab_notes:
    st.markdown("### 📚 Smart Study Notes & Summary Generator")
    n_col1, n_col2 = st.columns([1, 2])
    with n_col1:
        notes_topic = st.text_input("Subject / Chapter", value="Transformer Architecture & Self-Attention")
        notes_style = st.selectbox("Style", ["comprehensive", "quick_revision", "cheatsheet", "formula_sheet"])
        notes_source = st.text_area("Optional Source Text or Syllabus Excerpt", height=150)
        gen_notes_btn = st.button("Generate Structured Notes", use_container_width=True)

    with n_col2:
        if gen_notes_btn:
            with st.spinner("Synthesizing high-retention study notes..."):
                res_notes = NotesService.generate_notes(notes_topic, notes_style, context_text=notes_source)
                st.session_state.active_notes = res_notes

        if "active_notes" in st.session_state:
            st.markdown(st.session_state.active_notes["content"])
            st.download_button(
                "📥 Download Markdown Notes",
                data=st.session_state.active_notes["content"],
                file_name=f"{notes_topic.replace(' ', '_')}_notes.md",
                mime="text/markdown"
            )

# ----------------- TAB 4: FLASHCARDS -----------------
with tab_flashcards:
    st.markdown("### 🗂️ Active Recall & Spaced Repetition Flashcards (SuperMemo-2)")
    f_col1, f_col2 = st.columns([1, 3])
    with f_col1:
        fc_topic = st.text_input("Flashcard Topic", value="Data Structures & Algorithms")
        fc_count = st.slider("Card Count", 4, 12, 6)
        if st.button("Generate Deck", use_container_width=True):
            with st.spinner("Generating flashcards..."):
                deck = FlashcardService.generate_deck(fc_topic, fc_count)
                st.session_state.active_deck = deck
                st.session_state.card_idx = 0

    with f_col2:
        if "active_deck" in st.session_state and st.session_state.active_deck:
            cards = st.session_state.active_deck.get("cards", [])
            idx = st.session_state.get("card_idx", 0)
            if cards and idx < len(cards):
                card = cards[idx]
                st.markdown(f"#### Card {idx+1} of {len(cards)}")
                
                # Card container
                with st.container():
                    st.info(f"**Front:**\n### {card['front']}")
                    
                    show_ans = st.checkbox("Reveal Answer", key=f"ans_reveal_{idx}")
                    if show_ans:
                        st.success(f"**Back:**\n{card['back']}")
                        if card.get("hint"):
                            st.caption(f"💡 Hint: {card['hint']}")
                        
                        st.markdown("**Rate your recall ease (SM-2 Interval Adjustment):**")
                        c1, c2, c3, c4 = st.columns(4)
                        with c1:
                            if st.button("Again (Hard)", key="b_hard"):
                                FlashcardService.review_card(card["id"], 1)
                                st.session_state.card_idx = (idx + 1) % len(cards)
                                st.rerun()
                        with c2:
                            if st.button("Good", key="b_good"):
                                FlashcardService.review_card(card["id"], 3)
                                st.session_state.card_idx = (idx + 1) % len(cards)
                                st.rerun()
                        with c3:
                            if st.button("Easy", key="b_easy"):
                                FlashcardService.review_card(card["id"], 5)
                                st.session_state.card_idx = (idx + 1) % len(cards)
                                st.rerun()
                        with c4:
                            if st.button("Skip Next ➡️", key="b_skip"):
                                st.session_state.card_idx = (idx + 1) % len(cards)
                                st.rerun()

# ----------------- TAB 5: STUDY ROADMAP -----------------
with tab_roadmap:
    st.markdown("### 🗺️ Adaptive Milestone Study Planner")
    r_col1, r_col2 = st.columns([1, 2])
    with r_col1:
        rm_goal = st.text_input("Exam or Subject Goal", value="Pass Google Cloud Generative AI Certification")
        rm_days = st.slider("Preparation Window (Days)", 7, 60, 14)
        rm_hours = st.slider("Weekly Hours", 4, 30, 10)
        if st.button("Generate Roadmap", use_container_width=True):
            with st.spinner("Architecting personalized curriculum roadmap..."):
                rm_data = RoadmapService.generate_roadmap(rm_goal, rm_days, rm_hours)
                st.session_state.active_roadmap = rm_data

    with r_col2:
        if "active_roadmap" in st.session_state and st.session_state.active_roadmap:
            rm = st.session_state.active_roadmap
            st.markdown(f"#### 🎯 {rm.get('title')}")
            st.caption(f"Timeline: {rm.get('duration_days')} Days • Weekly Commitment: {rm.get('weekly_hours')} Hours")
            
            for phase in rm.get("phases", []):
                st.markdown(f"### 📍 {phase.get('phase_name')} ({phase.get('days_range')})")
                for obj in phase.get("key_objectives", []):
                    st.markdown(f"- 🎯 {obj}")
                for m in phase.get("daily_milestones", []):
                    st.markdown(f"**Day {m['day']}**: {m['task']} *(Checkpoint: {m['checkpoint']} - {m['estimated_minutes']}m)*")
                st.markdown("---")

            if rm.get("capstone_challenge"):
                st.warning(f"🏆 **Capstone Challenge**: {rm['capstone_challenge']}")

# ----------------- TAB 6: COGNITIVE ANALYTICS -----------------
with tab_analytics:
    st.markdown("### 📊 Learning Analytics & Bloom's Cognitive Mastery")
    analytics = AnalyticsService.get_dashboard_metrics()
    
    m1, m2, m3, m4 = st.columns(4)
    with m1:
        st.metric("Total Quizzes Attempted", analytics["total_quizzes"])
    with m2:
        st.metric("Average Score", f"{analytics['average_score']}%")
    with m3:
        st.metric("Study Streak", f"{analytics['study_streak_days']} Days 🔥")
    with m4:
        st.metric("Flashcards Mastered", analytics["total_cards"])

    st.markdown("#### 🧠 Bloom's Taxonomy Cognitive Mastery Radar")
    b_cols = st.columns(6)
    for idx, item in enumerate(analytics["bloom_details"]):
        with b_cols[idx]:
            st.markdown(f"""
            <div style="background-color:#F8FAFC; border: 1px solid #E2E8F0; border-radius:10px; padding:12px; text-align:center;">
                <div style="color:{item['color']}; font-weight:700; font-size:0.9rem;">{item['name']}</div>
                <div style="font-size:1.4rem; font-weight:800; margin:6px 0;">{item['score_pct']}%</div>
                <div style="font-size:0.75rem; color:#64748B;">{item['correct']}/{item['total']} correct</div>
                <div style="font-size:0.75rem; font-weight:600; color:{'#10B981' if item['status']=='Mastered' else '#64748B'}">{item['status']}</div>
            </div>
            """, unsafe_allow_html=True)
