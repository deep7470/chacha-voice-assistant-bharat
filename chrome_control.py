# ----------------------------------------------------------
# Chrome Control — Hybrid Smart Search for Chacha AI
# Uses Gemini AI for understanding and local fallback when offline.
# ----------------------------------------------------------

import re
import time
import webbrowser
import subprocess
import psutil
import os
from voice import say

try:
    import gemini_ai  # uses get_gemini_json for intent understanding
except ImportError:
    gemini_ai = None


# ----------------------------------------------------------
# ✅ Check if Chrome is running
# ----------------------------------------------------------
def is_chrome_running():
    for proc in psutil.process_iter(['name']):
        try:
            if proc.info['name'] and 'chrome' in proc.info['name'].lower():
                return True
        except Exception:
            continue
    return False


# ----------------------------------------------------------
# 🚀 Open Chrome if not already running
# ----------------------------------------------------------
def open_chrome():
    try:
        if is_chrome_running():
            return
        chrome_paths = [
            r"C:\Program Files\Google\Chrome\Application\chrome.exe",
            r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
        ]
        for path in chrome_paths:
            if os.path.exists(path):
                subprocess.Popen([path, "https://www.google.com"],
                                 stdout=subprocess.DEVNULL,
                                 stderr=subprocess.DEVNULL)
                time.sleep(1)
                return
        webbrowser.open("https://www.google.com")
    except Exception as e:
        print("❌ open_chrome error:", e)


# ----------------------------------------------------------
# 🧠 Smart Local Fallback (if Gemini not working)
# ----------------------------------------------------------
def local_understand(text: str):
    """
    Understand user intent without AI:
    Detects YouTube / Website / Google based on patterns.
    """
    text = text.lower().strip()

    # Detect if it's a website link
    if re.search(r"[a-z0-9-]+\.(com|in|org|net|io|gov|edu)", text):
        match = re.search(r"([a-z0-9-]+\.(com|in|org|net|io|gov|edu))", text)
        return "website", match.group(1)

    # Detect YouTube/music intent
    if any(w in text for w in ["youtube", "song", "video", "music", "gaana", "play"]):
        cleaned = re.sub(r"(youtube|song|video|music|gaana|play|search|karo|par|pe)", "", text)
        cleaned = re.sub(r"\s+", " ", cleaned).strip()
        return "youtube", cleaned or "trending"

    # Default: Google search
    cleaned = re.sub(r"(google|search|karo|par|pe|me|on|in|find|ke|ka|ki|ko)", "", text)
    cleaned = re.sub(r"\s+", " ", cleaned).strip()
    return "google", cleaned or "latest news"


# ----------------------------------------------------------
# 🧩 Unified Auto-Search
# ----------------------------------------------------------
def auto_search(user_text: str):
    """
    Automatically understand and search (Gemini + local fallback).
    """
    if not user_text:
        return

    intent, query = None, None

    # Try Gemini first
    if gemini_ai:
        try:
            ai_data = gemini_ai.get_gemini_json(user_text)
            intent = ai_data.get("intent")
            query = ai_data.get("message_text") or user_text
        except Exception as e:
            print("⚠️ Gemini offline or error:", e)

    # Fallback to local logic if Gemini fails or returns chat
    if not intent or intent == "chat":
        intent, query = local_understand(user_text)

    print(f"🎯 Auto-decided: intent={intent} | query={query}")

    # Route automatically
    if intent in ("open_website", "website"):
        open_website(query)
    elif intent == "youtube" or ("song" in user_text.lower() or "video" in user_text.lower()):
        open_youtube(query)
    else:
        open_google(query)


# ----------------------------------------------------------
# 🔍 Google Search
# ----------------------------------------------------------
def open_google(query: str):
    say(f"Google par {query} search kar raha hoon.")
    url = f"https://www.google.com/search?q={query.replace(' ', '+')}"
    ensure_chrome(url)


# ----------------------------------------------------------
# ▶️ YouTube Search
# ----------------------------------------------------------
def open_youtube(query: str):
    say(f"YouTube par {query} dhoond raha hoon.")
    url = f"https://www.youtube.com/results?search_query={query.replace(' ', '+')}"
    ensure_chrome(url)


# ----------------------------------------------------------
# 🌍 Website Open
# ----------------------------------------------------------
def open_website(name: str):
    if not name:
        return
    # Clean up unnecessary words
    name = re.sub(r"(open|website|karo|par|pe|dot)", "", name, flags=re.IGNORECASE)
    name = name.strip().replace(" ", "")
    if not name.startswith("http"):
        name = "https://" + name
    ensure_chrome(name)


# ----------------------------------------------------------
# 🧭 Ensure Chrome runs and open link
# ----------------------------------------------------------
def ensure_chrome(url):
    if not is_chrome_running():
        open_chrome()
        time.sleep(2)
    webbrowser.open(url)
    print(f"✅ Opened: {url}")


# ----------------------------------------------------------
# 🧪 Test Mode
# ----------------------------------------------------------
if __name__ == "__main__":
    say("Chacha hybrid Chrome control active.")
    auto_search("YouTube par Arijit Singh ke sad songs chalao")
    auto_search("Google par Delhi ka weather dikhana")
    auto_search("Open website github dot com")
    auto_search("Show me IPL score")
    auto_search("Play Arijit Singh songs")
