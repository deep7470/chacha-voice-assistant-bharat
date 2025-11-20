# gemini_ai.py
# ----------------------------------------------------------
# Natural Language Understanding + Intent Classification for Chacha
# Handles mixed Hindi/English commands (no manual keywords)
# ----------------------------------------------------------

import google.generativeai as genai
import json
import os
import time
import re
from voice import say


# ----------------------------------------------------------
# API CONFIG
# ----------------------------------------------------------
API_KEY = os.environ.get("GEMINI_API_KEY")
if not API_KEY:
    print("❌ GEMINI_API_KEY not found in environment.")
else:
    genai.configure(api_key=API_KEY)
    print("✅ Gemini AI configured successfully with gemini-2.5-flash.")
model = genai.GenerativeModel("gemini-2.5-flash") if API_KEY else None


# ----------------------------------------------------------
# FALLBACK SYSTEM INSTRUCTION
# ----------------------------------------------------------
SYSTEM_INSTRUCTION = """
You are 'Chacha' — an Indian AI assistant with a confident, fun, and friendly personality.
You talk casually like a helpful friend — slightly witty, like Jarvis but with desi flavor.
Always refer to yourself as "Chacha" and address the user politely as "aap" or "beta" depending on tone.
You can use short Hindi-English mix replies, not robotic.
Return responses naturally and quickly.

If user says “volume badhao”, “awaz full karo”, “volume 70 percent”, “mute karo”, etc,
  then intent="set_volume" and message_text should include a numeric level (0.0 to 1.0) if possible.
  Example: "volume 50 percent" → level 0.5, "full" → 1.0, "mute" → 0.0.

You will return a STRICT JSON object with the following keys:
{
 "intent": "<one of: chat, open_app, open_website, search, play_music, pause_music, resume_music, stop_music, next_music,
            send_message, detect_object, take_screenshot, lock_pc, shutdown_pc, restart_pc, open_settings>",
 "contact_name": "<optional contact name or None>",
 "message_text": "<main topic, search term, or message text>"
}

Rules:
- Detect what the user *wants to do*, not literal translation.
- If user says something like “google pe search karo python tutorial”, intent=search, message_text="python tutorial"
- If user says “open YouTube”, intent=open_app, message_text="youtube"
- If user says “play music” or “song chalao”, intent=play_music
- If user is chatting casually (“chacha how are you?”), intent=chat
- Preserve emojis, names, and Hinglish exactly as said.
Return ONLY valid JSON, nothing else.
"""


# ----------------------------------------------------------
# GENERATE JSON INTENT
# ----------------------------------------------------------
def get_gemini_json(user_text: str):
    """Extracts intent and target text from user input."""
    if not model:
        return {"intent": "chat", "contact_name": None, "message_text": user_text}

    prompt = f"{SYSTEM_INSTRUCTION}\nUser said: {user_text}"
    try:
        response = model.generate_content(
            prompt,
            generation_config={"response_mime_type": "application/json"},
        )
        text = getattr(response, "text", "").strip()
        print("📜 Gemini raw JSON:", text)
        # inside get_gemini_json(), before json.loads(text)
        json_text = re.search(r"\{.*\}", text, re.DOTALL)
        if json_text:
            text = json_text.group(0)
        data = json.loads(text)
        return {
            "intent": data.get("intent", "chat"),
            "contact_name": data.get("contact_name"),
            "message_text": data.get("message_text"),
        }
    except Exception as e:
        print("❌ Gemini JSON parse error:", e)
        # fallback simple keyword-based understanding
        low = user_text.lower()
        if "open" in low or "start" in low:
            return {"intent": "open_app", "contact_name": None, "message_text": user_text}
        if "search" in low or "google" in low or "youtube" in low:
            return {"intent": "search", "contact_name": None, "message_text": user_text}
        if "music" in low or "song" in low or "play" in low:
            return {"intent": "play_music", "contact_name": None, "message_text": user_text}
        return {"intent": "chat", "contact_name": None, "message_text": user_text}


# ----------------------------------------------------------
# NATURAL CHAT RESPONSE
# ----------------------------------------------------------
def get_gemini_response(prompt, speak=True):
    """Generate Chacha-style friendly conversational response."""
    if not model:
        say("Sorry, I’m not connected to Gemini right now.")
        return "error"

    try:
        response = model.generate_content(
            f"You are Chacha, a friendly voice assistant. "
            f"Understand tone (Hindi/English/Hinglish) and reply naturally, friendly, short.\nUser said: {prompt}",
            generation_config={"temperature": 0.7},
        )
        text = getattr(response, "text", "").strip()
        if not text:
            text = "Sorry, I couldn’t understand that."
        print("🧠 Gemini says:", text)
        if speak:
            say(text)
        return text
    except Exception as e:
        print("❌ Gemini error:", e)
        say("Something went wrong with AI response.")
        return "error"
