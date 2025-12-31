import asyncio
import os
import json
from dotenv import load_dotenv
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


load_dotenv()

def load_user_context():
    try:
        with open("user_data.json", "r") as f:
            data = json.load(f)
            return data
    except:
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
                "2. Wait for the candidate to speak introducing theirself"
                "2. After the user speaks, wait for 2 seconds, then Ask a follow-up based on their introduction. "
                "3. Ask one behavioural question. "
                "4. Keep answers concise (1-2 sentences). "
                "5. End politely after 3-4 questions."
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
    cli.run_app(server)