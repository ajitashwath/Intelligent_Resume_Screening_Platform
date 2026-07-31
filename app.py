import streamlit as st
import fitz
import pandas as pd

from matcher import compute_match_score, rank_candidates
from extractor import extract_skills_by_category

st.set_page_config(
    page_title="AI Resume Screening Platform",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }
    
    .metric-container {
        background: rgba(255, 255, 255, 0.03);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 12px;
        padding: 18px;
        text-align: center;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
    }
    .metric-value {
        font-size: 2.2rem;
        font-weight: 700;
        margin-bottom: 4px;
    }
    .metric-label {
        font-size: 0.85rem;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        opacity: 0.8;
    }
    
    .skill-pill {
        display: inline-block;
        padding: 5px 12px;
        margin: 3px;
        border-radius: 20px;
        font-size: 0.82rem;
        font-weight: 500;
    }
    .pill-matched {
        background-color: rgba(34, 197, 94, 0.15);
        color: #4ADE80;
        border: 1px solid rgba(34, 197, 94, 0.3);
    }
    .pill-missing {
        background-color: rgba(239, 68, 68, 0.15);
        color: #F87171;
        border: 1px solid rgba(239, 68, 68, 0.3);
    }
    .pill-cat {
        background-color: rgba(56, 189, 248, 0.15);
        color: #38BDF8;
        border: 1px solid rgba(56, 189, 248, 0.3);
    }
</style>
""", unsafe_allow_html=True)

def extract_text_from_upload(uploaded_file) -> str:
    try:
        pdf_bytes = uploaded_file.read()
        doc = fitz.open(stream=pdf_bytes, filetype="pdf")
        text = ""
        for page in doc:
            text += page.get_text()
        doc.close()
        return text.strip()
    except Exception as e:
        st.error(f"Error processing {uploaded_file.name}: {e}")
        return ""

def render_badges(items: list[str], pill_class: str) -> str:
    if not items:
        return "<em>None detected</em>"
    return "".join([f'<span class="skill-pill {pill_class}">{item}</span>' for item in items])

with st.sidebar:
    st.title("Resume Matcher")
    st.caption("AI-powered candidate screening")
    
    st.divider()
    
    st.markdown("### Scoring Weights")
    semantic_w = st.slider("Semantic Similarity", 0.0, 1.0, 0.6, step=0.1)
    skill_w = round(1.0 - semantic_w, 1)
    st.caption(f"Skill Overlap Weight: **{skill_w}**")
    
    st.divider()
    st.markdown("""
    **How it works:**
    1. Paste the target **Job Description**.
    2. Upload one or more **Resume PDFs**.
    3. Click **Analyze Candidates** to view rankings and skill overlap.
    """)

st.title("Intelligent Resume Screening Platform")
st.markdown("Upload candidate resumes and compare them against your target job requirements.")

st.write("")

col1, col2 = st.columns([1, 1], gap="medium")

with col1:
    st.subheader("1. Job Description")
    default_jd = """We are looking for a Software Engineer with experience in Python,
