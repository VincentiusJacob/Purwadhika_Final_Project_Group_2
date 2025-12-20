from langchain_core.tools import tool
from langchain_qdrant import QdrantVectorStore
from qdrant_client import QdrantClient
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
import os
from dotenv import load_dotenv

load_dotenv()

# KEYS
api_key = os.getenv("OPENAI_API_KEY")
qdrant_url = os.getenv("QDRANT_ENDPOINT") 
qdrant_api_key = os.getenv("QDRANT_API_KEY")  
collection_name = "Jobs_Documents" 

# Initialize Clients

llm = ChatOpenAI(model="gpt-4o-mini")
embedding = OpenAIEmbeddings(model="text-embedding-3-small")
qdrant_client = QdrantClient(url=qdrant_url, api_key=qdrant_api_key)
vector_store = QdrantVectorStore(client=qdrant_client, collection_name=collection_name, embedding=embedding)

# Tools for Job_Information_Agent

@tool 
def retrieve_information_from_database(query:str):
    """
    Use this tool to search for specific job information in the Database.
    Input should be a specific query string about jobs.
    """

    documents = vector_store.similarity_search(query, k=3)
    return "\n\n".join(doc.page_content for doc in documents)




