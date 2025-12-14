import streamlit as st
import requests

API_URL = "http://localhost:8000/job-information"

st.set_page_config(page_title="Job Search Chatbot", layout="centered")

st.title("Job Search Assistant")
st.write("Tanya apapun tentang pekerjaan di Indonesia")

if "messages" not in st.session_state:
    st.session_state.messages = []
        

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])


if prompt := st.chat_input("Ask about a job..."):

    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        status_container = st.status("Agent is thinking...", expanded=True)
        
        try:
            response = requests.post(API_URL, json={"query": prompt})
            
            if response.status_code == 200:
                data = response.json()
                ans = data.get("response", "No response")
                steps = data.get("steps", [])
       
                for step in steps:
                    status_container.write(step)
                
                status_container.update(label="Process Complete", state="complete", expanded=False)
                
                st.markdown(ans)
                st.session_state.messages.append({"role": "assistant", "content": ans})
                
            else:
                status_container.update(label="Error", state="error")
                st.error(f"Error: {response.text}")
                
        except Exception as e:
            status_container.update(label="Connection Failed", state="error")
            st.error(f"Connection failed: {e}")