import streamlit as st
import pandas as np
import numpy as np

# st.title("Hello! What would you like to do?")

# if st.button("Home"):
#     st.switch_page("your_app.py")
# if st.button("Chat"):
#     st.switch_page("pages/01_ChattingPage.py")
# if st.button("Search Jobs"):
#     st.switch_page("pages/02_JobSearch.py")
# if st.button("Analyze CV"):
#     st.switch_page("pages/03_CVAnalyzer.py")
# if st.button("AI Consultant"):
#     st.switch_page("pages/04_AIConsultant.py")
# if st.button("Mock Interview"):
#     st.switch_page("pages/05_MockInterview.py")

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

st.switch_page("pages/03_CVAnalyzer.py")
# st.markdown(
#     """
#     <style>
#         [data-testid="stSidebar"] {
#             display: none;
#         }

#         [data-testid="collapsedControl"] {
#             display: none;
#         }
#     </style>
#     """,
#     unsafe_allow_html=True,
# )