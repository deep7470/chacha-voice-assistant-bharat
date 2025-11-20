import time
import threading
from voice import say

def set_reminder(delay_seconds: int, message: str):
    """Set a reminder after specific seconds."""
    try:
        say(f"ठीक है, मैं {delay_seconds} सेकंड बाद याद दिला दूँगा.")
        print(f"⏱️ Reminder set for {delay_seconds} seconds: {message}")
        threading.Timer(delay_seconds, trigger_reminder, args=[message]).start()
    except Exception as e:
        print("❌ Reminder error:", e)


def trigger_reminder(message: str):
    """Speak reminder when time is up."""
    say(f"⏰ याद दिलाना: {message}")
    print(f"🔔 Reminder Triggered: {message}")


def extract_delay_and_message(text: str):
    """Extract delay (seconds/minutes) and message from user's command."""
    text = text.lower()
    delay = 0

    # Detect seconds
    if "second" in text:
        parts = text.split("second")[0].split()
        for word in parts[::-1]:
            if word.isdigit():
                delay = int(word)
                break

    # Detect minutes
    elif "minute" in text or "min" in text:
        parts = text.split("minute")[0].split()
        for word in parts[::-1]:
            if word.isdigit():
                delay = int(word) * 60
                break

    # Default safety (if no number found)
    if delay == 0:
        delay = 10  # default 10 sec

    # Extract the actual reminder message
    if "yaad dilana" in text:
        message = text.split("yaad dilana")[-1].strip()
    elif "remind" in text:
        message = text.split("remind")[-1].strip()
    else:
        message = text

    # Remove leftover timing words
    message = message.replace("after", "").replace("seconds", "").replace("minutes", "").strip()

    return delay, message
