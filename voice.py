# voice.py (replace play_mp3, speak_edge_tts, say)
import os
import asyncio
import pyttsx3
from edge_tts import Communicate
from playsound import playsound   # pip install playsound
import threading

_speech_lock = threading.Lock()

async def _edge_tts_save(text, filename):
    try:
        voice = "hi-IN-MadhurNeural"
        tts = Communicate(text, voice=voice)
        await tts.save(filename)
        return True
    except Exception as e:
        print("❌ Edge-TTS save error:", e)
        return False

def _speak_offline(text):
    try:
        engine = pyttsx3.init()
        engine.setProperty("rate", 165)
        engine.say(text)
        engine.runAndWait()
        return True
    except Exception as e:
        print("❌ pyttsx3 error:", e)
        return False

def say(text):
    text = (text or "").strip()
    if not text:
        return
    print(f"🗣️ Chacha will say: {text}")
    with _speech_lock:
        try:
            tmp = "temp_chacha.mp3"
            ok = asyncio.run(_edge_tts_save(text, tmp))
            if ok and os.path.exists(tmp):
                try:
                    playsound(tmp)
                except Exception as e:
                    print("⚠️ playsound error:", e)
                try:
                    os.remove(tmp)
                except:
                    pass
            else:
                _speak_offline(text)
        except Exception as e:
            print("⚠️ Voice.say exception:", e)
            _speak_offline(text)
