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
from data.database import save_user_data




# ======================================================= Internal Variables =======================================================

BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")

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
    :root {
        --bg-main: #0b0f14;
        --bg-surface: #121826;
        --bg-card: #161d2f;

        --text-main: #e8ebf3;
        --text-muted: #9aa3b2;

        --accent: #6c8cff;
        --accent-hover: #7f9bff;
        --accent-soft: rgba(108, 140, 255, 0.15);

        --border-soft: rgba(255,255,255,0.06);
        --radius-lg: 18px;
        --radius-md: 14px;
    }

    section[data-testid="stSidebar"] {
        background-color: var(--bg-surface);
    }

    html, body, .stApp {
        background-color: var(--bg-main);
        color: var(--text-main);
    }

    .block-container {
        max-width: 900px;
        padding-top: 2.5rem;
        padding-bottom: 3rem;
    }

    /* Insight / surface cards */
    .surface {
        background-color: var(--bg-card);
        border: 1px solid var(--border-soft);
        border-radius: var(--radius-lg);
        padding: 28px;
        margin-bottom: 40px;
    }

    /* Section titles */
    .section-title {
        text-align: center;
        font-size: 34px;
        font-weight: 700;
        margin-bottom: 32px;
    }

    /* Job card */
    .job-card {
        background-color: var(--bg-card);
        border: 1px solid var(--border-soft);
        border-radius: var(--radius-lg);
        padding: 22px 24px;
        margin-bottom: 20px;
        transition: transform 0.15s ease, border 0.15s ease;
    }

    .job-card:hover {
        transform: translateY(-2px);
        border-color: var(--accent);
    }

    .job-title {
        font-size: 20px;
        font-weight: 600;
        margin: 0;
    }

    .job-meta {
        margin-top: 6px;
        font-size: 14px;
        color: var(--text-muted);
    }

    /* Job description dropdown */
    .job-details {
        margin-top: 14px;
    }

    .job-details summary {
        cursor: pointer;
        font-size: 14px;
        font-weight: 500;
        color: var(--accent);
        list-style: none;
        display: flex;
        gap: 6px;
        align-items: center;
    }

    .job-details summary::-webkit-details-marker {
        display: none;
    }

    .job-details summary::before {
        content: "▸";
        transition: transform 0.2s ease;
    }

    .job-details[open] summary::before {
        transform: rotate(90deg);
    }

    .job-details-content {
        margin-top: 12px;
        font-size: 14px;
        line-height: 1.6;
        color: var(--text-muted);
    }

    /* Buttons */
    .stButton > button {
        background-color: var(--accent);
        color: #0b0f14;
        border-radius: var(--radius-md);
        border: none;
        font-weight: 600;
        padding: 0.6rem 1.3rem;
    }

    .stButton > button:hover {
        background-color: var(--accent-hover);
    }

    /* Floating proceed button */
    .bottom-right-button {
        position: fixed;
        bottom: 24px;
        right: 24px;
        z-index: 999;
    }
    </style>
    """,
    unsafe_allow_html=True
)


# Upload CV
uploaded_file = st.file_uploader(
    "📄 Upload CV…",
    type=["pdf"],
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
        f"{BACKEND_URL}/analyze-cv",
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

    mongo_payload = {
        "user_name": data["user_name"],
        "user_summary": data["summary"],
        "assessment": data["assessment"],
        "session_id": data["session_id"],  
        "best_jobs": data["best_jobs"]
    }

    save_user_data(mongo_payload)


# Update local variables
MBTI = st.session_state["assessment"][0:7]
ASSESSMENT = st.session_state["assessment"][7:]
DUMMY_JOBS = st.session_state["best_jobs"]


# Personality Insight Card
st.markdown(
    f"""
    <div class="surface">
        <div style="font-size:42px; font-weight:800; margin-bottom:8px;">
            {MBTI}
        </div>
        <p style="color:var(--text-muted); line-height:1.7; font-size:16px; margin:0;">
            {ASSESSMENT}
        </p>
    </div>
    """,
    unsafe_allow_html=True
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

for job in DUMMY_JOBS:
    st.markdown(
        f"""
        <div class="job-card">
            <div class="job-title">{job["job_title"]}</div>
            <div class="job-meta">
                {job["company_name"]} &nbsp;|&nbsp;
                {job["work_type"]} &nbsp;|&nbsp;
                {job["work_style"]} &nbsp;|&nbsp;
                {job["salary"]} &nbsp;|&nbsp;
                {job["location"]}
            </div>
            <details class="job-details">
                <summary>Read more</summary>
                <div class="job-details-content">
                    {job["job_description"]}
                </div>
            </details>
        </div>
        """,
        unsafe_allow_html=True
    )



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