import streamlit as st
import pandas as np
import numpy as np

st.title("Hello! What would you like to do?")

if st.button("Home"):
    st.switch_page("your_app.py")
if st.button("Chat"):
    st.switch_page("pages/01_ChattingPage.py")
if st.button("Search Jobs"):
    st.switch_page("pages/02_JobSearch.py")
if st.button("Analyze CV"):
    st.switch_page("pages/03_CVAnalyzer.py")
if st.button("AI Consultant"):
    st.switch_page("pages/04_AIConsultant.py")
if st.button("Mock Interview"):
    st.switch_page("pages/05_MockInterview.py")