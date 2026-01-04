import os
import base64
import json
import sqlite3
from typing_extensions import TypedDict, Literal
from pydantic import BaseModel
from typing import Annotated, Any
from langgraph.graph import StateGraph, END
from langchain_core.messages import SystemMessage, AIMessage
from langgraph.graph.message import add_messages
from langchain_core.documents import Document
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_qdrant import QdrantVectorStore
from qdrant_client import QdrantClient, models
from qdrant_client.http import models as qm
from dotenv import load_dotenv

# TypedDict definition of State
class State(TypedDict):
    query: str
    summary: str
    best_jobs: list[dict]
    session_id: str
    messages: Annotated[list[Any], add_messages]


load_dotenv()
qdrant_url = os.getenv("QDRANT_ENDPOINT")
qdrant_key = os.getenv("QDRANT_API_KEY")

model = ChatOpenAI(model="gpt-4o-mini", temperature=0.3, api_key=os.getenv("OPENAI_API_KEY"))
client = QdrantClient(url=qdrant_url, api_key=qdrant_key)
embedding_model = OpenAIEmbeddings(model="text-embedding-3-small")

embeddings = embedding_model

vector_store = QdrantVectorStore.from_existing_collection(
    collection_name="Jobs_Documents",
    url=qdrant_url,
    api_key=qdrant_key,
    embedding=embedding_model,
)


# Temporary code to setup payload indexing

# from qdrant_client.models import PayloadSchemaType

# client.create_payload_index(
#     collection_name="Jobs_Documents",
#     field_name="metadata.work_type",
#     field_schema=PayloadSchemaType.TEXT
# )

# client.create_payload_index(
#     collection_name="Jobs_Documents",
#     field_name="metadata.work_style",
#     field_schema=PayloadSchemaType.TEXT
# )

# client.create_payload_index(
#     collection_name="Jobs_Documents",
#     field_name="metadata.location",
#     field_schema=PayloadSchemaType.TEXT
# )

# ============================================ Helper Functions ============================================

import re

def parse_min_salary(salary_str: str) -> int | None:
    if not salary_str:
        return None

    # Case 1: undisclosed
    if "Tidak Ditampilkan" in salary_str:
        return None

    # Normalize dash variants (–, —, -)
    # Split on dash and keep the first part
    first_part = re.split(r"[–—-]", salary_str)[0]

    # Remove everything except digits
    digits = re.sub(r"\D", "", first_part)

    if not digits:
        return None

    return int(digits)


# ============================================ Query Functions ============================================

def RAG_query(raw_parameters: dict, _query: str):
    RAG_parameters = {key: value for key, value in raw_parameters.items() if value is not None}
    # {"work_style": "Hybrid", "work_type": "Full time", ...}

    _must = [
        models.FieldCondition(
            key=f"metadata.{key}",
            match=models.MatchText(text=value)
        )
        for key, value in RAG_parameters.items()
    ]

    metadata_filter = models.Filter(
        must=_must
    )

    points = vector_store.similarity_search(
        query=_query,
        k=5,
        filter=metadata_filter
    )

    list_of_jobs = []
    for point in points:
        metadata = point.metadata
        page_content = point.page_content

        if "Job Description:" in page_content:
            job_desc = page_content.split("Job Description: ", 1)[1].strip()
        else:
            job_desc = page_content

        Job = {
            'job_title': metadata["job_title"],
            'company_name': metadata["company_name"],
            'work_type': metadata["work_type"],
            'work_style': metadata["work_style"],
            'location': metadata["location"],
            'salary': metadata["salary"],
            'job_description': job_desc,
        }

        list_of_jobs.append(Job)

    return list_of_jobs


# SELECT
#     *
# FROM jobs
# WHERE job_title LIKE '%' || :job_title || '%'
#   AND company_name LIKE '%' || :company_name || '%'
#   AND clean_location LIKE '%' || :location || '%'
#   AND LOWER(TRIM(work_style)) LIKE LOWER(TRIM(:work_style))
#   AND LOWER(TRIM(work_type)) LIKE LOWER(TRIM(:work_type))
#   AND :salary BETWEEN min_salary AND max_salary
# ORDER BY max_salary DESC
# LIMIT 5;


