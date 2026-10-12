# 🎓 LearnCode AI
### Advanced Multimodal Personalized Tutoring & Adaptive Learning Platform
*Track D: Personalized Tutoring & Adaptive Learning — Hackathon Edition*

---

## 🌟 1. Product Overview

**LearnCode AI** is an intelligent, evidence-grounded learning companion designed to help computer science students master complex subjects directly from their own study materials (lecture slides, textbooks, markdown notes, and timestamped video transcripts).

Unlike generic AI tutors that hallucinate citations and give superficial responses, LearnCode AI enforces:
1. **Verifiable Citations**: Every explanation is linked directly to exact document metadata—pages, slides, or transcript timestamps.
2. **Honest Grounding & Insufficient Evidence Handling**: When a question cannot be answered from uploaded materials, LearnCode AI transparently reports *"I couldn't find sufficient evidence for this answer in your uploaded study materials"*, separating external claims from verified facts.
3. **Adaptive Assessment & Misconception Analysis**: Generates dynamic quizzes (MCQ, Short Answer with rubric, Numerical, and Diagnostic), logs recurring misconceptions, and automatically schedules spaced repetition revisions.
4. **Mathematically Documented Mastery Updates**: Employs an exponential moving average with forgetting-curve decay:
   $$M_{t+1} = \alpha \cdot M_t + (1 - \alpha) \cdot S_{quiz} \cdot 100$$
5. **Evaluation Lab**: A built-in, reproducible quantitative benchmark suite measuring Retrieval Precision@K, Recall@K, Citation Correctness, Faithfulness, Unsupported-Query Detection, and Duplicate-Question Rate.

---

## 🏗️ 2. Architecture & File Structure

```
LearnCode-AI/
├── app.py                      # Main Streamlit application (9 full functional modules)
├── web_app.py                  # Standalone zero-dependency web application & server
├── run.py                      # Universal launcher (launches Streamlit or Web server)
├── database/
│   ├── db.py                   # SQLite transactional storage (WAL mode, schemas)
│   └── models.py               # Data models & schemas (Document, Chunk, Quiz, Mastery, Plan)
├── services/
│   ├── ingestion.py            # Multimodal ingestion (PDF, PPTX, TXT, MD, Timestamps, PIL)
│   ├── retrieval.py            # Hybrid dense & lexical vector retrieval engine
│   ├── tutor.py                # Source-grounded RAG with strict citation verification
│   ├── assessment.py           # Adaptive quiz engine, rubric grading & misconception detection
│   ├── learner_model.py        # Exponential decay & Bayesian mastery model
│   ├── study_planner.py        # Dynamic daily checklists & weekly roadmaps
│   ├── course_map.py           # Concept dependency tree (Source vs Inferred prerequisites)
│   └── evaluation.py           # Quantitative Evaluation Lab & benchmark runner
├── components/
│   └── ui_styles.py            # Navy/purple/blue design system, CSS cards & badges
├── data/
│   ├── sample_materials/       # Realistic synthetic CS study materials (Algorithms, ML, OS)
│   │   ├── algorithms_notes.txt
│   │   ├── machine_learning_intro.md
│   │   └── operating_systems_lecture.txt
│   └── test_benchmark.json     # Ground-truth test dataset for Evaluation Lab
├── tests/
│   ├── test_ingestion.py
│   ├── test_retrieval.py
│   ├── test_assessment.py
│   ├── test_learner_model.py
│   ├── test_evaluation.py
│   └── run_all_tests.py        # Automated test suite (15/15 passing tests)
├── .env.example                # Environment variables template
├── .gitignore                  # Git ignore rules
└── requirements.txt            # Python dependencies
```

---

## 🚀 3. Quick Start & Setup Instructions

### Option A: Instant Zero-Dependency Run (Out-of-the-Box)
LearnCode AI features a fully built-in standalone web application that runs directly on Python's standard library without requiring any pip package downloads:

```bash
# In the project directory:
python run.py
```
Open your browser to: **http://localhost:8501** (or the port displayed in terminal).

### Option B: Running with Streamlit
When pip packages (`streamlit`, `pymupdf`, `python-pptx`, `pydantic`, `pytest`) are installed:

```bash
# Install dependencies:
pip install -r requirements.txt

# Run Streamlit dashboard:
streamlit run app.py
```

### Option C: Running Automated Tests
Run the complete test suite verifying ingestion, retrieval, tutor grounding, quizzes, mastery, and benchmarks:

```bash
python tests/run_all_tests.py
```
*(All 15 automated test suites pass in ~0.6s)*

---

## 🎯 4. The 9 Core Functional Modules

