from livekit.agents import (
    Agent,
    AgentSession,
    JobContext,
    RunContext,
    WorkerOptions,
    cli,
    function_tool,
)
from livekit.plugins import groq, silero

from dotenv import load_dotenv

load_dotenv(dotenv_path=".env.local")

@function_tool
async def check_payment_status(context: RunContext, invoice_id: str):
    """Returns payment status for an invoice."""
    # Simulated logic
    return {
        "invoice_id": invoice_id,
        "status": "Paid" if invoice_id.endswith("7") else "Pending"
    }

@function_tool
async def summarize_expenses(context:RunContext, time_range: str):
    """Summarizes expenses over a time range (mock)."""
    return {
        "time_range": time_range,
        "total_expenses": 26450,
        "categories": {
            "software": 8200,
            "services": 5400,
            "utilities": 10850,
        }
    }


async def entrypoint(ctx: JobContext):
    await ctx.connect()

    agent = Agent(
        instructions="""
            You are a friendly voice assistant built by Livekit.
            Every conversation should start by greeting.
            Only use the appropriate tool based on what user asks.
            Do not fabricate or guess the financial data.
            Always follow the user's inputs.
            """,
        tools=[check_payment_status,summarize_expenses],
    )
    session = AgentSession(
        vad=silero.VAD.load(),
        stt=groq.STT(),  
        llm=groq.LLM(model="llama-3.3-70b-versatile"),
        tts=groq.TTS(model="playai-tts"), 
    )

    await session.start(agent=agent, room=ctx.room)
    await session.generate_reply(instructions="Say hello, then ask the user how their day is going and ask how you can assist with financial tasks.")

if __name__ == "__main__":
    cli.run_app(WorkerOptions(entrypoint_fnc=entrypoint))