from livekit.agents import cli, WorkerOptions
from agents.supervisor_agent import build_supervisor_graph

worker = build_supervisor_graph()
cli.run_app(WorkerOptions(entrypoint_fnc=worker))