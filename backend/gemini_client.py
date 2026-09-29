import os
import json
import re
import urllib.request
import urllib.error
from .config import GEMINI_API_KEY, DEFAULT_MODEL, FALLBACK_MODELS

class GeminiClient:
    def __init__(self, api_key=None, model=None):
        self.api_key = api_key or os.environ.get("GEMINI_API_KEY", "")
        self.model = model or os.environ.get("GEMINI_MODEL", DEFAULT_MODEL)
        self.sdk_available = False
        self.last_call_live = False
        self.last_error = None
        
        # Check if google-genai is installed
        try:
            from google import genai
            self.genai_sdk = genai
            self.sdk_available = True
        except ImportError:
            self.genai_sdk = None

    def set_api_key(self, key):
        self.api_key = key.strip() if key else ""
        os.environ["GEMINI_API_KEY"] = self.api_key
        self.last_error = None

    def has_api_key(self):
        return bool(self.api_key and len(self.api_key) > 5)

    def generate_text(self, prompt, system_instruction=None, temperature=0.7, user_question=None, persona="socratic"):
        """Generates text from Gemini, falling back to offline educational simulator if no key or error."""
        self.last_call_live = False
        self.last_error = None

        if self.has_api_key():
            models_to_try = [self.model] + [m for m in FALLBACK_MODELS if m != self.model]

            # 1. Try google-genai SDK if available
            if self.sdk_available:
                try:
                    client = self.genai_sdk.Client(api_key=self.api_key)
                    config = {}
                    if system_instruction:
                        config["system_instruction"] = system_instruction
                    if temperature is not None:
                        config["temperature"] = temperature
                        
                    for model_name in models_to_try:
                        try:
                            response = client.models.generate_content(
                                model=model_name,
                                contents=prompt,
                                config=config if config else None
                            )
                            if hasattr(response, "text") and response.text:
                                self.model = model_name
                                self.last_call_live = True
                                return response.text
                        except Exception as m_err:
                            self.last_error = str(m_err)
                            continue
                except Exception as sdk_err:
                    self.last_error = str(sdk_err)

            # 2. Direct HTTP REST API via urllib
            try:
                text = self._call_rest_api(prompt, system_instruction, temperature)
                self.last_call_live = True
                return text
            except Exception as e:
                self.last_error = str(e)
                print(f"[GeminiClient] API error: {e}. Falling back to internal educational intelligence.")
        
        # If no API key or API call failed, use internal educational engine
        return self._fallback_generate(prompt, system_instruction, user_question=user_question, persona=persona)

    def generate_json(self, prompt, system_instruction=None):
        """Generates structured JSON with schema extraction & robust regex cleaning."""
        raw_text = self.generate_text(prompt, system_instruction=system_instruction, temperature=0.3)
        return self.extract_json(raw_text)

    def extract_json(self, text):
        """Extracts and parses JSON from text, handling markdown fences and messy LLM output."""
        if not text:
            return {}
        
        # Strip markdown fences if present
        cleaned = text.strip()
        cleaned = re.sub(r"^```(?:json)?\s*", "", cleaned, flags=re.MULTILINE)
        cleaned = re.sub(r"\s*```$", "", cleaned, flags=re.MULTILINE)
        cleaned = cleaned.strip()

        # Try direct parse
        try:
            return json.loads(cleaned)
        except Exception:
            pass

        # Try finding JSON object or array with regex
        match = re.search(r"(\{[\s\S]*\}|\[[\s\S]*\])", cleaned)
        if match:
            try:
                return json.loads(match.group(1))
            except Exception:
                pass
        
        return {"error": "Failed to parse JSON", "raw_content": text}

    def _call_rest_api(self, prompt, system_instruction=None, temperature=0.7):
        """Calls Gemini REST API via standard urllib."""
        models_to_try = [self.model] + [m for m in FALLBACK_MODELS if m != self.model]
        last_error = None

        for model_name in models_to_try:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={self.api_key}"
            
            payload = {
                "contents": [
                    {
                        "parts": [{"text": prompt}]
                    }
                ],
                "generationConfig": {
                    "temperature": temperature,
                    "maxOutputTokens": 3000
                }
            }
            if system_instruction:
                payload["systemInstruction"] = {
                    "parts": [{"text": system_instruction}]
                }

            data = json.dumps(payload).encode("utf-8")
            req = urllib.request.Request(
                url,
                data=data,
                headers={"Content-Type": "application/json"},
                method="POST"
            )

            try:
                with urllib.request.urlopen(req, timeout=25) as resp:
                    resp_data = json.loads(resp.read().decode("utf-8"))
                    candidates = resp_data.get("candidates", [])
                    if candidates:
                        parts = candidates[0].get("content", {}).get("parts", [])
                        if parts:
                            return parts[0].get("text", "")
            except urllib.error.HTTPError as h_err:
                err_body = h_err.read().decode("utf-8", errors="ignore")
                last_error = f"HTTP {h_err.code}: {err_body}"
                continue
            except Exception as ex:
                last_error = ex
                continue

        raise RuntimeError(f"All Gemini REST API endpoints failed. Last error: {last_error}")

    def _fallback_generate(self, prompt, system_instruction=None, user_question=None, persona="socratic"):
        """Educational generator for offline demonstration and testing without an API key."""
        prompt_lower = prompt.lower()

        # Check if JSON quiz was requested
        if "adaptive assessment engine" in prompt_lower or ("questions" in prompt_lower and "bloom" in prompt_lower):
            topic_match = re.search(r'topic:\s*\"([^\"]+)\"', prompt, re.IGNORECASE)
            topic = topic_match.group(1) if topic_match else "Machine Learning & AI"
            return json.dumps({
                "title": f"{topic} Mastery Quiz",
                "topic": topic,
                "difficulty": "intermediate",
                "bloom_level_focus": "all",
                "questions": [
                    {
                        "id": 1,
                        "question": f"Which of the following best defines the primary foundational goal of {topic}?",
                        "options": [
                            f"To systematically identify patterns and formulate predictive or analytical insights",
                            "To store static tabular records without automated inference",
                            "To manually hand-craft every edge case rule without statistical generalization",
                            "To bypass computational validation routines"
                        ],
                        "correct_index": 0,
                        "bloom_level": "remember",
                        "bloom_name": "Remembering",
                        "explanation": f"In {topic}, the core foundation is learning patterns and representations from input features to generalize to unseen instances.",
                        "hint": "Recall the fundamental purpose of pattern extraction and model generalization."
                    },
                    {
                        "id": 2,
                        "question": f"How does the concept of variance differ from bias when analyzing model performance in {topic}?",
                        "options": [
                            "Bias measures underfitting to assumptions; variance measures sensitivity to training data fluctuations",
                            "Variance and bias are identical mathematical metrics",
                            "Variance measures test runtime latency while bias measures memory consumption",
                            "Bias only applies to unsupervised clustering models"
                        ],
                        "correct_index": 0,
                        "bloom_level": "understand",
                        "bloom_name": "Understanding",
                        "explanation": "High bias leads to underfitting due to overly simplistic assumptions, whereas high variance leads to overfitting due to excessive sensitivity to training set noise.",
                        "hint": "Think of bias as systematic error and variance as dataset volatility."
                    },
                    {
                        "id": 3,
                        "question": f"An engineer applying {topic} observes training accuracy of 99% but validation accuracy of 68%. Which remediation technique should be prioritized?",
                        "options": [
                            "Introduce regularization (L1/L2, dropout) or collect more representative data",
                            "Increase model parameter size by 10x without dropout",
                            "Eliminate all validation sets and train strictly on raw test records",
                            "Disable gradient descent learning rate decay"
                        ],
                        "correct_index": 0,
                        "bloom_level": "apply",
                        "bloom_name": "Applying",
                        "explanation": "A large gap between training and validation accuracy is the textbook signature of overfitting. Regularization, data augmentation, and early stopping constrain model capacity.",
                        "hint": "What mechanism restrains a model from memorizing noise?"
                    },
                    {
                        "id": 4,
                        "question": f"When evaluating two competing architectures for {topic}, which trade-off curve is most critical to analyze for binary classification under class imbalance?",
                        "options": [
                            "Precision-Recall (PR) AUC rather than standard ROC-AUC",
                            "Raw Training Epoch Speed vs GPU Core Clock",
                            "Simple Mean Squared Error on Unnormalized labels",
                            "Unweighted Accuracy score alone"
                        ],
                        "correct_index": 0,
                        "bloom_level": "analyze",
                        "bloom_name": "Analyzing",
                        "explanation": "With severe class imbalance (e.g. 99% negative cases), ROC-AUC can present an overly optimistic picture, whereas PR curves directly scrutinize precision among positive predictions.",
                        "hint": "Which metric focuses specifically on the minority positive class?"
                    },
                    {
                        "id": 5,
                        "question": f"In designing an ethical deployment pipeline for {topic}, how should you evaluate potential algorithmic bias across demographic subgroups?",
                        "options": [
                            "Conduct disaggregated performance audits and fairness parity evaluations across protected attributes",
                            "Simply omit demographic labels and assume fairness is automatically preserved",
                            "Maximize aggregate accuracy across the whole population regardless of sub-group disparity",
                            "Rely solely on subjective stakeholder surveys"
                        ],
                        "correct_index": 0,
                        "bloom_level": "evaluate",
                        "bloom_name": "Evaluating",
                        "explanation": "Fairness audits require disaggregated metric evaluation (equalized odds, demographic parity) because removing protected attributes does not prevent proxy correlation bias.",
                        "hint": "Why is aggregate accuracy insufficient for vulnerable sub-populations?"
                    }
                ]
            })

        # Check if Flashcards were requested
        if "flashcard" in prompt_lower:
            topic_match = re.search(r'for:\s*\"([^\"]+)\"', prompt, re.IGNORECASE)
            topic = topic_match.group(1) if topic_match else "Core Concepts"
            return json.dumps({
                "deck_title": f"{topic} Flashcard Deck",
                "topic": topic,
                "cards": [
                    {
                        "id": 1,
                        "front": f"What is the foundational definition of {topic}?",
                        "back": f"{topic} is an organized domain that provides algorithmic frameworks, principles, and architectures to solve complex computational and cognitive challenges.",
                        "hint": "Think of the fundamental objective and theoretical framework.",
                        "bloom_level": "remember"
                    },
                    {
                        "id": 2,
                        "front": f"Explain the principle of abstraction in {topic}.",
                        "back": "Hiding low-level implementation complexities behind clean, well-defined modular interfaces to enable scalable system reasoning.",
                        "hint": "Separation of concerns and interface vs implementation.",
                        "bloom_level": "understand"
                    },
                    {
                        "id": 3,
                        "front": f"How do you diagnose performance bottlenecks in {topic}?",
                        "back": "Profile latency, analyze algorithmic time/space complexity (Big-O), and inspect I/O or convergence bottlenecks using systematic telemetry.",
                        "hint": "Measure before optimizing.",
                        "bloom_level": "apply"
                    },
                    {
                        "id": 4,
                        "front": f"Compare Trade-off: Efficiency vs Generalizability in {topic}.",
                        "back": "Specialized heuristics provide extreme efficiency on narrow data distributions, whereas broader parameterized models generalize better at the cost of compute.",
                        "hint": "No Free Lunch theorem.",
                        "bloom_level": "analyze"
                    },
                    {
                        "id": 5,
                        "front": f"What criteria validate that a {topic} solution is production-ready?",
                        "back": "Robust test coverage, graceful error handling, verified latency SLA, secure authentication, and observable telemetry metrics.",
                        "hint": "Reliability, scalability, and security.",
                        "bloom_level": "evaluate"
                    }
                ]
            })

        # Check if Roadmap was requested
        if "roadmap" in prompt_lower:
            goal_match = re.search(r'for:\s*\nGoal.*?: \"([^\"]+)\"', prompt, re.IGNORECASE)
            goal = goal_match.group(1) if goal_match else "Mastery Learning Track"
            return json.dumps({
                "title": f"{goal} Mastery Roadmap",
                "goal": goal,
                "duration_days": 14,
                "weekly_hours": 8,
                "phases": [
                    {
                        "phase_number": 1,
                        "phase_name": "Phase 1: Foundations & Core Architecture",
                        "days_range": "Days 1-4",
                        "key_objectives": [
                            "Understand core terminology, principles, and environmental setup",
                            "Build first working minimal prototype"
                        ],
                        "daily_milestones": [
                            {"day": 1, "task": "Set up workspace, dependencies, and review high-level overview", "checkpoint": "Environment verified and running", "estimated_minutes": 60},
                            {"day": 2, "task": "Study fundamental concepts and definitions through flashcard review", "checkpoint": "Complete Bloom's Level 1 & 2 quiz", "estimated_minutes": 90},
                            {"day": 3, "task": "Implement hands-on code examples and explore edge cases", "checkpoint": "Working prototype script", "estimated_minutes": 90},
                            {"day": 4, "task": "Consolidate notes and build mental model diagrams", "checkpoint": "One-page concept cheatsheet", "estimated_minutes": 60}
                        ]
                    },
                    {
                        "phase_number": 2,
                        "phase_name": "Phase 2: Deep Dive & Practical Application",
                        "days_range": "Days 5-9",
                        "key_objectives": [
                            "Analyze real-world problem statements and architectural trade-offs",
                            "Implement adaptive problem-solving techniques"
                        ],
                        "daily_milestones": [
                            {"day": 5, "task": "Examine case studies and architectural patterns", "checkpoint": "Compare 2 distinct approaches", "estimated_minutes": 90},
                            {"day": 6, "task": "Solve intermediate challenge problems and debug errors", "checkpoint": "Pass test cases", "estimated_minutes": 100},
                            {"day": 7, "task": "Rest & Spaced Repetition Flashcard review", "checkpoint": "Active recall retention review", "estimated_minutes": 45},
                            {"day": 8, "task": "Explore optimization, performance metrics, and bottlenecks", "checkpoint": "Benchmark analysis", "estimated_minutes": 90},
                            {"day": 9, "task": "Take diagnostic Bloom's Level 3 & 4 assessment", "checkpoint": "Achieve 80%+ mastery score", "estimated_minutes": 60}
                        ]
                    },
                    {
                        "phase_number": 3,
                        "phase_name": "Phase 3: Synthesis, Evaluation & Capstone",
                        "days_range": "Days 10-14",
                        "key_objectives": [
                            "Formulate original capstone project and conduct evaluation",
                            "Review comprehensive revision sheet before test"
                        ],
                        "daily_milestones": [
                            {"day": 10, "task": "Design and architect capstone project solution", "checkpoint": "Architecture specification doc", "estimated_minutes": 120},
                            {"day": 11, "task": "Develop core features of capstone project", "checkpoint": "End-to-end working system", "estimated_minutes": 120},
                            {"day": 12, "task": "Stress-test, evaluate failure modes, and add telemetry", "checkpoint": "Comprehensive evaluation report", "estimated_minutes": 90},
                            {"day": 13, "task": "Complete final mock exam covering all 6 Bloom's levels", "checkpoint": "90%+ target score", "estimated_minutes": 90},
                            {"day": 14, "task": "Final retrospective and portfolio documentation", "checkpoint": "Ready for presentation/certification", "estimated_minutes": 60}
                        ]
                    }
                ],
                "capstone_challenge": f"Design and implement an end-to-end practical solution demonstrating high-level mastery of {goal}.",
                "expert_tips": [
                    "Practice active recall every 48 hours rather than passive reading.",
                    "Explain each concept out loud in plain English (Feynman technique) to identify knowledge gaps.",
                    "Always solve problems with pen and paper first before writing code."
                ]
            })

        # Check if Notes were requested
        if "smart study notes generator" in prompt_lower or "core summary" in prompt_lower:
            topic_match = re.search(r'for:\s*\"([^\"]+)\"', prompt, re.IGNORECASE)
            topic = topic_match.group(1) if topic_match else "Study Topic"
            return f"""# 🎓 {topic}: Core Summary
**{topic}** represents a fundamental domain in modern computation and reasoning. At its core, it enables practitioners to formalize complex unstructured problems into structured, solvable components using verifiable rules and statistical models.

---

## 💡 Key Concepts & Definitions
- **Foundational Abstraction**: Isolating the essential semantic properties of a problem from incidental implementation details.
- **Inference & Generalization**: The capacity of an algorithm or cognitive agent to apply previously validated patterns to unobserved data instances.
- **Objective Function**: The explicit mathematical metric formulated to quantify optimization success or error minimization.
- **Invariant Properties**: Conditions that remain unconditionally true across all valid state transitions within the system.

---

## 🔍 Real-World Analogy / Mental Model
Imagine an expert conductor leading a symphony orchestra:
Each section (strings, brass, percussion) operates with its own specific technique, yet all synchronize through the conductor's rhythmic cues and score. Similarly, **{topic}** orchestrates disparate data inputs and processing stages into a harmonious, predictive output.

---

## ⚙️ Step-by-Step Breakdown & Mechanism
1. **Input Acquisition & Normalization**: Raw features and signals are validated, sanitized, and transformed into standard dimensional representations.
2. **Feature Representation & Embedding**: Data is mapped into high-dimensional vector spaces where semantic proximity mirrors conceptual similarity.
3. **Core Transformation / Decision Engine**: Parameterized layers apply mathematical transforms guided by the underlying model architecture.
4. **Output Verification & Calibration**: Results undergo threshold validation, error bounds checking, and confidence calibration before presentation.

---

## 📐 Formulae / Code Snippets / Theorems
```python
# Minimal Idiomatic Implementation Pattern for {topic}
def process_pipeline(input_data: list, threshold: float = 0.5) -> dict:
    \"\"\"Demonstrates deterministic execution flow.\"\"\"
    normalized = [x / max(input_data) for x in input_data if x is not None]
    results = [round(val, 3) for val in normalized if val >= threshold]
    return {{
        "total_processed": len(input_data),
        "retained_signals": len(results),
        "mean_activation": sum(results) / max(len(results), 1)
    }}
```

---

## ⚠️ Common Misconceptions & Exam Pitfalls
> **Pitfall 1**: Confusing correlation with causal dependency in observed features.  
> **Pitfall 2**: Neglecting distribution shift between training environments and production runtime.  
> **Pitfall 3**: Assuming larger model capacity automatically guarantees better out-of-sample generalization without regularization.

---

## 📝 Quick Review Checklist
- [ ] Can you define the core objective of {topic} in under 20 seconds?
- [ ] Have you memorized the top 3 mathematical formulas or architectural constraints?
- [ ] Can you diagram the end-to-end dataflow from memory?
- [ ] Do you understand why standard accuracy fails under skewed distributions?
- [ ] Can you explain the trade-off between model latency and inference precision?
"""

        # --- AI Tutor Chat Response Handling ---
        # Extract the real clean question
        clean_question = user_question
        if not clean_question:
            m_q = re.search(r'Student Question:\s*(.*)', prompt, re.DOTALL)
            clean_question = m_q.group(1).split("\n\nPlease respond")[0].strip() if m_q else prompt.strip()

        q_lower = clean_question.lower()

        # Specific high-demand topic: Types of Errors (5-mark exam style question answer)
        if "error" in q_lower or "types of error" in q_lower:
            return """### 📋 5-Mark Exam Question & Model Answer: Types of Errors in Programming

**Question:**  
*(5 Marks)* Define error in programming. Explain the major types of errors encountered during program compilation and execution with a suitable example for each.

---

### 📝 Model Answer & Marking Scheme:

#### 1. Definition (1 Mark)
An **error** (or bug) is an illegal state, flaw, or mistake in computer program code that causes it to produce incorrect output, crash, or fail to compile.

#### 2. Types of Errors (3 Marks - 1 mark for each major type with example)

* **A. Syntax Errors (Compile-Time Errors)**  
  Occur when code violates the grammatical rules of the programming language. Detected by the compiler/interpreter before execution.  
  *Example:* Missing closing bracket or semicolon.
  ```python
  # Syntax Error: Missing colon at end of if statement
  if x > 10
      print("x is large")
  ```

* **B. Runtime Errors (Exceptions)**  
  Occur while the program is actively executing, causing it to terminate abruptly (crash). Syntactically valid, but illegal operations are attempted.  
  *Example:* Division by zero, index out of bounds, null pointer dereference.
  ```python
  # Runtime Error: ZeroDivisionError
  result = 100 / 0
  ```

* **C. Logical Errors (Semantic Errors)**  
  The program compiles and runs to completion without crashing, but produces **incorrect or unintended results** due to flawed programmer logic or algorithmic mistakes.  
  *Example:* Using addition instead of multiplication.
  ```python
  # Logical Error: Area of rectangle should be width * height
  area = width + height  # Logical bug!
  ```

#### 3. Summary & Comparison Table (1 Mark)

| Error Type | Detection Stage | Caused By | Program Crashes? |
| :--- | :--- | :--- | :--- |
| **Syntax Error** | Compilation / Parsing | Grammar rule violation | Doesn't run at all |
| **Runtime Error** | Execution | Illegal operations (e.g. ÷ 0) | Yes (Uncaught crash) |
| **Logical Error** | Post-execution testing | Flawed algorithm / formula | No (Wrong answer) |

---

> 💡 **Exam Tip (Coach Advice):** Always include code examples for each error type to secure full marks. Examiners look for the distinct detection stage (Compile-time vs Runtime vs Post-test).
"""

        # Other exam style requests
        if "exam" in q_lower and ("mark" in q_lower or "question" in q_lower):
            return f"""### 📋 Model Exam Answer: {clean_question}

#### 1. Core Definition & Principle (1 Mark)
A concise, high-yield definition addressing the fundamental concept directly.

#### 2. Technical Breakdown & Mechanism (2 Marks)
- **Primary Mechanism**: How the underlying logic operates step-by-step.
- **Key Equation or Rule**: The mathematical or algorithmic formulation that governs the system.

#### 3. Concrete Example or Code Illustration (1 Mark)
```python
# Illustrative Minimal Example
def example_demonstration(inputs):
    return [process(x) for x in inputs if validate(x)]
```

#### 4. Summary & High-Yield Distinction (1 Mark)
- **Common Exam Trap**: Never confuse this concept with related terms.
- **Exam Heuristic**: Remember the 3-step test-day checklist.

---
*Tip: Written in accordance with standard 5-mark university marking rubrics.*
"""

        # General intelligent tutor response
        return f"""### 💡 {clean_question}

Hello! Here is a structured breakdown from your **EduGenie AI Tutor**:

1. **Core Concept**:
   Let's dissect **"{clean_question}"** directly. The key idea centers on establishing clear relationships between your inputs, constraints, and target outcomes.

2. **Step-by-Step Logic**:
   - **Step 1**: Establish fundamental definitions and boundary conditions.
   - **Step 2**: Apply the core governing theorem or algorithmic mechanism.
   - **Step 3**: Scrutinize edge cases, failure modes, and efficiency trade-offs.

3. **High-Yield Mental Model**:
   Visualize the mechanism like a well-calibrated pipeline: each stage sanitizes, validates, and refines the data before passing it downstream.

---

#### ❓ Reflection Question:
*How would this behavior change if the primary boundary condition were inverted? Give it a thought and let's discuss!*
"""

# Global singleton
gemini_client = GeminiClient()
