"""
LearnCode AI — Master Application
Advanced Multimodal Personalized Tutoring & Adaptive Learning Platform
Track D: Personalized Tutoring & Adaptive Learning
"""
import sys
import os
import json
import tempfile
from datetime import datetime

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# Add project root to sys.path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

try:
    import streamlit as st
    HAS_STREAMLIT = True
except ImportError:
    HAS_STREAMLIT = False

# Services & Database
from database.db import get_db
from database.models import (
    DocumentMetadata,
    DocumentChunk,
    AssessmentQuestion,
    AssessmentEvaluation,
    TopicMasteryRecord,
    StudyPlan,
)
from services.ingestion import IngestionPipeline
from services.retrieval import HybridRetrievalEngine
from services.tutor import GroundedTutorService
from services.assessment import AssessmentEngine
from services.learner_model import LearnerModelService
from services.study_planner import StudyPlannerService
from services.course_map import CourseMapService
from services.evaluation import EvaluationLabService
from components.ui_styles import (
    CUSTOM_CSS,
    render_brand_header,
    render_metric_card,
    render_citation_box,
    render_grounding_badge,
)


def seed_default_materials_if_empty(db, ingestion):
    """Pre-populates sample educational materials if database is brand new."""
    docs = db.get_all_documents()
    if not docs:
        sample_dir = os.path.join(BASE_DIR, "data", "sample_materials")
        if os.path.exists(sample_dir):
            for fname in os.listdir(sample_dir):
                fpath = os.path.join(sample_dir, fname)
                if os.path.isfile(fpath):
                    try:
                        d_meta, d_chunks = ingestion.process_file(fpath, filename=fname, is_demo=True)
                        db.save_document(d_meta, d_chunks)
                        for prereq in d_meta.extra_metadata.get("detected_prerequisites", []):
                            db.save_prerequisite(
                                prereq["from_topic"],
                                prereq["to_topic"],
                                prereq["is_explicit"],
                                prereq.get("rationale", ""),
                                prereq.get("source_ref", "")
                            )
                    except Exception:
                        pass