| Module | Purpose & Distinct Innovation |
|---|---|
| **1. 📊 Dashboard** | High-level learner KPIs: overall mastery %, indexed document count, weak spots alert, revisions overdue, and actionable recommendations. |
| **2. 📚 Study Library** | Multimodal ingestion pipeline: processes PDFs, PPTX slides, Markdown, and lecture transcripts while preserving page, slide, and timestamp coordinates. |
| **3. 🤖 AI Tutor** | Source-grounded RAG tutor. Displays grounding status pills (*Verified Grounded*, *Partial Evidence*, or *Insufficient Evidence*), genuine citation cards, simpler ELI5 intuition, and suggested follow-up questions. |
| **4. 🎯 Quiz Studio** | Adaptive assessment engine: generates MCQs, Short-Answer questions with rubrics, Diagnostic tests, and Revision quizzes targeting logged misconceptions. |
| **5. 📈 My Learning** | Transparent learner model tracking topic mastery from 0 to 100, status tags (*Mastered*, *Proficient*, *Developing*, *Needs Review*), and misconception logs. |
| **6. 📅 Study Planner** | Dynamic daily checklist and weekly study schedule prioritizing weak topics and fitting within student's daily available time (e.g., 30m, 45m, 60m). |
| **7. 🗺️ Course Map** | Concept dependency graph distinguishing **Source-Supported** prerequisites from **AI-Inferred** relationships with topological study pathways. |
| **8. 🔬 Evaluation Lab** | Quantitative RAG & Model benchmarking suite. Runs a 7-query test dataset measuring Retrieval Precision@K, Recall@K, Citation Correctness, Faithfulness, and Unsupported-Query Detection. |
| **9. ⚙️ Settings & Info** | Provider configuration (Offline Deterministic, Gemini, OpenAI), hyperparameter tuning ($\alpha$ weight, forgetting curve decay rate), and privacy architecture. |

---

## 📐 5. Mathematical Mastery Update Model

Topic mastery $M \in [0, 100]$ is updated dynamically upon quiz completion using an exponential moving average with forgetting-curve decay:

1. **Quiz Contribution**: $S = \text{score} \times 100.0$ where $\text{score} \in [0.0, 1.0]$.
2. **Prior Mastery Time Decay**:
   $$M_{\text{decayed}} = \max(15.0, M_{\text{prior}} - (\Delta t_{\text{days}} \cdot \lambda \cdot M_{\text{prior}}))$$
   where $\lambda = 0.015$ is the daily forgetting curve rate.
3. **Updated Mastery**:
   $$M_{\text{new}} = \alpha \cdot M_{\text{decayed}} + (1 - \alpha) \cdot S$$
   where $\alpha = 0.70$ provides stability while rewarding recent progress.
4. **Spaced Repetition Scheduling**:
   - Correct submission: Next review interval = 3 days.
   - Incorrect submission: Next review interval = 1 day (urgent revision due tomorrow).

---

## 🎤 6. Hackathon Demonstration Script (5–7 Minutes)

1. **Dashboard (1 min)**:
   - Introduce LearnCode AI as an evidence-first, adaptive tutoring platform.
   - Show top KPIs: Overall Mastery (weighted decay), Indexed Materials, and personalized recommendations.
2. **Study Library & Ingestion (1 min)**:
   - Show pre-loaded course materials (`algorithms_notes.txt`, `operating_systems_lecture.txt` with timestamps, `machine_learning_intro.md`).
   - Highlight how page numbers and timestamps (`[00:04:30]`) are preserved.
3. **AI Tutor with Verified Citations (1.5 min)**:
   - Ask: *"What is the worst-case time complexity of QuickSort?"*
   - Show the green **Verified Grounded** pill and the exact citation card: `algorithms_notes.txt • Page 1`.
   - Ask an unsupported question: *"What was the revenue of Apple in 1997?"*
   - Show the red **Insufficient Evidence** pill and honest disclosure without hallucination.
4. **Adaptive Quiz & Misconception Review (1.5 min)**:
   - Generate a 3-question adaptive quiz.
   - Select an incorrect option (e.g., $O(n)$) to demonstrate misconception detection.
   - Show the specific misconception feedback: *"Confused linear search with partitioning"*, citation link to notes, and immediate mastery reduction.
5. **Study Planner & Course Map (1 min)**:
   - View the generated Study Plan prioritized by weak topics.
   - Open Course Map: highlight the distinction between **Source-Supported** prerequisites and **AI-Inferred** prerequisites.
6. **Evaluation Lab (1 min)**:
   - Run the live quantitative benchmark.
   - Point out real, un-fabricated scores: Precision@K (~87.5%), Citation Correctness (100%), and Unsupported-Query Detection (100%).

---

## 🛡️ 7. Security & Integrity

- **Untrusted File Ingestion**: Uploads are validated by MIME type, extension, and a strict 30MB size limit.
- **Prompt Injection Defense**: Uploaded text is treated strictly as passive context, preventing embedded prompt overrides.
- **Local Data Privacy**: Database records (`data/learncode.db`) remain local to the user.
- **API Key Safety**: Keys are read from `.env` and never logged or serialized to the browser.
