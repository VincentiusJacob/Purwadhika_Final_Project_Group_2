from typing_extensions import TypedDict
import streamlit as st
import json
import os

DB_FILE = "user_data.json"

# TypedDict definition of Global State
state = {
    "user_summary": "",
    "user_name": "",
    "prefered_jobs": {},
    "session_id": 0,
    "assessment": ""
}

def save_state():
    """Save the current in-memory state to a JSON file."""

    try:
        with open(DB_FILE, "w") as f:
            json.dump(state, f, indent=4)
    except Exception as e:
        print(f"Error saving state: {e}")

def load_state():
    """Loads the state from the JSON file into memory."""

    global state
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, "r") as f:
                loaded_data = json.load(f)
                state.update(loaded_data)
        except Exception as e:
            print(f"Error loading state: {e}")

load_state()


