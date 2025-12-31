from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from agents.supervisor_agent import get_supervisor
from langchain_core.messages import HumanMessage, AIMessage, ToolMessage
import traceback
from livekit import api as livekit_api
import os
from dotenv import load_dotenv
import sqlite3

load_dotenv()

app = FastAPI()

current_dir = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(current_dir, '..', 'data', 'jobs_database.db')

conn = sqlite3.connect(db_path, check_same_thread=False)
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

supervisor_agent = get_supervisor()

class ChatRequest(BaseModel):
    query: str
    thread_id: str = "default"

class TokenRequest(BaseModel):
    room_name: str
    participant_name: str


# ================================================= RETRIEVE JOB INFORMATION FROM VECTOR DB / DIRECT ANSWER =========================================
@app.post("/job-information")
async def job_information(request: ChatRequest):
    try :
        initial_state = {
            "messages": [HumanMessage(content=request.query)]
        }

        result = supervisor_agent.invoke(initial_state)

        steps_log = []
        final_message=""

        for msg in result["messages"]:
            if isinstance(msg, AIMessage) and msg.tool_calls:
                for tool in msg.tool_calls:
                    steps_log.append(f"Agent calling tool: **{tool['name']}**")
            elif isinstance(msg, ToolMessage):
                snippet = msg.content[:100] + "..." if len(msg.content) > 100 else msg.content
                steps_log.append(f"Tool returned data: {snippet}")
            elif isinstance(msg, AIMessage) and msg.content:
                final_message = msg.content
        

        return {
            "response": final_message,
            "steps": steps_log
        }

    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

# ======================================================= GET LIVEKIT TOKEN ===================================================
@app.post("/get-livekit-token")
async def get_livekit_token(req: TokenRequest):
    try:
        api_key = os.getenv("LIVEKIT_API_KEY")
        api_secret = os.getenv("LIVEKIT_API_SECRET")

        if not api_key or not api_secret:
            raise HTTPException(status_code=500, detail="LiveKit credentials not set")

        grant = livekit_api.VideoGrants(
            room_join=True,
            room=req.room_name,
            can_publish=True,
            can_subscribe=True,
        )

        token = livekit_api.AccessToken(api_key, api_secret) \
            .with_identity(req.participant_name) \
            .with_name(req.participant_name) \
            .with_grants(grant) \
            .to_jwt()

        return {"token": token}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ====================================================== GET JOBS FROM SQL DB ===============================================

@app.get("/get-all-jobs")
async def get_all_jobs():
    
    cursor.execute("SELECT * FROM jobs")
    rows = cursor.fetchall()
    return [
        {
            "job_title": row['job_title'],
            "company_name": row['company_name'],
            "location": row['clean_location'],
            "work_style": row['work_style'],
            "work_type": row['work_type'],
            "min_salary": row['min_salary'],
            "max_salary": row['max_salary'],
            "job_description": row['job_description']
        }
        for row in rows
    ]
    

   