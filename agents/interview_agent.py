import asyncio
import os
import json
import sys
from dotenv import load_dotenv
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
from livekit.agents import (
    Agent,
    AgentServer,
    AgentSession,
    JobContext,
    cli,
    llm,
)
from livekit.plugins import openai, silero
from livekit.plugins.turn_detector.multilingual import MultilingualModel

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from data.database import load_user_data


load_dotenv()

def start_health_check_server():
    class HealthCheckHandler(BaseHTTPRequestHandler):
        def do_GET(self):
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b"OK")
        
        def log_message(self, format, *args):
            pass

    # Cloud Run mewajibkan listen di port 8080 (atau sesuai env PORT)
    port = int(os.getenv("PORT", 8080))
    server = HTTPServer(("0.0.0.0", port), HealthCheckHandler)
    print(f"✅ Dummy Health Check Server listening on port {port}")
    server.serve_forever()
# -----------------------------------------------------

def load_user_context():
    """
    Mengambil data user terbaru dari MongoDB Cloud.
    """

    data = load_user_data()
    
    if data:
        print(f"Data found for user: {data.get('user_name')}")
        return data
    else:
        print("No user data found in MongoDB.")
        return None
    
# class SarahInterviewer(Agent):
#     def __init__(self) -> None:
#         super().__init__(
#             instructions=(
#                 "You are a professional HR interviewer named Sarah. "
#                 "Conduct a 5-minute screening interview. "
#                 "1. Welcome the candidate warmly. "
#                 "2. Wait for the candidate to speak introducing theirself"
#                 "2. After the user speaks, wait for 2 seconds, then Ask a follow-up based on their introduction. "
#                 "3. Ask one behavioural question. "
#                 "4. Keep answers concise (1-2 sentences). "
#                 "5. End politely after 3-4 questions."
#             )
#         )

class SarahInterviewer(Agent):
    def __init__(self, user_data) -> None:
        
        # Default values 
        name = "Candidate"
        summary = "a candidate looking for a job"
        target_job_str = "a potential role at our company" 

        if user_data:
            name = user_data.get("user_name", "Candidate")
            print(f"User name: {name}")
            summary = user_data.get("user_summary", "a candidate looking for a job")
            
            prefered_job = user_data.get("prefered_jobs", {})

        
            if prefered_job and isinstance(prefered_job, dict):
                title = prefered_job.get("job_title", "Software Engineer")
                company = prefered_job.get("company_name", "Unknown Company")
      
                target_job_str = f"the position of {title} at {company}"

        super().__init__(
            instructions=(
                f"You are a professional HR interviewer named Sarah. "
                f"Conduct a 5-minute screening interview with {name}. "
                f"You are interviewing a candidate with this background: {summary}. "
                f"You are interviewing them for {target_job_str}. "
                "1. Welcome the candidate warmly by greeting by their name. "
                "2. Wait for the candidate to speak introducing theirself. " # Typo fix: themself/themselves
                "3. After the user speaks, wait for 2 seconds, then Ask a follow-up based on their introduction. " # Fixed number sequence
                "4. Ask one behavioural question. "
                "5. Keep answers concise (1-2 sentences). "
                "6. End politely after 3-4 questions."
            )
        )


server = AgentServer()

@server.rtc_session()
async def my_agent(ctx: JobContext):
    user_data = load_user_context()

    session = AgentSession(
        stt=openai.STT(model="whisper-1"),
        llm=openai.LLM(model="gpt-4o-mini"),
        tts=openai.TTS(voice="alloy"),
        vad=silero.VAD.load(),
        turn_detection=MultilingualModel(),   
    )

    await session.start(room=ctx.room, agent=SarahInterviewer(user_data))
    await session.generate_reply(
        instructions="Greet the candidate by name if known, or warmly welcome them to the interview for the specific role found in their data."
    )

if __name__ == "__main__":

    threading.Thread(target=start_health_check_server, daemon=True).start()
    
    if len(sys.argv) == 1:
        print("⚠️ No command provided. Defaulting to 'start'...")
        sys.argv.append("start")

    cli.run_app(server)