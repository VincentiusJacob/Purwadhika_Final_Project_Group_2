# TEMPORARY FOR TESTING
import sys
from pathlib import Path
import os
import json

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


import streamlit as st
import requests
import base64
from streamlit.runtime.scriptrunner import get_script_run_ctx


# ======================================================= Internal Variables =======================================================

DB_FILE = "user_data.json"

DB_FILE = "user_data.json"

MBTI = "ENTP-T" # Example

ASSESSMENT = (
    "You are an ENTP-T. Your personality type is characterized by a natural curiosity "
    "and a love for exploring new ideas and possibilities. You thrive in environments "
    "that challenge your intellect and allow you to express your creativity. "
    "Your enthusiasm and quick wit make you a natural leader, easily able to inspire "
    "and motivate others."
) # Example

# Dummy job data
DUMMY_JOBS = [
    {
        "job_title": "Product Manager",
        "company_name": "Tokopedia",
        "work_type": "Hybrid",
        "salary": "IDR 15–25M",
        "location": "Jakarta",
        "job_desc": (
            "Lead cross-functional teams to build impactful products. "
            "You will define product vision, work with engineering, "
            "and drive execution from ideation to launch."
        ),
    },
    {
        "job_title": "AI Consultant",
        "company_name": "Accenture",
        "work_type": "On-site",
        "salary": "IDR 20–30M",
        "location": "Jakarta",
        "job_desc": (
            "Work with enterprise clients to design AI-driven solutions. "
            "Translate business problems into technical architectures "
            "and guide implementation strategies."
        ),
    },
]


# ======================================================= Helper Functions =======================================================


def truncate_text(text, max_chars=220):
    if len(text) <= max_chars:
        return text, False
    return text[:max_chars].rsplit(" ", 1)[0] + "...", True


def get_session_id():
    "Retrieves the unique session ID for the current user's browser tab."
    ctx = get_script_run_ctx()
    if ctx is None:
        raise Exception("Failed to get the script run context")
    return ctx.session_id


# ======================================================= Streamlit UI =======================================================

# Page Config
st.set_page_config(
    page_title="CV Analyzer",
    layout="centered",
)
st.title("Analyze your CV")


# Global CSS
st.markdown(
    """
    <style>
    body {
        background-color: #0f1220;
    }

    .upload-card {
        background: #5a5f73;
        padding: 22px;
        border-radius: 999px;
        text-align: center;
        margin-bottom: 30px;
    }

    .insight-card {
        background: #2f3446;
        padding: 28px;
        border-radius: 22px;
        margin-bottom: 40px;
    }

    .insight-grid {
        display: grid;
        grid-template-columns: 120px 1fr;
        gap: 20px;
        align-items: start;
    }

    .mbti {
        font-size: 42px;
        font-weight: 700;
        color: white;
    }

    .divider {
        width: 1px;
        background: #6f7388;
        height: 100%;
    }

    .assessment {
        color: #cfd3e0;
        line-height: 1.6;
    }

    .section-title {
        text-align: center;
        font-size: 36px;
        font-weight: 700;
        color: white;
        margin-bottom: 30px;
    }

    .job-card {
        background: #3a3f52;
        padding: 26px;
        border-radius: 22px;
        margin-bottom: 22px;
    }

    .job-title {
        font-size: 22px;
        font-weight: 700;
        color: white;
    }

    .job-meta {
        color: #b7bccb;
        font-size: 14px;
        margin-bottom: 12px;
    }

    details > summary {
        cursor: pointer;
        list-style: none;
        color: #cfd3e0;
        font-size: 14px;
    }

    details > summary::-webkit-details-marker {
        display: none;
    }

    .job-desc {
        color: #cfd3e0;
        line-height: 1.6;
        margin-top: 10px;
    }

    .bottom-right-button {
        position: fixed;
        bottom: 24px;
        right: 24px;
        z-index: 9999;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Upload CV
uploaded_file = st.file_uploader(
    "📄 Upload CV…",
    type=["pdf", "docx"],
    label_visibility="collapsed",
)

# Cache uploaded file in session state
if uploaded_file and "file_cached" not in st.session_state:
    st.session_state["file_cached"] = uploaded_file.getvalue()

# If cache is not detected, stop the rest of the program from running.
if "file_cached" not in st.session_state:
    st.stop()

# If user uploads CV
if "analysis_done" not in st.session_state:
    file_as_bytes = st.session_state["file_cached"]

    initial_state = {
        "summary": "",
        "user_name": "",
        "cv_contents": "",
        "best_jobs": [],
        "file_bytes": base64.b64encode(file_as_bytes).decode("utf-8"),
        "session_id": get_session_id(),
        "assessment": ""
    }

    request = requests.post(
        "http://localhost:8000/analyze-cv",
        json=initial_state
    )

    data = request.json()

    # Update session state values
    st.session_state["user_summary"] = data["summary"]
    st.session_state["user_name"] = data["user_name"]
    st.session_state["best_jobs"] = data["best_jobs"]
    st.session_state["session_id"] = data["session_id"]
    st.session_state["assessment"] = data["assessment"]
    st.session_state["analysis_done"] = True


# Update local variables
MBTI = st.session_state["assessment"][0:7]
ASSESSMENT = st.session_state["assessment"][7:]
DUMMY_JOBS = st.session_state["best_jobs"]


# Personality Insight Card
st.markdown(
    f"""
    <div style="
        background:#2f3446;
        padding:32px;
        border-radius:22px;
        margin-bottom:40px;
    ">
        <div style="
            font-size:42px;
            font-weight:800;
            color:white;
            margin-bottom:8px;
        ">
            {MBTI}
        </div> 
        <p style="
            color:#cfd3e0;
            line-height:1.7;
            font-size:16px;
            margin:0;
        ">
            {ASSESSMENT}
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)


