# TEMPORARY FOR TESTING
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import streamlit as st
import requests
from streamlit.runtime.scriptrunner import get_script_run_ctx
from streamlit_extras.stylable_container import stylable_container

temp_jobs = st.session_state["best_jobs"]

# ===================================== Helper Functions =====================================
def get_session_id():
    "Retrieves the unique session ID for the current user's browser tab."
    ctx = get_script_run_ctx()
    if ctx is None:
        raise Exception("Failed to get the script run context")
    return ctx.session_id


# ===================================== Streamlit UI =====================================
st.title("Specify your Job")

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
    .job-card-container [data-testid="stVerticalBlockBorderConfigured"] {
        background-color: var(--bg-card) !important;
        border: 1px solid var(--border-soft) !important;
        border-radius: var(--radius-lg) !important;
        padding: 22px 24px !important;
        margin-bottom: 20px !important;
        transition: transform 0.15s ease, border 0.15s ease;
    }

    .job-card-container [data-testid="stVerticalBlockBorderConfigured"]:hover {
        transform: translateY(-2px) !important;
        border-color: var(--accent) !important;
    }

    .job-card-container [data-testid="stVerticalBlockBorderConfigured"]:has(details[open]) {
    transform: none;
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

    .job-actions {
        margin-top: 16px;
        display: flex;
        justify-content: flex-start;
    }

    .job-actions .stButton > button {
        background-color: var(--accent);
        color: #0b0f14;
        border-radius: 999px;
        font-weight: 600;
        padding: 0.55rem 1.4rem;
        box-shadow: 0 8px 24px rgba(108,140,255,0.25);
    }

    .job-actions .stButton > button:hover {
        background-color: var(--accent-hover);
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

with st.expander("Read Explanation"):
    st.write(
        """
Use this tool to further specify your recommended jobs by simply writing the command you wish the agent to do.
There are three query approaches: 

**[Build upon your current list]**

**[Find new jobs based on CV]**

**[Find specific jobs you want]**

Here are examples of how to query for each approach:

[Building upon provided list of jobs]:
- "I like these jobs, but I only want the ones with a provided salary."
- "I only want the jobs that are provided in Jakarta."
- "I only want Hybrid-type jobs."

[Find new jobs based on CV]:
- "Find new jobs that match my CV but are only in Jakarta."
- "None of these jobs fit me. Find new jobs."

[Find specific jobs you want]:
- "Find me new jobs fit for a computer science student thats in Jakarta and has a listed salary."

Tip: Use the keyword 'new' to find new jobs or specific jobs.
"""
    )
user_input = st.text_input("Specify your reccommended job list:", value=None ,placeholder="eg. \"Find new jobs that match my CV but are available in Jakarta.\"")


# On user input
if user_input is not None:
    initial_state = {
        'query': user_input,
        'summary': st.session_state["user_summary"],
        'best_jobs': st.session_state["best_jobs"],
        'messages': []
    }

    request = requests.post(
        "http://localhost:8000/job-search",
        json=initial_state
    )

    try:
        data = request.json()
    except Exception as e:
        print(e)
        print(request)

    try:
        temp_jobs = data["best_jobs"]
    except Exception:
        print("Error ocurred. This what data looks like")
        print(data)

    if not temp_jobs or data["messages"][-2]["content"] == "Null intent":
        with st.chat_message("ai"):
            st.write(data["messages"][-1]["content"])


# Display Current Jobs List
st.markdown(
    """
    <div class="section-title">
        Your Current Jobs List
    </div>
    """,
    unsafe_allow_html=True,
)


for i, job in enumerate(temp_jobs):
    with stylable_container(
        key=f"job_card_{i}",
        css_styles=[
            # job-card
            """
            {
                background-color: #161d2f;
                border: 1px solid rgba(255,255,255,0.06);
                border-radius: 18px;
                padding: 22px 24px;
                margin-bottom: 20px;
                transition: transform 0.15s ease;

                    &:hover {
                    transform: translateY(-2px);
                    border-color: #6c8cff;
                }
            }
            """,

            # fix the Button Overlap
            """
            div[data-testid="stButton"] {
                margin-top: 40px;
                display: block;
            }
            """
        ]
    ):
        st.markdown(
            f"""
            <div class="job-title">{job["job_title"]}</div>
            <div class="job-meta">
                {job["company_name"]} &nbsp;|&nbsp;
                {job["work_type"]} &nbsp;|&nbsp;
                {job["work_style"]} &nbsp;|&nbsp;
                {job["salary"]} &nbsp;|&nbsp;
                {job["location"]}
            </div>
            <div class="job-actions" id="job-action-{i}"></div>
            <details class="job-details">
                <summary>Read more</summary>
                <div class="job-details-content">
                    {job["job_description"]}
                </div>
            </details>
            """,
            unsafe_allow_html=True
        )

        if st.button("Prepare for this job", key=f"job_btn_{i}"):
            st.session_state['prefered_jobs'] = {
                "job_title": job['job_title'],
                "company_name": job['company_name'],
                "job_description": job['job_description']
            }
            st.session_state['last_consulted_job_title'] = ""
            st.switch_page("pages/04_AIConsultant.py")



if not temp_jobs:
    left_co, cent_co, last_co = st.columns([1, 2, 1])

    with cent_co:
        # Use st.info or st.warning for a "pre-packaged" cute look
        st.info("No data found!", icon="🔍")