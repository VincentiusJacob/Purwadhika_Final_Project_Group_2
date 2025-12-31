import streamlit as st
import requests
import os
from dotenv import load_dotenv
from data.global_state import state as global_state

load_dotenv()

API_URL = os.getenv("BACKEND_URL", "http://localhost:8000")
LIVEKIT_URL = os.getenv("LIVEKIT_URL") 

st.set_page_config(page_title="AI Mock Interview", layout="centered")

preference_job = st.session_state.get('prefered_jobs', {})

# ini sebaiknya pake session state
username = global_state["user_name"]

st.title("🎙️ Interview with Sarah")

if preference_job.get('job_title') == None:
    st.warning("⚠️ You need to analyze your CV first AND select your prefereced job to generate the necessary data for this feature.")
else: 

    if "token" not in st.session_state:
        st.session_state.token = None


    if st.button("Start Session"):
        try:
            room_name = f"interview-{username.lower().replace(' ', '-')}"
            payload = {"room_name": room_name, "participant_name": username}
            
            res = requests.post(f"{API_URL}/get-livekit-token", json=payload)
            
            if res.status_code == 200:
                st.session_state.token = res.json()["token"]
                st.success("Connected to Sarah! Click 'Start Audio' below.")
            else:
                st.error(f"Failed to get token: {res.text}")
        except Exception as e:
            st.error(f"Connection Error: {e}")


    def client_html(token, server_url):
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
        <style>
            body {{ font-family: sans-serif; background: #0e1117; color: white; display: flex; flex-direction: column; align-items: center; justify-content: center; }}
            button {{ padding: 12px 24px; background: #ef4444; color: white; border: none; border-radius: 5px; cursor: pointer; font-size: 16px; margin-top: 20px; }}
            button:disabled {{ background: #555; cursor: not-allowed; }}
            #status {{ font-size: 18px; font-weight: bold; margin-bottom: 10px; }}
        </style>
        </head>
        <body>
            <div id="status">Ready to Connect</div>
            <button id="btn" onclick="startCall()">Start Audio</button>

            <script type="module">
                import {{ Room, RoomEvent, createLocalTracks }} from "https://cdn.jsdelivr.net/npm/livekit-client/dist/livekit-client.esm.mjs";

                const btn = document.getElementById('btn');
                const status = document.getElementById('status');
                let room;

                window.startCall = async () => {{
                    btn.disabled = true;
                    btn.innerText = "Connecting...";
                    
                    try {{
                        room = new Room();
                        // Connect ke LiveKit Cloud pakai Token dari Backend
                        await room.connect('{server_url}', '{token}');
                        
                        // Nyalakan Mic User
                        const tracks = await createLocalTracks({{ audio: true, video: false }});
                        await room.localParticipant.publishTrack(tracks[0]);

                        // Dengar Suara Sarah
                        room.on(RoomEvent.TrackSubscribed, (track) => {{
                            if (track.kind === 'audio') {{
                                const el = track.attach();
                                document.body.appendChild(el);
                                status.innerText = "Sarah is speaking 🟢";
                            }}
                        }});
                        
                        room.on(RoomEvent.TrackUnsubscribed, () => {{
                            status.innerText = "Your turn to speak 🎤";
                        }});

                        status.innerText = "Connected! Say Hello to Sarah.";
                        btn.innerText = "Connected";
                        
                    }} catch (e) {{
                        status.innerText = "Error: " + e.message;
                        btn.disabled = false;
                        btn.innerText = "Retry";
                    }}
                }}
            </script>
        </body>
        </html>
        """

    if st.session_state.token:
        st.components.v1.html(client_html(st.session_state.token, LIVEKIT_URL), height=300)