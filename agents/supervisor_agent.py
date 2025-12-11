from typing import TypedDict, Annotated, List, Dict
from langgraph.graph import StateGraph, END
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage, BaseMessage, AIMessage
import operator
from agents.interview_agent import generate_interview_response


class AgentState(TypedDict):
    messages: Annotated[List[BaseMessage], operator.add]
    next_step: str
    job_context: Dict 
    interview_count: int 


def interview_node(state: AgentState):
    """
    Node ini menangani logika interview dalam konteks Graph.
    (Biasanya dipakai jika interview-nya text-based via chat biasa).
    """
    history = state['messages']
    job_ctx = state.get('job_context', {})
    count = state.get('interview_count', 0)
    
    response_text = generate_interview_response(history, job_ctx, count)
    
    return {
        "messages": [AIMessage(content=response_text)],
        "interview_count": count + 1,
        "next_step": "end_turn" # Kembali ke user
    }


def supervisor_node(state: AgentState):
    """
    Otak utama yang menentukan mau panggil agent mana.
    """
    llm = ChatOpenAI(model="gpt-4o-mini")
    
    messages = state['messages']
    last_user_msg = messages[-1].content.lower()
    

    if "interview" in last_user_msg or "latihan" in last_user_msg:
        return {"next_step": "interview_agent"}
    elif "cari kerja" in last_user_msg:
        return {"next_step": "job_search_agent"} 
    else:
        return {"next_step": "general_chat"}

# 4. Build Graph
def build_supervisor_graph():
    workflow = StateGraph(AgentState)
    
    # Daftarkan Node
    workflow.add_node("supervisor", supervisor_node)
    workflow.add_node("interview_agent", interview_node)
    # workflow.add_node("job_search_agent", job_search_node) # Nanti ditambah
    
    # Set Entry Point
    workflow.set_entry_point("supervisor")
    
    # Buat Edge (Jalur Logika)
    workflow.add_conditional_edges(
        "supervisor",
        lambda x: x['next_step'], # Baca value 'next_step' dari output supervisor
        {
            "interview_agent": "interview_agent",
            "job_search_agent": END, # Sementara END dulu
            "general_chat": END
        }
    )
    
    workflow.add_edge("interview_agent", END) # Setelah interview jawab, balik ke user
    
    return workflow.compile()