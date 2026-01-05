# pages/04_AIConsultant.py
import streamlit as st
import requests


st.set_page_config(page_title="AI Career Consultant", layout="centered")

st.title("👨‍💼 AI Job Consultant")

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

    /* App background */
    html, body, .stApp {
        background-color: var(--bg-main);
        color: var(--text-main);
    }

    /* Centered layout polish */
    .block-container {
        max-width: 900px;
        padding-top: 2.5rem;
        padding-bottom: 3rem;
    }

    /* Sidebar */
    section[data-testid="stSidebar"] {
        background-color: var(--bg-surface);
        border-right: 1px solid var(--border-soft);
    }

    section[data-testid="stSidebar"] button {
        background: transparent;
        color: var(--text-muted);
        border-radius: 10px;
    }

    section[data-testid="stSidebar"] button:hover,
    section[data-testid="stSidebar"] button[aria-selected="true"] {
        background-color: var(--accent-soft);
        color: var(--text-main);
        font-weight: 600;
    }

    /* Chat bubbles */
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

    /* Chat input */
    div[data-testid="stChatInput"] textarea {
        background-color: var(--bg-card);
        color: var(--text-main);
        border-radius: var(--radius-lg);
        border: 1px solid var(--border-soft);
        padding: 12px;
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

    /* Alerts */
    div[data-testid="stAlert"] {
        background-color: var(--bg-card);
        border: 1px solid var(--border-soft);
        border-radius: var(--radius-md);
        color: var(--text-muted);
    }
    </style>
    """,
    unsafe_allow_html=True
)


preference_job = st.session_state.get('prefered_jobs', {})
user_summary = st.session_state.get('user_summary', 'User has not provided a summary.')

current_job_title = preference_job.get('job_title', 'None')
last_job_title = st.session_state.get('last_consulted_job', None)

# if user select different prefered job, the system will delete previous chat history
if current_job_title != last_job_title:
    if 'consultant_messages' in st.session_state:
        del st.session_state['consultant_messages']
    
    st.session_state['last_consulted_job'] = current_job_title

if "consultant_messages" not in st.session_state:
    st.session_state.consultant_messages = []

    if current_job_title != "None":
        initial_context = f"""
        CONTEXT:
        The user is looking for a job. Here is their profile summary:
        {user_summary}

        The User Prefered job is:
        Role: {preference_job.get('job_title', 'Not specified')}
        Company: {preference_job.get('company_name', 'Not specified')}

        The Job Description is:
        {preference_job.get('job_description', 'No description provided.')}
        
        YOUR TASK:
        You are a Career Consultant. Do NOT provide job listings. 
        Instead, help them prepare to get their prefered job. Tell them what skills they lack, 
        what they should learn ("harus belajar apa"), and next steps by comparing their summary and the job description.
        """
        
        st.session_state.consultant_messages.append({"role": "system", "content": initial_context})
        st.session_state.consultant_messages.append({"role": "assistant", "content": f"I see you want to apply for the **{preference_job.get('job_title')}** position at **{preference_job.get('company_name')}**. I have analyzed the job description. What would you like to know?"})


for msg in st.session_state.consultant_messages:
    if msg["role"] != "system":
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

is_disabled = current_job_title == "None"
placeholder_text = "Select your prefered job first!" if is_disabled else "What skills should I learn?"

if is_disabled:
    st.warning("⚠️ You need to analyze your CV first AND select your prefered job to start consulting.")

if prompt := st.chat_input(placeholder_text, disabled=is_disabled):
    st.session_state.consultant_messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        # We reuse your existing API endpoint but the context is handled in history
        # Note: You might need to update your api/app.py to handle history or just send the prompt
        # For simplicity here, we assume a basic completion or you can reuse your supervisor agent
        
        # Construct a query that includes context for the stateless API
        full_query = f"User Profile: {user_summary}. User Question: {prompt}"
        
        API_URL = "http://localhost:8000/job-information" 
        response = requests.post(API_URL, json={"query": full_query})
        
        if response.status_code == 200:
            ans = response.json().get("response", "Error")
            st.markdown(ans)
            st.session_state.consultant_messages.append({"role": "assistant", "content": ans})