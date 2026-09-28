# 🎓 EduGenie AI: Google Gemini Powered Learning Assistant

[![Google Gemini](https://img.shields.io/badge/Google_Gemini-3.8_Flash-4285F4?logo=google&logoColor=white)](https://ai.google.dev/)
[![Python](https://img.shields.io/badge/Python-3.9+-3776AB?logo=python&logoColor=white)](https://python.org)
[![Pedagogy](https://img.shields.io/badge/Taxonomy-Bloom's_Revised-10B981)](#-blooms-revised-taxonomy-integration)
[![Zero Dependency](https://img.shields.io/badge/Execution-Zero_External_Dependencies-6366F1)](#-quick-start)

---

## 📺 Project Background & Video Analysis

This repository implements the complete **EduGenie AI** platform based on the project demo video:
- **Video Source**: [https://youtu.be/OKNf89r4D4A?si=ft-Po6Se14Wy63SF](https://youtu.be/OKNf89r4D4A?si=ft-Po6Se14Wy63SF)
- **Title**: *EduGenie: Google Gemini Powered Learning Assistant*
- **Program**: Google Cloud Generative AI track (Skill Wallet / SmartBridge / Naan Mudhalvan)
- **Core Mission**: Transform passive educational content into an adaptive, multimodal, and personalized learning experience using **Google Gemini** and structured pedagogical frameworks (Bloom's Revised Taxonomy).

---

## 🌟 Core Pillars & Feature Suite

```
                                  ┌───────────────────────────┐
                                  │      EduGenie AI Core     │
                                  │  (Powered by Gemini 3.8)  │
                                  └─────────────┬─────────────┘
                                                │
         ┌───────────────────┬──────────────────┼──────────────────┬──────────────────┐
         ▼                   ▼                  ▼                  ▼                  ▼
┌─────────────────┐ ┌─────────────────┐ ┌───────────────┐ ┌─────────────────┐ ┌─────────────────┐
│ 💬 AI Tutor     │ │ 📝 Bloom's Quiz │ │ 📚 Smart      │ │ 🗂️ Flashcards   │ │ 🗺️ Milestone    │
│    Personas &   │ │    Diagnostic   │ │    Notes &    │ │    Spaced       │ │    Study        │
│    Voice Read   │ │    Evaluator    │ │    Summaries  │ │    Repetition   │ │    Roadmaps     │
└─────────────────┘ └─────────────────┘ └───────────────┘ └─────────────────┘ └─────────────────┘
                                                │
                                                ▼
                                 ┌─────────────────────────────┐
                                 │ 📊 Cognitive Mastery Radar  │
                                 │   & Longitudinal Analytics  │
                                 └─────────────────────────────┘
```

### 1. 💬 Multimodal AI Study Tutor
- **4 Pedagogical Personas**:
  - **Socratic Mentor**: Guides students with intuitive leading questions rather than giving immediate answers.
  - **Exam Revision Coach**: Emphasizes high-yield formulas, common misconceptions, and test pitfalls.
  - **Conceptual Storyteller (ELI5)**: Explains advanced topics through accessible real-world analogies.
  - **Academic Scholar**: Provides formal mathematical definitions, proofs, and academic rigor.
- **Auditory Learning (Text-To-Speech)**: Integrated browser speech synthesis for hands-free audio revision.
- **Reference Grounding**: Accepts student notes, textbook excerpts, or code to ground responses.

### 2. 📝 Adaptive Diagnostic Quiz Engine (Bloom's Revised Taxonomy)
Targeted evaluation covering all six cognitive dimensions:
1. **Remembering**: Recall terms, definitions, and foundational facts.
2. **Understanding**: Explain concepts and interpret mechanisms.
3. **Applying**: Calculate, implement, and solve concrete problems.
4. **Analyzing**: Compare, contrast, and decompose complex systems.
5. **Evaluating**: Justify decisions, critique methods, and evaluate trade-offs.
6. **Creating**: Formulate hypotheses and design new solutions.
- **Interactive Exam Mode**: Includes question timers, hint accordions, instant feedback, and question-by-question explanations.

### 3. 📚 Smart High-Retention Notes Generator
- Generates structured study material formatted into:
  - High-level Executive Summary
  - Key Principles & Crisp Definitions
  - Real-World Analogy / Mental Model
  - Step-by-Step Mechanism / Dataflow
  - Mathematical Formulas / Code Blocks
  - Common Misconceptions & Exam Pitfalls
  - 5-Point Test Day Checklist
- **Export Ready**: Copy to clipboard or download as `.md` file.

### 4. 🗂️ Spaced Repetition Flashcards (SuperMemo-2)
- Interactive **3D flip card** animations.
- Implementation of the **SuperMemo-2 (SM-2)** algorithm:
  - Dynamically calculates card ease factors and interval schedules based on student recall ratings (`Again`, `Hard`, `Good`, `Easy`).

### 5. 🗺️ Adaptive Study Roadmap Planner
- Transforms any subject goal into an actionable study curriculum.
- Generates phased milestones, estimated daily minutes, practical checkpoints, capstone challenges, and retention heuristics.

### 6. 📊 Cognitive Analytics Dashboard
- Visualizes mastery across all 6 Bloom's Taxonomy tiers.
- Tracks daily study streaks, average assessment scores, and past attempt logs.

---

## ⚡ Quick Start

### Option A: Zero-Dependency Modern Full-Stack Server (Recommended)
EduGenie runs out-of-the-box using the Python standard library with **zero external pip dependencies**:

```bash
# 1. Navigate to project directory
cd edugenie-ai

# 2. Start the web application
python3 server.py 8080
# or: ./run.sh server

# 3. Open in your browser:
# http://localhost:8080
```

> [!TIP]
> EduGenie includes a built-in educational intelligence engine that enables full testing offline. To activate live Google Gemini 3.8 Flash, simply enter your `GEMINI_API_KEY` in the top right key modal or in your `.env` file!

---

### Option B: Streamlit Web App
For users and evaluators who prefer the classic Streamlit student dashboard:

```bash
# 1. Install optional requirements
pip install -r requirements.txt

# 2. Launch Streamlit
streamlit run app.py
# or: ./run.sh streamlit
```

---

### Option C: Run Automated Tests

```bash
./run.sh test
# or: python3 tests/test_services.py && python3 tests/test_server.py
```

---

## 📁 Repository Structure

```
edugenie-ai/
├── app.py                      # Streamlit application
├── server.py                   # Lightweight zero-dependency HTTP server
├── run.sh                      # Unified execution script (server / streamlit / test)
├── requirements.txt            # Python dependencies (google-genai, streamlit, pypdf)
├── .env.example                # Sample environment variables
├── README.md                   # Complete documentation
├── backend/
│   ├── config.py               # Settings, Bloom's levels, personas
│   ├── gemini_client.py        # Gemini client + educational fallback engine
│   ├── prompts.py              # Prompt engineering templates
│   ├── database.py             # SQLite persistence (quizzes, SM-2 flashcards, notes)
│   └── services/
│       ├── tutor_service.py    # AI Tutor multi-turn chat & personas
│       ├── quiz_service.py     # Bloom's quiz generator & evaluator
│       ├── notes_service.py    # Smart notes & cheatsheet generator
│       ├── flashcard_service.py# Flashcard generator & SM-2 algorithm
│       ├── roadmap_service.py  # Study planner & roadmap generator
│       ├── pdf_service.py      # PDF & document text extractor
│       └── analytics_service.py# Cognitive mastery radar & streak analytics
├── frontend/
│   ├── index.html              # Modern responsive Single Page Application
│   ├── css/
│   │   └── styles.css          # Glassmorphism theme, 3D flip card styles
│   └── js/
│       ├── app.js              # State management & modal logic
│       ├── tutor.js            # Chat UI & Speech Synthesis (TTS)
│       ├── quiz.js             # Interactive quiz runner & scoring
│       ├── notes.js            # Notes generator & markdown exporter
│       ├── flashcards.js       # 3D flashcard viewer & SM-2 rating
│       ├── roadmap.js          # Timeline roadmap visualizer
│       └── analytics.js        # Cognitive mastery progress & charts
├── sample_data/
│   ├── sample_physics_notes.txt
│   └── sample_cs_syllabus.txt
└── tests/
    ├── test_services.py        # Service unit tests
    └── test_server.py          # HTTP route handler tests
```

---

## 🔑 Environment Configuration

Create a `.env` file in the project root:

```bash
# Google AI Studio API Key (https://aistudio.google.com/)
GEMINI_API_KEY=your_gemini_api_key_here

# Recommended Gemini Model
GEMINI_MODEL=gemini-3.8-flash

# Port (Default: 8080)
PORT=8080
```

---

## 🧠 Bloom's Revised Taxonomy Integration

| Level | Cognitive Objective | Target Verbs in EduGenie |
| :--- | :--- | :--- |
| **1. Remembering** | Recalling facts, terms, and basic concepts | Define, Identify, List, Name, Recall |
| **2. Understanding** | Explaining ideas, concepts, and relationships | Explain, Summarize, Interpret, Classify |
| **3. Applying** | Using learned information to solve novel problems | Apply, Solve, Calculate, Implement |
| **4. Analyzing** | Deconstructing systems and comparing approaches | Analyze, Compare, Contrast, Decompose |
| **5. Evaluating** | Justifying decisions and critiquing trade-offs | Evaluate, Critique, Judge, Justify |
| **6. Creating** | Formulating original hypotheses and designing architectures | Design, Create, Construct, Synthesize |

---

## 📡 REST API Reference

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/api/status` | Server health, active Gemini model & key status |
| `POST` | `/api/config/key` | Update Gemini API key dynamically |
| `POST` | `/api/tutor/chat` | Send message to AI Tutor with selected persona |
| `POST` | `/api/quiz/generate` | Generate adaptive quiz by topic and Bloom's level |
| `POST` | `/api/quiz/submit` | Grade assessment and compute cognitive breakdown |
| `GET` | `/api/quiz/history` | Retrieve past assessment attempts |
| `POST` | `/api/notes/generate` | Generate structured study notes and checklists |
| `POST` | `/api/flashcards/generate` | Generate flashcard deck |
| `POST` | `/api/flashcards/review` | Update card recall interval using SuperMemo-2 (SM-2) |
| `POST` | `/api/roadmap/generate` | Generate personalized study timeline and milestones |
| `GET` | `/api/analytics` | Retrieve Bloom's mastery radar data & streak |

---

## 📜 License
Developed for educational research and AI learning. Released under the MIT License.
