import time
import speech_recognition as sr
import gemini_ai
import chrome_control
import music_control
import interactive_object_detection as iobj
import system_control
import whatsapp_control
import reminder_control
from voice import say
import psutil
import datetime


# ----------------------------------------------------------
# 🎧 Listen Once
# ----------------------------------------------------------
def listen_once(timeout=12, phrase_time_limit=8):
    r = sr.Recognizer()
    try:
        with sr.Microphone() as source:
            r.pause_threshold = 0.6
            r.adjust_for_ambient_noise(source, duration=0.5)
            audio = r.listen(source, timeout=timeout, phrase_time_limit=phrase_time_limit)
    except (sr.WaitTimeoutError, KeyboardInterrupt):
        return "none"
    except Exception as e:
        print("🎤 Mic error:", e)
        return "none"
    try:
        text = r.recognize_google(audio, language="en-IN").strip()
        print(f"🗣️ Heard: {text}")
        return text
    except Exception:
        return "none"


# ----------------------------------------------------------
# 🔉 Volume Parser
# ----------------------------------------------------------
def extract_volume_level(text):
    """Extract numeric or keyword-based volume level (0–1)."""
    text = text.lower()
    if "full" in text or "hundred" in text or "max" in text or "poori" in text:
        return 1.0
    if "mute" in text or "zero" in text or "band" in text:
        return 0.0
    for word in text.split():
        if word.isdigit():
            level = int(word) / 100
            return min(max(level, 0.0), 1.0)
    return None


# ----------------------------------------------------------
# 🧠 Process Command
# ----------------------------------------------------------
def process_command(user_input: str):
    if not user_input or user_input.strip().lower() in ("none", ""):
        return None

    user_text = user_input.strip().lower()
    print(f"\n🎯 Processing: {user_text}")

    # 🔉 Voice-controlled Volume Commands
    if any(k in user_text for k in ["volume", "awaaz", "sound"]):
        import re
        match = re.search(r"(\d+)\s*%?", user_text)
        if match:
            level = int(match.group(1))
            music_control.set_system_volume(level)
            say(f"Awaaz {level} percent kar di.")
            return
        elif any(k in user_text for k in ["full", "max", "poori", "zyada"]):
            music_control.set_system_volume(100)
            say("Awaaz poori kar di.")
            return
        elif any(k in user_text for k in ["kam", "ghata", "low"]):
            music_control.set_system_volume(30)
            say("Awaaz kam kar di.")
            return

    # 🕒 Reminder (MOVE THIS OUTSIDE volume block)
    if any(k in user_text for k in ["yaad dilana", "remind", "alarm lagao", "set timer"]):
        delay, msg = reminder_control.extract_delay_and_message(user_text)
        if delay > 0 and msg:
            reminder_control.set_reminder(delay, msg)
        else:
            say("Mujhe samajh nahi aaya kitne time baad ya kya yaad dilana hai.")
        return
    # 🕒 Time and Date
    if any(k in user_text for k in ["time", "samay", "kitne baje", "date", "aaj ki tareekh", "tarikh", "date batao", "aaj kya date hai"]):
        now = datetime.datetime.now()
        current_time = now.strftime("%I:%M %p")
        current_date = now.strftime("%A, %d %B %Y")
        if "time" in user_text or "baje" in user_text or "samay" in user_text:
            say(f"Abhi {current_time} baj rahe hain.")
            print(f"🕒 Time: {current_time}")
        else:
            say(f"Aaj {current_date} hai.")
            print(f"📅 Date: {current_date}")
        return


    # 💬 AI understanding via Gemini
    ai_data = {}
    intent = "chat"
    target = ""
    contact = None
    try:
        ai_data = gemini_ai.get_gemini_json(user_text)
        intent = ai_data.get("intent", "chat")
        target = ai_data.get("message_text") or ""
        contact = ai_data.get("contact_name")
    except Exception as e:
        print("⚠️ Gemini JSON error:", e)

    print(f"🧩 Intent: {intent} | target: {target} | contact: {contact}")

    # Exit
    if any(w in user_text for w in ["exit", "quit", "band kar", "goodbye", "stop program"]):
        say("Goodbye! Chacha band ho raha hai.")
        return "exit"

    # WhatsApp
    if intent == "send_message":
        if contact and target:
            whatsapp_control.send_whatsapp_message(contact, target)
        else:
            say("Contact ya message samajh nahi aaya.")
        return

    # App open
    if intent in ("open_app", "start_app", "open"):
        app_name = target or user_text.replace("open", "").strip()
        system_control.open_app(app_name)
        return

    # System controls
    if intent == "take_screenshot": system_control.take_screenshot(); return
    if intent == "lock_pc": system_control.lock_pc(); return
    if intent == "shutdown_pc": system_control.shutdown_pc(); return
    if intent == "restart_pc": system_control.restart_pc(); return
    if intent == "open_settings": system_control.open_settings(); return

    # 🔋 Battery status
    if any(k in user_text for k in ["battery", "charge", "battery status", "kitni battery", "charging hai ya nahi"]):
        battery = psutil.sensors_battery()
        if battery:
            percent = int(battery.percent)
            charging = "charging ho rahi hai" if battery.power_plugged else "charging nahi ho rahi hai"
            say(f"Battery {percent} percent hai aur {charging}.")
            print(f"🔋 Battery: {percent}% | {charging}")
        else:
            say("Battery information mil nahi rahi hai.")
        return

    # 🎵 Music controls
    if "youtube" in user_text:
        chrome_control.auto_search(user_text)
        return
    if intent == "play_music": music_control.play_track(0); return
    if intent == "next_music": music_control.play_next(); return
    if intent == "stop_music": music_control.stop_music(); return
    if intent == "resume_music": music_control.resume_music(); return
    if intent == "pause_music": music_control.pause_music(); return

    # 📷 Object Detection
    if any(k in user_text for k in
           ["ye kya", "what is this", "dekho ye kya", "batado ye", "chacha ye kya", "mere haath me kya",
            "dekho yah kya hai"]):
        try:
            say("Camera chalu kar raha hoon, ek second...")
            iobj.start_camera_background()
            time.sleep(0.5)
            iobj.ask_and_describe()
        except Exception as e:
            say("Camera start nahi ho paaya.")
            print("📷 Camera error:", e)
        return

    # 🌐 Search / Website
    if intent in ("search", "open_website", "browse", "google_search", "youtube_search"):
        chrome_control.auto_search(target or user_text)
        return

    # 🤖 Default Chat
    gemini_ai.get_gemini_response(user_text, speak=True)
    return


# ----------------------------------------------------------
# 🏁 Main Loop
# ----------------------------------------------------------
def main():
    say("नमस्ते, मैं चाचा हूँ! बताइए, आपकी क्या मदद कर सकता हूँ?")
    print("✅ Chacha is online and ready.")

    while True:
        query = listen_once(timeout=10, phrase_time_limit=8)
        if query == "none":
            continue
        result = process_command(query)
        if result == "exit":
            break
        time.sleep(0.2)


if __name__ == "__main__":
    main()
