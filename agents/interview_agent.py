import asyncio
import os
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

class SarahInterviewer(Agent):
    def __init__(self) -> None:
        super().__init__(
            instructions=(
                "You are a professional HR interviewer named Sarah. "
                "Conduct a 5-minute screening interview. "
                "1. Welcome the candidate warmly. "
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
    session = AgentSession(
        stt=openai.STT(model="whisper-1"),
        llm=openai.LLM(model="gpt-4o-mini"),
        tts=openai.TTS(voice="alloy"),
        vad=silero.VAD.load(),
        turn_detection=MultilingualModel(),   
    )

    await session.start(room=ctx.room, agent=SarahInterviewer())
    await session.generate_reply(
        instructions="Say hello to the candidate and ask them to briefly introduce themselves."
    )

if __name__ == "__main__":
    cli.run_app(server)