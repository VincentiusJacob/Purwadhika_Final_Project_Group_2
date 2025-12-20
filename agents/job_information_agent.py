from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent
from .agent_tools import retrieve_information_from_database

def get_job_info_agent():
    llm = ChatOpenAI(model="gpt-4o-mini")
    
    tools = [retrieve_information_from_database]

    system_prompt = """
    You are a specialist job seeker assistant.

    YOU PROVIDE INFROMATIONS ABOUT JOB TO THE USER
    
    RULES:
    1. You MUST use the 'retrieve_information_from_database' tool to find real data. 
    2. DO NOT answer from your own knowledge. 
    3. If the user asks for a job, IMMEDIATELY call the tool.
    4. After getting data from the tool, summarize it in Bahasa Indonesia.
    """

    agent = create_react_agent(
        model=llm,
        tools=tools,
        prompt=system_prompt,
        name="job_information_agent"
    )

    return agent