Java, SQL, REST APIs, Git, Linux, Docker, AWS and problem solving.
Experience with Machine Learning is a plus."""
    
    job_description = st.text_area(
        "Paste Job Description",
        value=default_jd,
        height=240,
        placeholder="Enter detailed job description...",
        help="Paste the requirements and skills for the role."
    )

with col2:
    st.subheader("2. Candidate Resumes")
    uploaded_files = st.file_uploader(
        "Upload Resume PDFs",
        type=["pdf"],
        accept_multiple_files=True,
        help="You can upload multiple resumes for batch comparison."
    )
    
    if uploaded_files:
        st.success(f"**{len(uploaded_files)}** file(s) attached")

st.write("")
analyze_btn = st.button("Analyze Candidates", type="primary", use_container_width=True)

if analyze_btn:
    if not job_description.strip():
        st.warning("Please provide a valid Job Description.")
    elif not uploaded_files:
        st.warning("Please upload at least one Resume PDF.")
    else:
        with st.spinner("Processing resumes and computing AI match scores..."):
            results = []
            
            for file in uploaded_files:
                resume_text = extract_text_from_upload(file)
                if not resume_text:
                    continue
                
                match_res = compute_match_score(
                    resume_text,
                    job_description,
                    semantic_weight=semantic_w,
                    skill_weight=skill_w
                )
                
                categorized = extract_skills_by_category(resume_text)
                
                results.append({
                    "name": file.name,
                    "text": resume_text,
                    "match_score": match_res.match_score,
                    "semantic_score": match_res.semantic_score,
                    "skill_overlap_score": match_res.skill_overlap_score,
                    "matched_skills": match_res.matched_skills,
                    "missing_skills": match_res.missing_skills,
                    "categorized_skills": categorized
                })
            
            st.session_state["results"] = rank_candidates(results)

if "results" in st.session_state and st.session_state["results"]:
    results = st.session_state["results"]
    st.divider()
    
    if len(results) > 1:
        st.header("Candidate Rankings")
        
        df_summary = pd.DataFrame([
            {
                "Rank": idx + 1,
                "Candidate File": r["name"],
                "Overall Match": f"{r['match_score']:.1f}%",
                "Semantic Score": f"{r['semantic_score']:.1f}%",
                "Skill Overlap": f"{r['skill_overlap_score']:.1f}%",
                "Matched Skills": len(r["matched_skills"]),
                "Missing Skills": len(r["missing_skills"]),
            }
            for idx, r in enumerate(results)
        ])
        
        st.dataframe(df_summary, use_container_width=True, hide_index=True)
        st.divider()
    
    st.header("Detailed Match Analysis")
    
    candidate_names = [r["name"] for r in results]
    selected_name = st.selectbox("Select Candidate to Inspect:", candidate_names)
    
    selected_candidate = next(c for c in results if c["name"] == selected_name)
    
    m1, m2, m3 = st.columns(3)
    
    with m1:
        st.markdown(f"""
        <div class="metric-container">
            <div class="metric-value" style="color: #38BDF8;">{selected_candidate['match_score']:.1f}%</div>
            <div class="metric-label">Overall Match Score</div>
        </div>
        """, unsafe_allow_html=True)
        st.progress(min(selected_candidate['match_score'] / 100.0, 1.0))

    with m2:
        st.markdown(f"""
        <div class="metric-container">
            <div class="metric-value" style="color: #818CF8;">{selected_candidate['semantic_score']:.1f}%</div>
            <div class="metric-label">Semantic Relevance</div>
        </div>
        """, unsafe_allow_html=True)
        st.progress(min(selected_candidate['semantic_score'] / 100.0, 1.0))

    with m3:
        st.markdown(f"""
        <div class="metric-container">
            <div class="metric-value" style="color: #4ADE80;">{selected_candidate['skill_overlap_score']:.1f}%</div>
            <div class="metric-label">Skill Overlap</div>
        </div>
        """, unsafe_allow_html=True)
        st.progress(min(selected_candidate['skill_overlap_score'] / 100.0, 1.0))

    st.write("")
    st.write("")

    tab_skills, tab_categories, tab_text = st.tabs(["Skill Match Breakdown", "Skills by Category", "Extracted Resume Text"])

    with tab_skills:
        col_matched, col_missing = st.columns(2)
        
        with col_matched:
            st.markdown(f"### Matched Skills ({len(selected_candidate['matched_skills'])})")
            st.markdown(
                render_badges(selected_candidate["matched_skills"], "pill-matched"),
                unsafe_allow_html=True
            )
            
        with col_missing:
            st.markdown(f"### Missing Skills ({len(selected_candidate['missing_skills'])})")
            st.markdown(
                render_badges(selected_candidate["missing_skills"], "pill-missing"),
                unsafe_allow_html=True
            )

    with tab_categories:
        st.markdown("### Detected Skills by Category")
        cat_data = selected_candidate.get("categorized_skills", {})
        if not cat_data:
            st.info("No categorized skills detected in resume.")
        else:
            for cat_name, skill_list in cat_data.items():
                st.markdown(f"**{cat_name}**")
                st.markdown(
                    render_badges(skill_list, "pill-cat"),
                    unsafe_allow_html=True
                )
                st.write("")

    with tab_text:
        st.text_area(
            label="Raw Extracted Text",
            value=selected_candidate["text"],
            height=300,
            disabled=True
        )