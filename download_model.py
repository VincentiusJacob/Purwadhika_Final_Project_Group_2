from livekit.plugins.silero import VAD
from livekit.plugins.turn_detector.multilingual import MultilingualModel


VAD.load()                         
MultilingualModel._ensure_model()   # auto-download model kalau belum ada

print("All models ready")