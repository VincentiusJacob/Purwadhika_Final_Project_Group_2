from typing_extensions import TypedDict

# TypedDict definition of Global State
state = {
    "user_summary": str,
    "best_jobs": list[dict],
    "session_id": int,
    "assessment": str
}