def SQL_query(raw_parameters: dict):
    conn = sqlite3.connect("data/jobs_database.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    filter = {
        key: value for key, value in raw_parameters.items() if value is not None
    }

    my_list  = [
        f"{key} LIKE '%' || :{key} || '%'" for key, value in filter.items() if key != "salary"
    ]

    x = "\nAND ".join(my_list)

    try:
        if filter.get("salary"):
            if not x:
                x = "max_salary >= :salary"
            else:    
                x = x + "\nAND max_salary >= :salary"
    except Exception:
        pass

    query = f"""SELECT
    *
    FROM jobs
    WHERE {x}
    ORDER BY max_salary DESC
    LIMIT 5;
    """

    # print(query)

    results = cursor.execute(query, filter).fetchall()
    # print(results)

    jobs = []

    for row in results:
        job = {
            'job_title': row["job_title"],
            'company_name': row["company_name"],
            'work_type': row["work_type"],
            'work_style': row["work_style"],
            'location': row["location"],
            'salary': f"""{row["min_salary"]} - {row["max_salary"]}""",
            'job_description': row["job_description"],
        }

        jobs.append(job)

    return jobs

    

# Job = {
#             'job_title': metadata["job_title"],
#             'company_name': metadata["company_name"],
#             'work_type': metadata["work_type"],
#             'work_style': metadata["work_style"],
#             'location': metadata["location"],
#             'salary': metadata["salary"],
#             'job_desc': job_desc,
#         }




# ============================================ Langchain/Langgraph ============================================

def search_compile(initial_state: State):
    search_agent = StateGraph(State)

    search_agent.add_node("entry_point", entry_point)
    search_agent.add_node("python_filter", python_filter)
    search_agent.add_node("RAG_search", rag_search)
    search_agent.add_node("SQL_search", sql_search)
    search_agent.add_node("final_check", final_check)

    search_agent.set_entry_point("entry_point")

    search_agent.add_conditional_edges(
        "entry_point",
        choose_edge,
        {
            "python_filter": "python_filter",
            "RAG_search": "RAG_search",
            "SQL_search": "SQL_search",
            "Null intent": "final_check"
        }
        
    )

    search_agent.add_edge("python_filter", "final_check")
    search_agent.add_edge("RAG_search", "final_check")
    search_agent.add_edge("SQL_search", "final_check")

    search_agent.set_finish_point("final_check")

    app = search_agent.compile()
    response = app.invoke(initial_state)

    return response


class EntryFormat(BaseModel):
    entry_point: Literal["python_filter", "RAG_search", "SQL_search", "Null intent"]

def entry_point(state: State):
    user_query = state["query"]
    json_model = model.with_structured_output(EntryFormat)
    
    system_prompt = SystemMessage(
        f"""
        Select the appropriate route for the user query.

        [Build upon your current list] -> python_filter

        [Find new jobs based on CV] -> RAG_search

        [Find specific jobs you want] -> SQL_search

        Example queries (they don't have to match, just the overall intent)

        python_filter: 
        - "build upon the given list by filtering based chosen parameters."
        - "I like these jobs, but I only want the ones with a provided salary."
        - "I only want the jobs that are provided in Jakarta."
        - "I only want Hybrid-type jobs."

        RAG_search: 
        - "Find 10 new jobs with RAG using the user's CV summary that are in Tangerang."
        - "Find new jobs that match my CV but are only in Jakarta."
        - "None of these jobs fit me. Find new jobs."  

        SQL_search: 
        - "Search for 10 new data analysis jobs in Bandung."
        - "Find me new jobs fit for a computer science student thats in Jakarta and has a listed salary."

        tip: Unless the user asks for "new jobs", its most likely python_filter.
        tip: SQL_search usually involves directly finding jobs jobs based on titles.

        If the query has no matching intent, respond with None.

        User query:
        {user_query}
        """
    )

    response = json_model.invoke([system_prompt]).entry_point

    print("---------------------")
    print(response)
    print("---------------------")
    return {"messages": [system_prompt, AIMessage(response)]}


def choose_edge(state: State):
    choice = state["messages"][-1].content

    if "python_filter" in choice:
        return "python_filter"
    elif "RAG_search" in choice:
        return "RAG_search"
    elif "SQL_search" in choice:
        return "SQL_search"
    else:
        return "Null intent"


class FilterFormat(BaseModel):
    work_style: Literal["On-site", "Hybrid", "Remote"] | None = None
    work_type: Literal[
        "Full time", "Paruh waktu", "Kasual", "Kontrak/Temporer"
    ] | None = None
    min_salary: int | None = None
    location: str | None = None

