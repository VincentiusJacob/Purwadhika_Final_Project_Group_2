import streamlit as st
from data.global_state import state as global_state, save_state
import requests
import math
import os
import json

API_URL = "http://localhost:8000/get-all-jobs"
ITEMS_PER_PAGE = 10
DB_FILE = "user_data.json"

st.set_page_config(page_title="Job Search", layout="wide")

if 'page_number' not in st.session_state:
    st.session_state.page_number = 1

st.title("Got a Specific Job in Mind?")

st.markdown("Here are the current available jobs in Indonesia")

st.markdown(f"**Filters**")

if "prefered_jobs" not in st.session_state:
    st.session_state["prefered_jobs"] = {}


# User may filter by Job Title, Company, Min and Max Salary , Location, Work Type, Work Style
col1, col2, col3, col4 = st.columns([1,1,1,1])

with col1:
    with st.container(border=True):
        st.markdown("Job Title")
        job_title_filter = st.text_input(
            "Enter job title...",
        )
    
    with st.container(border=True):
        st.markdown("Work Type")
        work_type_fiter = st.selectbox(
            "Choose your working type",
            ("All", "Full Time", "Paruh waktu", "Kontrak/Temporer", "Kasual")
        )

with col2:
    with st.container(border=True):
        st.markdown("Company Name")
        company_filter = st.text_input(
            "Enter company name..."
        )

    with st.container(border=True):
        st.markdown("Work Style")
        work_style_filter = st.selectbox(
            "Choose your working style",
            ("All", "On-Site", "Remote", "Hybrid")
        )

with col3:
    with st.container(border=True):
        st.markdown("Salary Range")
        salary_range = st.slider("Select your minimum and maximum salary", 0, 100_000_000, (1_000_000, 100_000_000), step=500_000, format="Rp %d")

with col4:
    with st.container(border=True):
        st.markdown("Location")
        location_filter = st.text_input("Enter location...")


try:
    response = requests.get(API_URL)

    if response.status_code == 200:
        jobs = response.json()

        filtered_jobs = []

        filter_min_salary, filter_max_salary = salary_range

        for job in jobs:
            if job_title_filter and job_title_filter.lower() not in job.get('job_title', '').lower():
                continue

            if company_filter and company_filter.lower() not in job.get('company_name', '').lower():
                continue

            if location_filter and location_filter.lower() not in job.get('location', '').lower():
                continue

            if work_type_fiter != "All":
                if work_type_fiter and work_type_fiter.lower() not in job.get('work_type', '').lower():
                    continue
            
            if work_style_filter != "All":
                if work_style_filter and work_style_filter.lower() not in job.get('work_style', '').lower():
                    continue

            job_min = job.get('min_salary', 0)
            job_max = job.get('max_salary', 0)

            if job_min == 0 and job_max == 0:
                if filter_min_salary > 0:
                    continue 
            else:
             
                if job_min < filter_min_salary or job_max > filter_max_salary:
                    continue
            
            filtered_jobs.append(job)

        total_jobs = len(filtered_jobs)
        total_pages = math.ceil(total_jobs / ITEMS_PER_PAGE)

        if st.session_state.page_number > total_pages:
            st.session_state.page_number = 1
        
        start_index = (st.session_state.page_number - 1) * ITEMS_PER_PAGE
        end_index = start_index + ITEMS_PER_PAGE

        current_page_jobs = filtered_jobs[start_index:end_index]

        st.caption(f"Showing {start_index + 1}-{min(end_index, total_jobs)} of {total_jobs} jobs")

        if not current_page_jobs:
            st.warning("No jobs found matching your criteria.")
        else:
            for i, job in enumerate(current_page_jobs):
                with st.container(border=True):
                    col1, col2 = st.columns([3, 1])

                    with col1:
                        st.subheader(job.get('job_title', 'Untitled'))
                        st.write(f"**{job.get('company_name', '-')}**")
                        st.write(f"📍 {job.get('location', '-')} | {job.get('work_type', '-')} | {job.get('work_style', '-')}")
                    
                    with col2:
                        min_sal = job.get('min_salary', 0)
                        max_sal = job.get('max_salary', 0)

                        if min_sal == 0 and max_sal == 0:
                            st.markdown("**Salary not mentioned**")
                        else:
                            st.markdown(f"**Rp {min_sal:,} - Rp {max_sal:,}**")

                        if st.button("Prepare for this job", key=f"job_{i}"):
                            global_state['prefered_jobs'] = {
                                "job_title": job['job_title'],
                                "company_name": job['company_name'],
                                "job_description": job['job_description']
                            }
                            
                            st.session_state['prefered_jobs'] = global_state['prefered_jobs']
                            save_state()

                            st.session_state['last_consulted_job_title'] = ""

                            st.success("Data is updated, You are ready for consulting and practice interview.")

                    with st.expander("See Job Description"):
                        desc = job.get("job_description", "No description provided.")
                        st.markdown(desc.replace("\\n", "\n"))

        st.divider()
        col_prev, col_page_display, col_next = st.columns([1, 2, 1])

        with col_prev:
            if st.session_state.page_number > 1:
                if st.button("⬅️ Previous"):
                    st.session_state.page_number -= 1
                    st.rerun() 

        with col_page_display:
            st.markdown(f"<div style='text-align: center'>Page <b>{st.session_state.page_number}</b> of <b>{total_pages}</b></div>", unsafe_allow_html=True)

        with col_next:
            if st.session_state.page_number < total_pages:
                if st.button("Next ➡️"):
                    st.session_state.page_number += 1
                    st.rerun() 
    else:
        st.error(f"Failed to fetch jobs. Status code: {response.status_code}")

except Exception as e:
    st.error(e)





