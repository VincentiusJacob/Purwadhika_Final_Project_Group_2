import streamlit as st

# -------------------------------------------------
# Page config
# -------------------------------------------------
st.set_page_config(
    page_title="UI Style Board",
    layout="wide"
)

# -------------------------------------------------
# GLOBAL DESIGN SYSTEM (CSS)
# -------------------------------------------------
st.markdown(
    """
    <style>
    /* ===============================
       DESIGN TOKENS
    =============================== */
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
        --radius-sm: 10px;
    }

    /* ===============================
       GLOBAL RESET / IDENTITY WIPE
    =============================== */
    html, body, .stApp {
        background-color: var(--bg-main);
        color: var(--text-main);
    }

    section[data-testid="stSidebar"] {
        background-color: var(--bg-surface);
    }

    .block-container {
        padding-top: 2.5rem;
        padding-bottom: 3rem;
        max-width: 1200px;
    }

    /* ===============================
       TYPOGRAPHY
    =============================== */
    h1, h2, h3 {
        font-weight: 600;
        letter-spacing: -0.02em;
        margin-bottom: 0.4rem;
    }

    .muted {
        color: var(--text-muted);
        font-size: 14px;
    }

    /* ===============================
       SURFACES / CARDS
    =============================== */
    .surface {
        background-color: var(--bg-card);
        border: 1px solid var(--border-soft);
        border-radius: var(--radius-lg);
        padding: 20px 22px;
    }

    .surface + .surface {
        margin-top: 20px;
    }

    /* ===============================
       JOB CARD
    =============================== */
    .job-card {
        background-color: var(--bg-card);
        border: 1px solid var(--border-soft);
        border-radius: var(--radius-lg);
        padding: 18px 20px;
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
        line-height: 1.4;
    }

    /* ===============================
        JOB DESCRIPTION DROPDOWN
    =============================== */

    .job-details {
        margin-top: 14px;
    }

    .job-details summary {
        list-style: none;
        cursor: pointer;
        font-size: 14px;
        font-weight: 500;
        color: var(--accent);
        display: flex;
        align-items: center;
        gap: 6px;
        user-select: none;
    }

    .job-details summary::-webkit-details-marker {
        display: none;
    }

    /* Chevron */
    .job-details summary::before {
        content: "▸";
        display: inline-block;
        transition: transform 0.2s ease;
    }

    /* Rotate when open */
    .job-details[open] summary::before {
        transform: rotate(90deg);
    }

    .job-details-content {
        margin-top: 12px;
        font-size: 14px;
        line-height: 1.6;
        color: var(--text-muted);
    }


    /* ===============================
       BUTTONS
    =============================== */
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

    /* ===============================
       ALERTS
    =============================== */
    div[data-testid="stAlert"] {
        background-color: #1a2135;
        border: 1px solid var(--border-soft);
        border-radius: var(--radius-md);
        color: var(--text-muted);
    }

    /* ===============================
       CHAT
    =============================== */
    .chat-user {
        background: var(--accent-soft);
        border-left: 3px solid var(--accent);
        border-radius: var(--radius-md);
        padding: 12px 14px;
        margin-bottom: 12px;
        font-size: 15px;
    }

    .chat-ai {
        background: var(--bg-card);
        border: 1px solid var(--border-soft);
        border-radius: var(--radius-md);
        padding: 12px 14px;
        margin-bottom: 12px;
        font-size: 15px;
    }

    /* ===============================
       CHAT INPUT
    =============================== */
    div[data-testid="stChatInput"] textarea {
        background-color: var(--bg-card);
        color: var(--text-main);
        border-radius: var(--radius-lg);
        border: 1px solid var(--border-soft);
        padding: 12px;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# -------------------------------------------------
# STYLE BOARD CONTENT
# -------------------------------------------------
st.title("UI Style Board")
st.markdown(
    "<p class='muted'>All recurring UI elements used across the project</p>",
    unsafe_allow_html=True
)

# -------------------------------------------------
# SECTION: JOB CARD + BUTTON
# -------------------------------------------------
st.subheader("Job Card")

with st.container():
    st.markdown(
        """
        <div class="job-card">
            <div>
                <div class="job-title">Backend Engineer</div>
                <div class="job-meta">
                    PT Lintas Teknologi Indonesia &nbsp;|&nbsp;
                    Full-time &nbsp;|&nbsp;
                    Hybrid &nbsp;|&nbsp;
                    Rp 12–18 jt &nbsp;|&nbsp;
                    Jakarta Selatan
                </div>
            </div>
            <details class="job-details">
                <summary>Read more</summary>
                <div class="job-details-content">
                    You will be responsible for designing and maintaining backend
                    services, optimizing database queries, and collaborating with
                    frontend engineers to deliver scalable production systems.
                </div>
            </details>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.write("")  # spacing
    st.button("Save Job")


# -------------------------------------------------
# SECTION: ALERT
# -------------------------------------------------
st.subheader("Alert / Warning")
st.warning("You need to analyze your CV and select a preferred job first.")

# -------------------------------------------------
# SECTION: CHAT
# -------------------------------------------------
st.subheader("Chat Elements")

with st.container():
    st.markdown(
        """
        <div class="surface">
            <div class="chat-user">
                What skills should I focus on for this role?
            </div>
            <div class="chat-ai">
                You should prioritize backend system design, database indexing,
                and production-ready API architecture.
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

# -------------------------------------------------
# CHAT INPUT (BOTTOM)
# -------------------------------------------------
prompt = st.chat_input("Ask about skills, preparation, or next steps…")
if prompt:
    st.write(prompt)