def python_filter(state: State):
    print("python_filter was chosen ----------------------\n")
    json_model = model.with_structured_output(FilterFormat)
    system_prompt = SystemMessage(
        f"""
        Extract filters from the user query into the given schema.

        Rules:
        - Only populate a field if explicitly stated; otherwise use None.
        - Do not infer missing values.
        - Normalize locations to the least specific valid form (e.g. Jakarta Selatan → Jakarta),
        unless the query explicitly requires specificity.
        - Use exact enum values for work_style and work_type.

        Query:
        {state['query']}
        """
    )

    py_filter = json_model.invoke([system_prompt])

    print("py_filter ----------------------")
    print(py_filter) #check
    print("")
    

    jobs = state["best_jobs"]
    passed_jobs = []

    for job in jobs:
        title = job["job_title"]
        print(f"Processing Job: {title} ---------------")

        # fields
        work_style = job["work_style"].lower()
        work_type  = job["work_type"].lower()
        location   = job["location"].lower()

        print(f"style = {work_style}, type = {work_type}, location {location}")

        if py_filter.work_style is not None and work_style != py_filter.work_style.lower():
            print("Failed on work_style check...\n")
            continue

        if py_filter.work_type is not None and work_type != py_filter.work_type.lower():
            print("Failed on work_type check...\n")
            continue

        if py_filter.location is not None and py_filter.location.lower() not in location:
            print("Failed on location check...\n")
            continue

        job_min_salary = parse_min_salary(job["salary"])
        print(f"min_salary = {job_min_salary}")
        min_salary_filter = py_filter.min_salary

        # User did not specify a salary
        if min_salary_filter is None:
            print("Job passed! Appending to list")
            passed_jobs.append(job)
            print("\n")
            continue

        # Skip undisclosed salaries
        if job_min_salary is None:
            print("Failed on salary check... (Salary not provided)\n")
            continue

        if min_salary_filter is not None and job_min_salary < min_salary_filter:
            print("Failed on salary check... (Salary below minimum requirement)\n")
            continue

        print("Job passed! Appending to list")
        passed_jobs.append(job)
        print("\n")

    # print(passed_jobs)
    return {"messages": [system_prompt, AIMessage(content=json.dumps(py_filter.model_dump()))],"best_jobs": passed_jobs}


class RAGFormat(BaseModel):
    work_style: Literal["On-site", "Hybrid", "Remote"] | None = None
    work_type: Literal[
        "Full time", "Paruh waktu", "Kasual", "Kontrak/Temporer"
    ] | None = None
    location: str | None = None

def rag_search(state: State):
    print("RAG_search was chosen ----------------------\n")
    json_model = model.with_structured_output(RAGFormat)
    system_prompt = SystemMessage(
        f"""
        According to this user query, output an appropriate Json object that contains the query's specifications as a filter.

        Rules:
        - Only populate a field if explicitly stated; otherwise use None.
        - Do not infer missing values.
        - Locations are caps-sensitive. Correct = 'Jakarta Selatan' | Incorrect = 'jakarta selatan'
        - Use exact enum values for work_style and work_type.
        - Generalize locations. Prefer 'Jakarta' over 'Jakart Selatan' unless specified.

        Query:
        {state['query']}
        """
    )

    RAG_parameters = json_model.invoke([system_prompt]).model_dump()
    print(f"RAG_Parameters: {RAG_parameters}")
    response = RAG_query(RAG_parameters, state["query"])

    return {"messages": [system_prompt, AIMessage(content=json.dumps(RAG_parameters, ensure_ascii=False, indent=2))], "best_jobs": response}


class SQLFormat(BaseModel):
    job_title: str | None = None
    company_name: str | None = None
    work_style: Literal["On-site", "Hybrid", "Remote"] | None = None
    work_type: Literal[
        "Full time", "Paruh waktu", "Kasual", "Kontrak/Temporer"
    ] | None = None
    location: str | None = None
    salary: int | None = None

