import pymupdf
import os
import json
import time
from hashlib import md5
from typing_extensions import TypedDict
from langgraph.graph import StateGraph
from langchain_core.messages import SystemMessage
from langchain_core.documents import Document
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_qdrant import QdrantVectorStore
from qdrant_client import QdrantClient
from qdrant_client.http import models as qm
from dotenv import load_dotenv

# TypedDict definition of State
class State(TypedDict):
    summary: str
    user_name: str
    cv_contents: str
    best_jobs: list[dict]
    file_bytes: bytes
    session_id: int
    assessment: str


load_dotenv()
qdrant_url = os.getenv("QDRANT_ENDPOINT")
qdrant_key = os.getenv("QDRANT_API_KEY")

model = ChatOpenAI(model="gpt-4o-mini", temperature=0.3, api_key=os.getenv("OPENAI_API_KEY"))
client = QdrantClient(url=qdrant_url, api_key=qdrant_key)
embedding_model = OpenAIEmbeddings(model="text-embedding-3-small")

embeddings = embedding_model

# Create collection if it doesn't exist
if not client.collection_exists("uploaded_cvs"):
    print("Creating 'uploaded_cvs' collection...")

    client.create_collection(
        collection_name="uploaded_cvs",
        vectors_config=qm.VectorParams(size=1536, distance=qm.Distance.COSINE)
    )

CV_VectorStore = QdrantVectorStore(
    client=client,
    collection_name="uploaded_cvs",
    embedding=embeddings,
)

Jobs_VectorStore = QdrantVectorStore(
    client=client,
    collection_name="Jobs_Documents",
    embedding=embeddings,
)

# ================================= Functions =================================
def convert_bytes(file: bytes) -> str:
    doc = pymupdf.open(stream=file, filetype="pdf")
    text = ""
    for page in doc:
        text = text + page.get_text()
    return text


def analysis_compile(intial_state: State):
    # compiles main graph, passes State, and starts the program
    document_agent = StateGraph(State)

    # Define graph
    document_agent.add_node("read_doc", read_doc)
    document_agent.add_node("construct_vector", construct_vector)
    document_agent.add_node("find_jobs", find_jobs)
    document_agent.add_node("assess_user", assess_user)

    document_agent.set_entry_point("read_doc")

    document_agent.add_edge("read_doc", "construct_vector")
    document_agent.add_edge("construct_vector", "find_jobs")
    document_agent.add_edge("find_jobs", "assess_user")

    document_agent.set_finish_point("assess_user")

    app = document_agent.compile()
    response = app.invoke(intial_state)

    return response


def read_doc(State: State):
    byte_file = State["file_bytes"]
    cv_contents = convert_bytes(byte_file)

    system_prompt = SystemMessage(
        f"""You are a CV analyzer. Your role is to extract the user's fullname and provide a summary analysis of the CV that adequately encapsulates 
        the prospect's persona.

        You must output a strictly valid JSON object with exactly two keys:
        1. "name": The full name of the candidate found in the CV. If not found, use "Candidate".
        2. "summary": The summary analysis string following the format below:

        Username: 
        Preferred Companies: (if available)
        Preferred Location: (based on their stated location or past location history)
        Preferred Salary Range:
        Preferred Work Type:
        Strenghts:
        Skills:
        General assessment:
        Work Experience:
        
        This summary will be used for semantic searching against a vector database that stores job information across Indonesia. 
        Output only the summary analysis as a single string. Example:
        
        "Preferred Companies: Microsoft | Preferred Location: Jakarta Selatan| and so on..."

        The following is the CV:
        {cv_contents}
        """ 
        )
    
    response = model.invoke([system_prompt]).content

    try:
        clean_json = response.replace("```json", "").replace("```", "")
        data = json.loads(clean_json)
        user_name = data.get("name", "Candidate")
        summary = data.get("summary", "")
    except:
        user_name = "Candidate"
        summary = response

    return {"summary": response, "user_name": user_name, "cv_contents": cv_contents}


def construct_vector(State: State):
    # Store CV summary + CV contents as metadata. Embed CV summary for vector points
    _metadata = {
        "cv_contents": State["cv_contents"],
        "created": int(time.time())
    }

    unique_identifier = State["summary"].lower().encode('utf-8')
    unique_id = md5(unique_identifier).hexdigest()

    doc = Document(
        page_content=State["summary"],
        metadata=_metadata,
        id=unique_id
    )

    qdrant = CV_VectorStore.add_documents([doc])

    # print(qdrant)

    return {}


def find_jobs(State: State):

    qdrant = Jobs_VectorStore.similarity_search_with_score(
        query=State["summary"],
        k=10,
    )

    list_of_jobs = []

    for points in qdrant:
        Document = points[0]
        metadata = Document.metadata
        page_content = Document.page_content

        if "Job Description:" in page_content:
            job_desc = page_content.split("Job Description: ", 1)[1].strip()
        else:
            job_desc = page_content

        Job = {
            'work_type': metadata["work_type"],
            'location': metadata["location"],
            'salary': metadata["salary"],
            'company_name': metadata["company_name"],
            'job_title': metadata["job_title"],
            'job_description': job_desc
        }

        list_of_jobs.append(Job)

    return {"best_jobs": list_of_jobs}


def assess_user(State: State):
    recommended_jobs = ""
    for job in State["best_jobs"]:
        company = job["company_name"]
        job_title = job["job_title"]

        recommended_jobs += f"{job_title} at {company}\n"


    system_prompt = SystemMessage(
        f"""
        You are MBTI assessment program. You will be given a user's CV summary and their recommended jobs, and from that I want you to write an
        assessment on their MBTI persona as well as a paragraph analysis of their work tendencies among other assessments.

        The output should be in the form of a single string/paragraph with the first 6 characters relating to their MBTI-A/T, and the rest being the assessment.
        Example: "ENTP-T You are an outgoing extrovert who..."
        Do not include quotation marks.

        Here is the provided data:
        Jobs:
        {recommended_jobs}

        CV_Summary:
        {State['summary']}
        """
    )

    response = model.invoke([system_prompt]).content.strip('"')
    return {"assessment": response}



# metadata={
# 'work_type': 'Full time', 
# 'location': 'Jakarta Raya', 
# 'salary': 'Tidak Ditampilkan', 
# 'company_name': 'PT. PUSAT BANDAR BERDIKARI', 
# 'job_title': 'STAFF PERSONALIA', 
# '_id': 'ff91ecd2-765e-b325-6b25-d463e6f1f9a5', 
# '_collection_name': 'Jobs_Documents'}