# Recommended Jobs
st.markdown(
    """
    <div class="section-title">
        Recommended Jobs
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown("""
<style>
    div[data-testid="stVerticalBlockBorderWrapper"] {
        background-color: #0E1117; 
        border: 1px solid #303030;
        border-radius: 10px;
        padding: 20px;
        margin-bottom: 15px;
    }

    div.stButton > button {
        width: 100%;
        background-color: #FF4B4B;
        color: white;
        border: none;
    }
</style>
""", unsafe_allow_html=True)

for i, job in enumerate(DUMMY_JOBS):

    with st.container(border=True):
        st.markdown(f"""
            <div style="margin-bottom: 4px;">
                <h3 style="margin:0; font-size:20px;">{job["job_title"]}</h3>
                <div style="color: grey; font-size: 14px; margin-top: 5px;">
                    {job["company_name"]} &nbsp;|&nbsp;
                    {job["work_type"]} &nbsp;|&nbsp;
                    {job["salary"]} &nbsp;|&nbsp;
                    {job["location"]}
                </div>
            </div>
        """, unsafe_allow_html=True)

        if st.button("Prepare for this job", key=f"job_btn_{i}"):
            st.session_state['prefered_jobs'] = {
                "job_title": job['job_title'],
                "company_name": job['company_name'],
                "job_description": job['job_description']
            }
      
            st.session_state['last_consulted_job_title'] = "" 
            
            st.success("Data is updated, You are ready for consulting and practice interview.")

        st.markdown(f"""
            <details style="margin-top: 15px; cursor: pointer; margin-bottom:10px;">
                <summary style="color: #4DA6FF;">▼ Read more</summary>
                <div style="margin-top: 10px; font-size: 14px; line-height: 1.6;">
                    {job["job_description"]}
                </div>
            </details>
        """, 
        unsafe_allow_html=True
    )



# Show button to proceed to next step
st.markdown('<div class="bottom-right-button">', unsafe_allow_html=True)
if st.button("Proceed", use_container_width=False):
    st.switch_page("pages/02_JobSearch.py")
st.markdown("</div>", unsafe_allow_html=True)



# Show button to proceed to next step
st.markdown('<div class="bottom-right-button">', unsafe_allow_html=True)
if st.button("Proceed", use_container_width=False):
    st.switch_page("pages/02_JobSearch.py")
st.markdown("</div>", unsafe_allow_html=True)


if __name__ == "__main__":
    # try:
    #     if uploaded_file is not None:
    #         file_as_bytes = uploaded_file.getvalue()

    #         initial_state: State = {
    #         "summary": "",
    #         "cv_contents": "",
    #         "best_jobs": [],
    #         "file_bytes": file_as_bytes,
    #         "session_id": 1,
    #         "assessment": ""
    #     }

    #     request = analysis_compile(initial_state)
    #     print(request["assessment"], request["best_jobs"][0])

    # except Exception:
    #     pass
    pass