def sql_search(state: State):
    print("SQL_search was chosen ----------------------\n")
    json_model = model.with_structured_output(SQLFormat)

    system_prompt = SystemMessage(
        f"""
        According to this user query, output an appropriate Json object that contains the query's specifications as a filter made for
        SQL querying.

        Rules:
        - Only populate a field if explicitly stated; otherwise use None.
        - Locations are caps-sensitive. Correct = 'Jakarta Selatan' | Incorrect = 'jakarta selatan'
        - Use exact enum values for work_style and work_type.
        - Generalize locations. Prefer 'Jakarta' over 'Jakart Selatan' unless specified.
        - Use the common denominator for Job titles. Consider it as a "keyword detector". So if user wants a data analysis job, simply
        "data" will suffice as: "Data Analyst", "Data Analysis Specialist", and "Data Engineer" could all be valid jobs.

        Query:
        {state['query']}
        """
    )

    SQL_parameters = json_model.invoke([system_prompt]).model_dump()
    print(SQL_parameters)
    response = SQL_query(SQL_parameters)

    # job_title, work_style, work_type, location, 
    return {"messages": [system_prompt, AIMessage(content=json.dumps(SQL_parameters, ensure_ascii=False, indent=2))], "best_jobs": response}


def final_check(state: State):
    if not state["best_jobs"] or state["messages"][-1].content == "Null intent":
        # best jobs is an empty [] 

        system_prompt = SystemMessage(
            """
            No jobs were returned, meaning the user's query was too specific/resulted in no matches.
            Judging from past messages, provide a 1-2 sentence comment on what possibly went wrong and what the user should change.
            Example: "It seems no jobs with those specifications are available in Bandung. Maybe lower your minimum salary criteria!"
            Example: "Thats not a valid query, please provide a valid query with appropriate intent."

            or it was a null
            """
        )

        response = model.invoke(state["messages"] + [system_prompt])

        return {"messages": response}
    
    return {}

# python filtering functions
if __name__ == "__main__":
    # Fake Jobs
    best_jobs = [
    {
        "Title": "Backend Engineer",
        "work_type": "Full time",
        "work_style": "Hybrid",
        "salary": "Rp 12.000.000 – Rp 18.000.000 per month",
        "location": "Jakarta Selatan"
    },
    {
        "Title": "Frontend Developer",
        "work_type": "Full time",
        "work_style": "Remote",
        "salary": "Rp 9.500.000",
        "location": "Jakarta"
    },
    {
        "Title": "Data Analyst",
        "work_type": "Paruh waktu",
        "work_style": "On-site",
        "salary": "Tidak Ditampilkan",
        "location": "Jakarta Barat"
    },
    {
        "Title": "Machine Learning Engineer",
        "work_type": "Full time",
        "work_style": "Hybrid",
        "salary": "Rp 25.000.000 – Rp 55.000.000",
        "location": "Jakarta Pusat"
    },
    {
        "Title": "UI/UX Designer",
        "work_type": "Kasual",
        "work_style": "Remote",
        "salary": "Rp 7.000.000 – Rp 9.000.000",
        "location": "Bandung"
    },
    {
        "Title": "Mobile App Developer",
        "work_type": "Kontrak/Temporer",
        "work_style": "Hybrid",
        "salary": "Rp 10.000.000",
        "location": "Jakarta Timur"
    },
    {
        "Title": "DevOps Engineer",
        "work_type": "Full time",
        "work_style": "On-site",
        "salary": "Rp 15.000.000 – Rp 22.000.000",
        "location": "Jakarta Barat"
    },
    {
        "Title": "QA Tester",
        "work_type": "Paruh waktu",
        "work_style": "Remote",
        "salary": "Rp 6.500.000",
        "location": "Depok"
    },
    {
        "Title": "Product Manager",
        "work_type": "Full time",
        "work_style": "Hybrid",
        "salary": "Rp 18.000.000 – Rp 30.000.000",
        "location": "Jakarta Selatan"
    },
    {
        "Title": "Data Engineer",
        "work_type": "Full time",
        "work_style": "On-site",
        "salary": "Rp 20.000.000",
        "location": "Tangerang"
    }
    ]

    # Fake summary
    user_summary = "I am a BIG FAN of data analysis and coding. WOohoo."

    user_query = "Find me a computing job with a salary of over 20 million a month"

    initial_state: State = {
        "query": user_query,
        "summary": user_summary,
        "best_jobs": best_jobs,
        "messages": []
    }

    print(f"user query: {user_query}\n")

    response = search_compile(initial_state)

    if response["best_jobs"]:
        for job in response["best_jobs"]:
            print(job)
    else:
        print(response["messages"][-1].content)