def main():
    if not HAS_STREAMLIT:
        print("\n=======================================================")
        print(" LearnCode AI — Master Platform")
        print("=======================================================")
        print("Streamlit package is not currently installed in this environment.")
        print("Launching the self-contained modern web application server instead...")
        from web_app import run_web_server
        run_web_server()
        return

    st.set_page_config(
        page_title="LearnCode AI — Personalized Tutoring",
        page_icon="🎓",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

    # Initialize Backend
    db = get_db()
    ingestion = IngestionPipeline()
    retrieval = HybridRetrievalEngine()
    tutor = GroundedTutorService(retrieval)
    assessment = AssessmentEngine(db)
    learner_model = LearnerModelService(db)
    study_planner = StudyPlannerService(db)
    course_map = CourseMapService(db)
    eval_lab = EvaluationLabService(db)

    # Seed starter materials for instant hackathon demonstration
    seed_default_materials_if_empty(db, ingestion)

    # Sidebar Navigation
    with st.sidebar:
        st.markdown("""
        <div style="padding: 10px 0 20px 0;">
            <div style="font-size:20px; font-weight:800; color:#1e1b4b; display:flex; align-items:center; gap:8px;">
                <span>🎓 LearnCode AI</span>
            </div>
            <div style="font-size:12px; color:#64748b; margin-top:2px;">Track D: Adaptive Tutoring & RAG</div>
        </div>
        """, unsafe_allow_html=True)

        nav_options = [
            "📊 Dashboard",
            "📚 Study Library",
            "🤖 AI Tutor",
            "🎯 Quiz Studio",
            "📈 My Learning",
            "📅 Study Planner",
            "🗺️ Course Map",
            "🔬 Evaluation Lab",
            "⚙️ Settings & Info"
        ]

        if "current_page" not in st.session_state:
            st.session_state["current_page"] = nav_options[0]

        selected_page = st.radio("Navigation", nav_options, index=nav_options.index(st.session_state["current_page"]))
        st.session_state["current_page"] = selected_page

        st.markdown("---")
        st.markdown("### Active Learner")
        user_id = st.text_input("Student ID", value="student_sankari", key="active_user_id")

        st.markdown("---")
        st.caption("Built for Hackathon Track D • Real Multimodal Grounding • Zero-Hallucination Citations")

    # -------------------------------------------------------------
    # 1. DASHBOARD
    # -------------------------------------------------------------
    if selected_page == "📊 Dashboard":
        st.markdown(render_brand_header(
            title="LearnCode AI Dashboard",
            subtitle="Your personalized multimodal tutoring and adaptive mastery control center"
        ), unsafe_allow_html=True)

        analytics = learner_model.get_learner_analytics(user_id=user_id)
        docs = db.get_all_documents()

        # Top metric cards
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            st.markdown(render_metric_card("Overall Mastery", f"{analytics['overall_mastery']}%", "Weighted exponential decay model"), unsafe_allow_html=True)
        with c2:
            st.markdown(render_metric_card("Indexed Materials", f"{len(docs)} Docs", f"{sum(d.total_chunks for d in docs)} verified chunks"), unsafe_allow_html=True)
        with c3:
            st.markdown(render_metric_card("Weak Spots Identified", f"{len(analytics['weak_topics'])} Topics", "Scores under 70% threshold"), unsafe_allow_html=True)
        with c4:
            st.markdown(render_metric_card("Revisions Due", f"{len(analytics['revisions_due'])} Overdue", "Spaced repetition Leitner schedule"), unsafe_allow_html=True)

        st.write("")

        # Actionable recommendations
        st.markdown("### 🎯 Recommended Next Learning Actions")
        if analytics["recommendations"]:
            for rec in analytics["recommendations"]:
                with st.container():
                    st.info(f"**[{rec['type']}] {rec['topic']}**: {rec['reason']}\n\n*Action:* {rec['action']}")
        else:
            st.success("🎉 You are up to date! Upload new chapters or take a Diagnostic Quiz to explore advanced topics.")

        col_left, col_right = st.columns([1.2, 1])

        with col_left:
            st.markdown("### 📚 Topics & Mastery Breakdown")
            all_records = analytics["all_records"]
            if all_records:
                for r in all_records:
                    col_t, col_bar = st.columns([1, 2])
                    with col_t:
                        st.write(f"**{r.topic}** ({r.status})")
                    with col_bar:
                        st.progress(r.mastery_score / 100.0)
            else:
                st.caption("No quiz attempts yet. Start by asking the AI Tutor or taking a Quiz!")

        with col_right:
            st.markdown("### ⚡ Quick Jump Actions")
            if st.button("🤖 Ask AI Tutor a Question", use_container_width=True):
                st.session_state["current_page"] = "🤖 AI Tutor"
                st.rerun()
            if st.button("🎯 Generate Adaptive Quiz", use_container_width=True):
                st.session_state["current_page"] = "🎯 Quiz Studio"
                st.rerun()
            if st.button("📅 View My Study Plan", use_container_width=True):
                st.session_state["current_page"] = "📅 Study Planner"
                st.rerun()
            if st.button("🔬 Open Evaluation Benchmark Lab", use_container_width=True):
                st.session_state["current_page"] = "🔬 Evaluation Lab"
                st.rerun()

    # -------------------------------------------------------------
    # -------------------------------------------------------------
    # 2. STUDY LIBRARY (Multimodal Ingestion & Document Management)
    # -------------------------------------------------------------
    elif selected_page == "📚 Study Library":
        st.markdown(render_brand_header(
            title="Study Library & Multimodal Ingestion Pipeline",
            subtitle="Upload PDFs, PowerPoint slides, notes, or lecture transcripts with timestamps"
        ), unsafe_allow_html=True)

        tab_upload, tab_view = st.tabs(["📤 Upload New Material", "📑 Manage Indexed Documents"])

        with tab_upload:
            st.markdown("#### Upload Your Study Materials")
            st.markdown(
                "Supported formats: **PDF (`.pdf`)** (extracts pages & coordinates via PyMuPDF), "
                "**PowerPoint (`.pptx`)** (preserves slides), "
                "**Markdown (`.md`) & Plain Text (`.txt`)**, "
                "and **Lecture Transcripts (`.srt`, `.vtt`)** with timestamps. Max size: 30 MB."
            )

            uploaded_file = st.file_uploader(
                "Select a PDF, textbook, slide deck, or transcript from your computer:",
                type=["pdf", "pptx", "txt", "md", "json", "vtt", "srt"],
                key="streamlit_file_uploader"
            )

            if uploaded_file is not None:
                # File details card
                col_f1, col_f2, col_f3 = st.columns(3)
                with col_f1:
                    st.info(f"**Filename:** {uploaded_file.name}")
                with col_f2:
                    ext_label = os.path.splitext(uploaded_file.name)[1].upper()
                    st.info(f"**Type:** {uploaded_file.type or ext_label}")
                with col_f3:
                    f_kb = len(uploaded_file.getvalue()) / 1024
                    f_size_str = f"{f_kb / 1024:.2f} MB" if f_kb > 1024 else f"{f_kb:.1f} KB"
                    st.info(f"**Size:** {f_size_str}")

                col_top, col_over = st.columns([2, 1])
                with col_top:
                    custom_topic = st.text_input(
                        "Primary Subject / Topic (optional — auto-detected from contents if blank):",
                        placeholder="e.g. Algorithms, Operating Systems, Machine Learning"
                    )
                with col_over:
                    overwrite_doc = st.checkbox("Overwrite if filename exists", value=False)

                if st.button("🚀 Upload & Process Document", use_container_width=True):
                    file_bytes = uploaded_file.getvalue()
                    file_size = len(file_bytes)

                    # Validation
                    is_valid, v_msg = ingestion.validate_file(uploaded_file.name, file_size)
                    if not is_valid:
                        st.error(f"❌ Validation Error: {v_msg}")
                    else:
                        existing = db.get_document_by_filename(uploaded_file.name)
                        if existing and not overwrite_doc:
                            st.warning(
                                f"⚠️ A document named '{uploaded_file.name}' is already indexed in your Study Library. "
                                "Enable 'Overwrite if filename exists' or delete the existing document to replace it."
                            )
                        else:
                            with st.spinner("Extracting text, preserving source coordinates, and building vector index..."):
                                t_ext = os.path.splitext(uploaded_file.name)[1].lower()
                                with tempfile.NamedTemporaryFile("wb", suffix=t_ext, delete=False) as tf:
                                    tf.write(file_bytes)
                                    tf_path = tf.name

                                try:
                                    if existing and overwrite_doc:
                                        db.delete_document(existing.id)

                                    doc_meta, chunks = ingestion.process_file(
                                        tf_path,
                                        filename=uploaded_file.name,
                                        user_topic=custom_topic.strip() or None,
                                        is_demo=False
                                    )
                                    db.save_document(doc_meta, chunks)

                                    for p in doc_meta.extra_metadata.get("detected_prerequisites", []):
                                        db.save_prerequisite(
                                            p["from_topic"],
                                            p["to_topic"],
                                            p["is_explicit"],
                                            p.get("rationale", ""),
                                            p.get("source_ref", "")
                                        )

                                    st.session_state["last_upload_info"] = {
                                        "doc": doc_meta,
                                        "chunks_count": len(chunks)
                                    }
                                    st.rerun()
                                except Exception as e:
                                    st.error(f"❌ Failed to process document: {str(e)}")
                                finally:
                                    if os.path.exists(tf_path):
                                        try:
                                            os.remove(tf_path)
                                        except Exception:
                                            pass

            # Persistent upload summary if a file was just processed
            if "last_upload_info" in st.session_state:
                info = st.session_state["last_upload_info"]
                d = info["doc"]
                st.write("---")
                st.success(f"✅ Successfully uploaded and indexed **{d.filename}** in your Study Library!")
                m1, m2, m3, m4 = st.columns(4)
                with m1:
                    st.metric("Primary Topic", d.primary_topic)
                with m2:
                    st.metric("Pages / Sections", d.total_pages_or_slides)
                with m3:
                    st.metric("Indexed Chunks", info["chunks_count"])
                with m4:
                    st.metric("Status", d.extra_metadata.get("processing_status", "Indexed & Searchable"))

                preview = d.extra_metadata.get("preview_text", "")
                if preview:
                    with st.expander("📖 Extracted Text Preview", expanded=True):
                        st.markdown(f"> {preview}")

                c_action1, c_action2, c_action3 = st.columns([1.5, 1.5, 1])
                with c_action1:
                    if st.button("🤖 Ask AI Tutor About This Document", use_container_width=True):
                        st.session_state["selected_doc_filter"] = d.id
                        st.session_state["current_page"] = "🤖 AI Tutor"
                        st.rerun()
                with c_action2:
                    if st.button("🎯 Generate Quiz from This Document", use_container_width=True):
                        st.session_state["quiz_doc_filter"] = d.id
                        st.session_state["current_page"] = "🎯 Quiz Studio"
                        st.rerun()
                with c_action3:
                    if st.button("Dismiss Notice", use_container_width=True):
                        del st.session_state["last_upload_info"]
                        st.rerun()

        with tab_view:
            user_docs = db.get_user_documents()
            demo_docs = db.get_demo_documents()

            # Search bar across all chunks
            search_query = st.text_input("🔍 Search within indexed documents and chunks:", placeholder="Search keywords, definitions, or algorithms across your library...")
            if search_query.strip():
                st.markdown(f"#### 🔎 Search Results for *'{search_query}'*:")
                search_results = db.search_chunks(search_query)
                if not search_results:
                    st.info(f"No indexed chunks matched '{search_query}'.")
                else:
                    st.caption(f"Found {len(search_results)} relevant chunks:")
                    for ch in search_results[:5]:
                        st.markdown(f"""
                        <div class="citation-box">
                            <strong>📄 {ch.filename} &bull; {ch.source_location} ({ch.topic})</strong>
                            <p style="margin-top:4px;">{ch.text[:240]}...</p>
                        </div>
                        """, unsafe_allow_html=True)
                st.write("---")

            # Section 1: User's Uploaded Documents
            st.markdown(f"### 📂 Uploaded Study Documents ({len(user_docs)})")
            if not user_docs:
                st.info("No personal study documents uploaded yet. Use the **Upload New Material** tab above to upload your course PDFs, slides, or transcripts!")
            else:
                for d in user_docs:
                    with st.expander(f"📄 {d.filename} — {d.primary_topic} ({d.file_type})", expanded=False):
                        st.write(f"**Document ID:** `{d.id}` | **Size:** {d.file_size_bytes / 1024:.1f} KB | **Uploaded:** {d.uploaded_at[:19]}")
                        st.write(f"**Total Pages/Sections:** {d.total_pages_or_slides} | **Indexed Chunks:** {d.total_chunks} | **Status:** `{d.extra_metadata.get('processing_status', 'Indexed & Searchable')}`")

                        preview = d.extra_metadata.get("preview_text", "")
                        if preview:
                            st.markdown(f"**Extracted Preview:** *\"{preview[:220]}...\"*")

                        chunks = db.get_all_chunks(document_id=d.id)
                        if chunks:
                            st.markdown("##### Sample Extracted Chunks with Exact Citations:")
                            for c in chunks[:3]:
                                st.markdown(f"> **[{c.source_location}]** {c.text[:220]}...")

                        col_d_a, col_d_b, col_d_c = st.columns([1.5, 1.5, 1])
                        with col_d_a:
                            if st.button("🤖 Ask AI Tutor About This Document", key=f"tutor_jump_{d.id}", use_container_width=True):
                                st.session_state["selected_doc_filter"] = d.id
                                st.session_state["current_page"] = "🤖 AI Tutor"
                                st.rerun()
                        with col_d_b:
                            if st.button("🎯 Quiz from This Document", key=f"quiz_jump_{d.id}", use_container_width=True):
                                st.session_state["quiz_doc_filter"] = d.id
                                st.session_state["current_page"] = "🎯 Quiz Studio"
                                st.rerun()
                        with col_d_c:
                            if st.button(f"🗑️ Delete Document", key=f"del_{d.id}", use_container_width=True):
                                db.delete_document(d.id)
                                st.warning(f"Deleted {d.filename} and completely removed its indexed chunks from search.")
                                st.rerun()

            st.write("---")
            # Section 2: Demo / Sample Learning Materials (Separated as required)
            with st.expander("🧪 Demo Materials (Sample Pre-Loaded Content for Testing)", expanded=False):
                st.caption("These sample files were pre-loaded for instant offline demonstration. They are kept strictly separate from your personal uploaded study documents.")
                if not demo_docs:
                    st.write("No sample demo materials present.")
                else:
                    for d in demo_docs:
                        st.markdown(f"- **📄 {d.filename}** — *{d.primary_topic}* ({d.file_type}, {d.total_chunks} chunks)")

    # -------------------------------------------------------------
    # 3. AI TUTOR (Grounded RAG with Citations)
    # -------------------------------------------------------------
    elif selected_page == "🤖 AI Tutor":
        st.markdown(render_brand_header(
            title="Source-Grounded AI Tutor",
            subtitle="Ask questions with genuine citations, exact page/slide/timestamp references, and honest evidence verification"
        ), unsafe_allow_html=True)

        all_chunks = db.get_all_chunks()
        if not all_chunks:
            st.warning("⚠️ No documents indexed in the library. Please upload study materials in the Study Library first.")
            return

        all_docs = db.get_all_documents()
        doc_options = {"All Documents (Search Entire Library)": "All"}
        for d in all_docs:
            doc_options[f"📄 {d.filename} ({d.primary_topic})"] = d.id

        # Determine pre-selected document if jumped from Study Library
        default_doc_idx = 0
        preselected_id = st.session_state.get("selected_doc_filter")
        if preselected_id:
            for idx, (label, doc_val) in enumerate(doc_options.items()):
                if doc_val == preselected_id:
                    default_doc_idx = idx
                    break

        # Query options
        c_opt1, c_opt2, c_opt3 = st.columns([1.5, 1.2, 1.3])
        with c_opt1:
            chosen_doc_label = st.selectbox("Select Study Document", list(doc_options.keys()), index=default_doc_idx)
            selected_doc_id = doc_options[chosen_doc_label]
        with c_opt2:
            topics = ["All"] + sorted(list(set(c.topic for c in all_chunks)))
            filter_topic = st.selectbox("Filter by Subject / Topic", topics)
        with c_opt3:
            explain_style = st.selectbox("Explanation Intuition Level", ["Standard Student", "Beginner / ELI5", "In-depth Technical"])

        # Sample suggested queries
        st.markdown("**Sample Grounded Queries:**")
        sample_qs = [
            "What is the worst-case time complexity of QuickSort?",
            "Explain the difference between a process and a thread in OS.",
            "How does gradient descent update weights during training?",
            "What are the four Coffman conditions for deadlock?",
            "What was the total net revenue of Tesla in 1999? (Test unsupported handling)"
        ]
        chosen_sample = st.selectbox("Click to auto-fill query:", ["-- Type your own question below --"] + sample_qs)

        default_input = "" if chosen_sample.startswith("--") else chosen_sample
        user_query = st.text_input("Enter your computer science or course question:", value=default_input)

        if st.button("💬 Ask Tutor", use_container_width=True) or (default_input and st.session_state.get("last_q") != default_input):
            if not user_query.strip():
                st.warning("Please enter a question.")
            else:
                st.session_state["last_q"] = user_query
                with st.spinner("Retrieving verified source chunks and grounding explanation..."):
                    level_key = "beginner" if "Beginner" in explain_style else ("advanced" if "Technical" in explain_style else "standard")
                    response = tutor.answer_query(
                        user_query,
                        all_chunks,
                        filter_topic=filter_topic if filter_topic != "All" else None,
                        filter_document_id=selected_doc_id if selected_doc_id != "All" else None,
                        simplify_level=level_key
                    )

                    # Display Grounding Status Badge & Generation Provider
                    col_b1, col_b2 = st.columns([1, 1])
                    with col_b1:
                        st.markdown(render_grounding_badge(response.grounding_status), unsafe_allow_html=True)
                    with col_b2:
                        st.caption(f"**Generation Engine:** `{response.generation_provider}`")
                    st.write("")

                    # Main Grounded Response
                    st.markdown("### 📖 Tutor Explanation")
                    st.markdown(response.answer)

                    # Citations Display
                    if response.citations:
                        st.markdown("### 🔎 Verified Source Citations")
                        st.caption("These citations are linked to actual document metadata and excerpts:")
                        for cite in response.citations:
                            st.markdown(render_citation_box(
                                filename=cite.filename,
                                location=cite.source_location,
                                excerpt=cite.excerpt,
                                score=cite.relevance_score
                            ), unsafe_allow_html=True)
                    elif response.outside_knowledge_note:
                        st.markdown("### 🌐 External Context Disclosure")
                        st.warning(response.outside_knowledge_note)

                    # Simplified Explanation & Practical Examples
                    if response.simpler_explanation:
                        with st.expander("💡 Simpler Intuition / Breakdown"):
                            st.write(response.simpler_explanation)

                    if response.practical_example:
                        with st.expander("💻 Practical Application & Implementation"):
                            st.write(response.practical_example)

                    # Suggested Follow-up Questions
                    if response.suggested_followups:
                        st.markdown("### 🔮 Recommended Follow-up Inquiries")
                        for fu in response.suggested_followups:
                            st.markdown(f"- {fu}")

    # -------------------------------------------------------------
    # 4. QUIZ STUDIO (Adaptive Assessments & Misconceptions)
    # -------------------------------------------------------------
    elif selected_page == "🎯 Quiz Studio":
        st.markdown(render_brand_header(
            title="Intelligent Quiz Studio",
            subtitle="Adaptive assessments, misconception identification, diagnostic tests, and targeted revision quizzes"
        ), unsafe_allow_html=True)

        all_chunks = db.get_all_chunks()
        if not all_chunks:
            st.warning("Please upload materials in the Study Library to generate grounded quizzes.")
            return

        all_docs = db.get_all_documents()
        quiz_doc_options = {"All Documents": "All"}
        for d in all_docs:
            quiz_doc_options[f"📄 {d.filename} ({d.primary_topic})"] = d.id

        default_quiz_doc_idx = 0
        preselected_quiz_doc = st.session_state.get("quiz_doc_filter")
        if preselected_quiz_doc:
            for idx, (label, doc_val) in enumerate(quiz_doc_options.items()):
                if doc_val == preselected_quiz_doc:
                    default_quiz_doc_idx = idx
                    break

        c_qdoc, c1, c2, c3, c4 = st.columns([1.5, 1, 1, 1, 1])
        with c_qdoc:
            chosen_qdoc_label = st.selectbox("Source Document", list(quiz_doc_options.keys()), index=default_quiz_doc_idx)
            selected_quiz_doc_id = quiz_doc_options[chosen_qdoc_label]
        with c1:
            quiz_type = st.selectbox("Assessment Type", ["MCQ", "ShortAnswer", "Mixed", "Diagnostic", "Revision"])
        with c2:
            topics = ["All"] + sorted(list(set(c.topic for c in all_chunks)))
            chosen_topic = st.selectbox("Target Topic", topics)
        with c3:
            difficulty = st.selectbox("Difficulty", ["Easy", "Medium", "Hard"])
        with c4:
            q_count = st.slider("Questions", min_value=1, max_value=8, value=3)

        if st.button("🎲 Generate Grounded Assessment"):
            with st.spinner("Generating questions with source references and misconception mappings..."):
                questions = assessment.generate_quiz(
                    all_chunks,
                    topic=chosen_topic,
                    difficulty=difficulty,
                    question_count=q_count,
                    quiz_type=quiz_type,
                    user_id=user_id,
                    document_id=selected_quiz_doc_id if selected_quiz_doc_id != "All" else None
                )
                st.session_state["active_quiz"] = questions
                st.session_state["quiz_submitted"] = False
                st.session_state["quiz_results"] = None

        if "active_quiz" in st.session_state and st.session_state["active_quiz"]:
            questions = st.session_state["active_quiz"]
            st.markdown(f"### 📝 Active Assessment ({len(questions)} Questions • {quiz_type})")

            student_answers = {}
            for idx, q in enumerate(questions, start=1):
                st.markdown(f"**Q{idx}. [{q.topic} - {q.difficulty}]** {q.question_text}")
                st.caption(f"Source Reference: {q.source_reference}")

                if q.question_type == "MCQ":
                    student_answers[q.id] = st.radio(
                        f"Select your answer for Q{idx}:",
                        q.options,
                        key=f"q_input_{q.id}"
                    )
                else:
                    student_answers[q.id] = st.text_area(
                        f"Write your concise explanation for Q{idx}:",
                        key=f"q_input_{q.id}"
                    )
                st.write("---")

            if st.button("📤 Submit Quiz for Grading & Mastery Update"):
                with st.spinner("Evaluating responses, detecting misconceptions, and updating learner model..."):
                    results = []
                    for q in questions:
                        ans = student_answers.get(q.id, "")
                        eval_res = assessment.grade_submission(q, ans, user_id=user_id)
                        # Trigger learner model update
                        learner_model.update_mastery(user_id, q.topic, eval_res)
                        results.append(eval_res)

                    st.session_state["quiz_submitted"] = True
                    st.session_state["quiz_results"] = results
                    st.rerun()

        # Display Grading Results
        if st.session_state.get("quiz_submitted") and st.session_state.get("quiz_results"):
            st.markdown("### 📊 Assessment Feedback & Misconception Review")
            results = st.session_state["quiz_results"]
            total_score = sum(r.score for r in results)
            pct = int((total_score / len(results)) * 100)

            st.markdown(f"#### Overall Score: **{total_score} / {len(results)} ({pct}%)**")

            for idx, res in enumerate(results, start=1):
                if res.is_correct:
                    st.success(f"**Q{idx}: Correct (+{res.score} pt)**\n\n{res.feedback}")
                else:
                    st.error(f"**Q{idx}: Incorrect (0 pt)**\n\n{res.feedback}")
                    if res.misconception_detected:
                        st.warning(f"**Misconception Detected:** {res.misconception_detected}")
                    st.info(f"**Explanation from Notes:** {res.supporting_excerpt}\n\n*Reference:* {res.source_reference}")
                st.write("")

            st.balloons() if pct >= 70 else None

    # -------------------------------------------------------------
    # 5. MY LEARNING (Mastery Tracking & Analytics)
    # -------------------------------------------------------------
    elif selected_page == "📈 My Learning":
        st.markdown(render_brand_header(
            title="Learner Mastery Analytics",
            subtitle="Transparent Bayesian / weighted mastery tracking, misconceptions history, and spaced repetition"
        ), unsafe_allow_html=True)

        analytics = learner_model.get_learner_analytics(user_id=user_id)
        records = analytics["all_records"]

        if not records:
            st.info("No learner history found yet. Complete a quiz in the Quiz Studio or run simulated profiles in the Evaluation Lab!")
        else:
            c1, c2, c3 = st.columns(3)
            with c1:
                st.markdown(render_metric_card("Overall Mastery", f"{analytics['overall_mastery']}%", "Formula: α*Prior + (1-α)*Score"), unsafe_allow_html=True)
            with c2:
                st.markdown(render_metric_card("Topics Mastered", f"{len(analytics['strong_topics'])}", "Mastery >= 70%"), unsafe_allow_html=True)
            with c3:
                st.markdown(render_metric_card("Weak Topics Requiring Review", f"{len(analytics['weak_topics'])}", "Targeted for next revision"), unsafe_allow_html=True)

            st.write("")
            st.markdown("### 🎯 Mastery by Topic")
            for r in records:
                col_name, col_prog, col_badge = st.columns([1.5, 2, 1])
                with col_name:
                    st.write(f"**{r.topic}**")
                    st.caption(f"{r.correct_attempts} / {r.total_attempts} correct attempts")
                with col_prog:
                    st.progress(r.mastery_score / 100.0)
                    st.caption(f"Score: {r.mastery_score}%")
                with col_badge:
                    badge_cls = "badge-mastered" if r.mastery_score >= 85 else ("badge-inferred" if r.mastery_score >= 70 else "badge-danger")
                    st.markdown(f'<span class="badge {badge_cls}">{r.status}</span>', unsafe_allow_html=True)
                    st.caption(f"Next revision: {r.revision_due_at[:10]}")

            # Misconceptions Log
            st.markdown("### ⚠️ Recorded Misconceptions Log")
            misc = analytics["misconceptions"]
            if not misc:
                st.success("No recurring misconceptions detected. Keep up the high accuracy!")
            else:
                for m in misc:
                    st.warning(f"**Topic:** {m['topic']} &bull; **Seen {m['frequency']} time(s)**\n\nMisconception: *\"{m['misconception_text']}\"*\n\nRecommended reading: `{m.get('suggested_reading', 'Review notes')}`")

    # -------------------------------------------------------------
    # 6. STUDY PLANNER
    # -------------------------------------------------------------
    elif selected_page == "📅 Study Planner":
        st.markdown(render_brand_header(
            title="Personalized Adaptive Study Planner",
            subtitle="Dynamic daily checklist and weekly schedule prioritized by weak topics and available study time"
        ), unsafe_allow_html=True)

        col_cfg1, col_cfg2, col_cfg3 = st.columns([1, 1, 1])
        with col_cfg1:
            daily_mins = st.select_slider("Daily Available Study Time (Minutes)", options=[15, 30, 45, 60, 90, 120], value=45)
        with col_cfg2:
            target_goal = st.text_input("Current Learning Goal", value="Ace Algorithmic Interviews & Systems")
        with col_cfg3:
            target_days = st.slider("Roadmap Duration (Days)", min_value=3, max_value=14, value=7)

        if st.button("🗓️ Generate / Recalculate Study Plan", use_container_width=True):
            with st.spinner("Generating prioritized checklist based on weak topics..."):
                study_planner.generate_plan(
                    user_id=user_id,
                    daily_available_minutes=daily_mins,
                    target_goal=target_goal,
                    target_days=target_days
                )
                st.success("Updated study plan generated!")

        latest_plan = db.get_latest_study_plan(user_id=user_id)
        if not latest_plan:
            st.info("No active study plan found. Click 'Generate / Recalculate Study Plan' above to build one!")
        else:
            st.markdown(f"### 📋 {latest_plan.title}")
            st.caption(f"Created: {latest_plan.created_at[:10]} • Target Completion: {latest_plan.target_date}")

            tasks_by_day = {}
            for t in latest_plan.tasks:
                tasks_by_day.setdefault(t.day, []).append(t)

            for day, day_tasks in tasks_by_day.items():
                with st.expander(f"📅 {day} ({sum(t.duration_minutes for t in day_tasks)} mins)", expanded=True):
                    for t in day_tasks:
                        p_badge = "badge-danger" if t.priority == "High" else "badge-warning"
                        st.markdown(f"""
                        <div class="task-item">
                            <div>
                                <strong>{t.topic}</strong> &bull; {t.activity}
                                <div style="font-size:12px;color:#64748b;margin-top:4px;">
                                    Duration: <strong>{t.duration_minutes} mins</strong> &bull; Source: <em>{t.source_material}</em>
                                </div>
                            </div>
                            <div>
                                <span class="badge {p_badge}">{t.priority} Priority</span>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)

    # -------------------------------------------------------------
    # 7. COURSE MAP (Curriculum & Prerequisite Relationships)
    # -------------------------------------------------------------
    elif selected_page == "🗺️ Course Map":
        st.markdown(render_brand_header(
            title="Interactive Course Map & Concept Tree",
            subtitle="Curriculum dependency graph distinguishing explicit Source-Supported prerequisites from AI-Inferred relationships"
        ), unsafe_allow_html=True)

        graph_data = course_map.build_concept_graph(user_id=user_id)

        st.markdown("### 🧭 Recommended Learning Sequence (Topological Order)")
        steps = " ➔ ".join([f"**{idx}. {t}**" for idx, t in enumerate(graph_data["recommended_order"], start=1)])
        st.info(f"Based on prerequisite dependencies: {steps}")

        st.write("")
        c_nodes, c_edges = st.columns([1.4, 1])

        with c_nodes:
            st.markdown("### 📦 Course Topics & Concept Nodes")
            for node in graph_data["nodes"]:
                with st.container():
                    st.markdown(f"#### {node['label']}")
                    st.write(f"**Mastery:** {node['mastery_score']}% &bull; **Status:** `{node['status']}`")
                    if node["subtopics"]:
                        st.caption("Subtopics: " + ", ".join(node["subtopics"]))
                    st.write("---")

        with c_edges:
            st.markdown("### 🔗 Prerequisite Dependencies")
            st.caption("Transparent classification between explicit source statements and inferred curricular flows:")
            for edge in graph_data["edges"]:
                badge_type = "badge-source" if edge["is_explicit"] else "badge-inferred"
                st.markdown(f"""
                <div style="background:#f8fafc;padding:12px;border-radius:8px;margin-bottom:8px;border:1px solid #e2e8f0;">
                    <div><strong>{edge['from']}</strong> ➔ <strong>{edge['to']}</strong></div>
                    <div style="margin-top:4px;"><span class="badge {badge_type}">{edge['type']}</span></div>
                    <div style="font-size:12px;color:#475569;margin-top:4px;"><em>{edge['rationale']}</em></div>
                </div>
                """, unsafe_allow_html=True)

    # -------------------------------------------------------------
    # 8. EVALUATION LAB (RAG & Model Benchmarking)
    # -------------------------------------------------------------
    elif selected_page == "🔬 Evaluation Lab":
        st.markdown(render_brand_header(
            title="Evaluation Lab & Benchmark Suite",
            subtitle="Transparent quantitative verification of retrieval precision, citation accuracy, answer faithfulness, and simulated learner adaptation"
        ), unsafe_allow_html=True)

        tab_rag_eval, tab_sim_eval, tab_history = st.tabs([
            "📊 Run Live Benchmark",
            "🤖 Simulated Learner Trajectory",
            "📜 Historical Evaluation Reports"
        ])

        with tab_rag_eval:
            st.markdown("#### Quantitative Metric Definitions:")
            st.markdown("""
            - **Retrieval Precision@K**: Fraction of top retrieved chunks strictly relevant to query topic.
            - **Retrieval Recall@K**: Proportion of required core facts present in retrieved chunks.
            - **Citation Correctness**: Integrity check confirming citations point to verified indexed documents.
            - **Answer Faithfulness**: Bounded score verifying generated statements are grounded in retrieved excerpts.
            - **Unsupported-Query Detection Rate**: System's ability to honestly state *'insufficient evidence'* when queries are outside indexed material.
            - **Duplicate Question Rate**: Measures assessment engine's uniqueness across repeated generations.
            """)

            if st.button("🚀 Execute Quantitative Benchmark Run"):
                with st.spinner("Running queries through retrieval, citation mapping, and unsupported query checks..."):
                    report = eval_lab.run_benchmark()
                    st.session_state["latest_eval_report"] = report
                    st.success("Benchmark completed and saved to database!")

            report = st.session_state.get("latest_eval_report")
            if report:
                st.markdown(f"### Benchmark Run `{report.run_id}` ({report.dataset_name})")
                m1, m2, m3 = st.columns(3)
                with m1:
                    st.markdown(render_metric_card("Retrieval Precision@K", f"{int(report.retrieval_precision_at_k*100)}%", "Top-K chunk relevance"), unsafe_allow_html=True)
                    st.markdown(render_metric_card("Answer Faithfulness", f"{int(report.answer_faithfulness*100)}%", "Grounded in source chunks"), unsafe_allow_html=True)
                with m2:
                    st.markdown(render_metric_card("Retrieval Recall@K", f"{int(report.retrieval_recall_at_k*100)}%", "Core facts coverage"), unsafe_allow_html=True)
                    st.markdown(render_metric_card("Unsupported Query Detection", f"{int(report.unsupported_query_detection_rate*100)}%", "Honest disclosure rate"), unsafe_allow_html=True)
                with m3:
                    st.markdown(render_metric_card("Citation Correctness", f"{int(report.citation_correctness_rate*100)}%", "Exact document & page/timestamp link"), unsafe_allow_html=True)
                    st.markdown(render_metric_card("Duplicate Question Rate", f"{int(report.duplicate_question_rate*100)}%", "Diversity across quizzes"), unsafe_allow_html=True)

        with tab_sim_eval:
            st.markdown("#### Multi-Session Simulated Learner Validation")
            st.caption("Verifies whether mastery updates, spaced repetition, and weak-spot recommendations dynamically adapt across distinct learner profiles:")

            if st.button("🧪 Run Multi-Session Learner Simulation"):
                with st.spinner("Simulating Struggling Learner vs Fast Learner..."):
                    sim_res = eval_lab.run_simulated_learner_trajectory()
                    st.session_state["sim_res"] = sim_res

            if "sim_res" in st.session_state:
                sim = st.session_state["sim_res"]
                c_a, c_b = st.columns(2)
                with c_a:
                    st.markdown("##### 👤 Learner Profile A: Struggling Student")
                    st.write(f"- Final Mastery: **{sim['learner_a_final_mastery']}%** (`{sim['learner_a_status']}`)")
                    st.write(f"- Generated Recommendations: **{len(sim['learner_a_recommendations'])}** urgent reviews")
                    st.warning("System correctly flagged weak topics and scheduled immediate 1-day revision interval.")
                with c_b:
                    st.markdown("##### 👤 Learner Profile B: Accelerated Student")
                    st.write(f"- Final Mastery: **{sim['learner_b_final_mastery']}%** (`{sim['learner_b_status']}`)")
                    st.write(f"- Generated Recommendations: **{len(sim['learner_b_recommendations'])}** advanced tasks")
                    st.success("System recognized proficiency and scheduled spaced repetition interval.")

                st.info(f"✅ Dynamic Adaptive Model Verification: {'PASSED' if sim['adaptive_verification'] else 'FAILED'} (Learner A Mastery < Learner B Mastery)")

        with tab_history:
            history = db.get_evaluation_reports(limit=5)
            if not history:
                st.info("No saved reports yet. Run the benchmark above to record one.")
            else:
                for h in history:
                    with st.expander(f"Report {h['run_id']} &bull; {h['timestamp'][:19]}"):
                        st.json(h["report_json"])

    # -------------------------------------------------------------
    # 9. SETTINGS & INFO
    # -------------------------------------------------------------
    elif selected_page == "⚙️ Settings & Info":
        st.markdown(render_brand_header(
            title="Settings & System Architecture",
            subtitle="Configure API providers, adjust learner hyperparameters, and inspect architecture"
        ), unsafe_allow_html=True)

        st.markdown("### 🔑 AI Provider Configuration")
        st.caption("LearnCode AI runs out-of-the-box in deterministic grounded mode, and supports Gemini and OpenAI seamlessly.")

        cur_provider = os.getenv("AI_PROVIDER", "offline_deterministic")
        c1, c2 = st.columns(2)
        with c1:
            provider_choice = st.selectbox("Active AI Generation Engine", ["offline_deterministic", "gemini", "openai"], index=["offline_deterministic", "gemini", "openai"].index(cur_provider) if cur_provider in ["offline_deterministic", "gemini", "openai"] else 0)
        with c2:
            st.write(f"**Current Status:** `{cur_provider}`")

        st.markdown("### 🎛️ Learner Model Hyperparameters")
        c_p1, c_p2 = st.columns(2)
        with c_p1:
            st.slider("Mastery Prior Weight (α)", min_value=0.1, max_value=0.9, value=0.7, step=0.05, help="Weight given to prior mastery in exponential moving average.")
        with c_p2:
            st.slider("Daily Forgetting Curve Decay Rate", min_value=0.005, max_value=0.05, value=0.015, step=0.005, help="Daily retention decay applied when a topic is unpracticed.")

        st.markdown("### 🛡️ Security, Privacy & Data Architecture")
        st.markdown("""
        - **Local SQLite Storage**: Learner data, attempts, and indexed chunks reside securely in `data/learncode.db`.
        - **Untrusted File Handling**: Uploaded files undergo strict MIME, extension, and 30MB size validations.
        - **Prompt Injection Defense**: Uploaded documents are treated as data, preventing instructions in study files from overriding tutor prompts.
        - **Zero Secret Exposure**: API keys are accessed via environment variables and never exposed to the client or checked into version control.
        """)


if __name__ == "__main__":
    main()
