import streamlit as st
import os
from livekit import api
from dotenv import load_dotenv

load_dotenv()

LIVEKIT_URL = os.getenv("LIVEKIT_URL")
LIVEKIT_API_KEY = os.getenv("LIVEKIT_API_KEY")
LIVEKIT_API_SECRET = os.getenv("LIVEKIT_API_SECRET")

if not all([LIVEKIT_URL, LIVEKIT_API_KEY, LIVEKIT_API_SECRET]):
    st.error("Missing LiveKit environment variables.")
    st.stop()

st.set_page_config(page_title="AI Mock Interview", layout="centered")

@st.cache_data
def get_token(room: str, user: str):
    return api.AccessToken(LIVEKIT_API_KEY, LIVEKIT_API_SECRET) \
        .with_identity(user).with_name(user) \
        .with_grants(api.VideoGrants(room_join=True, room=room,
                                     can_publish=True, can_subscribe=True,
                                     can_publish_data=True)).to_jwt()

@st.cache_data
def client_html(token: str, url: str) -> str:
    return f"""
        <!DOCTYPE html>
        <html>
        <head>
        <meta charset="utf-8"/>
        </head>
        <body style="margin:0;background:#111;color:#fff;font-family:-apple-system;display:flex;align-items:center;justify-content:center;height:100vh;">
        <div style="text-align:center">
        <h2>AI Mock Interview</h2>
        <p id="status">Ready</p>
        <button id="btn" onclick="run()" style="padding:12px 24px;border:none;border-radius:24px;background:#ef4444;color:#fff;font-size:16px;cursor:pointer">Start Interview</button>
        </div>
        <script type="module">
        import {{Room,createLocalTracks}} from 'https://esm.sh/livekit-client@latest';
        const btn=document.getElementById('btn'),status=document.getElementById('status');
        let room,connected=0;
        async function run(){{
        if(connected){{room.disconnect();connected=0;btn.textContent='Start Interview';status.textContent='Ready';return;}}
        btn.disabled=1;btn.textContent='Connecting...';status.textContent='Connecting...';
        try{{
            room=new Room();await room.connect('{url}','{token}');
            const [mic]=await createLocalTracks({{audio:true}});
            await room.localParticipant.publishTrack(mic);
            room.on('trackSubscribed',(t)=>{{if(t.kind==='audio'){{t.attach().play();status.textContent='Sarah speaking';}}}});
            room.on('trackUnsubscribed',()=>status.textContent='Your turn');
            room.on('disconnected',()=>{{connected=0;btn.textContent='Start Interview';status.textContent='Ready';}});
            connected=1;btn.textContent='End Interview';btn.disabled=0;status.textContent='Connected';
        }}catch(e){{alert(e.message);btn.disabled=0;btn.textContent='Start Interview';status.textContent='Failed';}}
        }}
        </script>
        </body>
        </html>
    """

st.title("AI Mock Interview")
name = st.text_input("Your name", value="John Doe")
if st.button("Create Session", type="primary"):
    if name.strip():
        room = f"interview-{name.lower().replace(' ', '-')}"
        token = get_token(room, name)
        st.success("Session ready")
        st.components.v1.html(client_html(token, LIVEKIT_URL), height=400)
    else:
        st.error("Name cannot be empty")