# TEMPORARY FOR TESTING
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import streamlit as st
import requests
from streamlit.runtime.scriptrunner import get_script_run_ctx

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


# Global CSS
st.markdown(
    """
    <style>
    body {
        background-color: #0f1220;
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
    </style>
    """,
    unsafe_allow_html=True
    )


# Display Current Jobs List
st.markdown(
    """
    <div class="section-title">
        Your Current Jobs List
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

for i, job in enumerate(temp_jobs):
    with st.container(border=True):
        st.markdown(f"""
            <div style="margin-bottom: 4px;">
                <h3 style="margin:0; font-size:20px;">{job["job_title"]}</h3>
                <div style="color: grey; font-size: 14px; margin-top: 5px;">
                    {job["company_name"]} &nbsp;|&nbsp;
                    {job["work_type"]} &nbsp;|&nbsp;
                    {job["work_style"]} &nbsp;|&nbsp;
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
            st.switch_page("pages/04_AIConsultant.py")

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


if not temp_jobs:
    left_co, cent_co, last_co = st.columns([1, 2, 1])

    with cent_co:
        # Use st.info or st.warning for a "pre-packaged" cute look
        st.info("No data found!", icon="🔍")