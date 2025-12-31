from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent
from .agent_tools import retrieve_information_from_database
from data.global_state import state, load_state

def get_job_info_agent():

    load_state()
    user_summary = state.get("user_summary", "No user data")
    
    llm = ChatOpenAI(model="gpt-4o-mini")
    
    tools = [retrieve_information_from_database]


    system_prompt = f"""
    You are a specialist job seeker assistant.
    
    CURRENT USER PROFILE:
    {user_summary}
    
    RULES:
    1. When searching for jobs, prioritize the user's location and salary expectations found in the profile above.
    2. You MUST use the 'retrieve_information_from_database' tool to find real data. 
    3. Summarize results in Bahasa Indonesia.
    """

    agent = create_react_agent(
        model=llm,
        tools=tools,
        prompt=system_prompt,
        name="job_information_agent"
    )

    return agent