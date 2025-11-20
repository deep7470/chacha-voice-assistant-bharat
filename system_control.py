# system_control.py
# Auto App Search & standard system controls.
# This opens apps using the Windows Start menu (press Win, type, Enter).
# Works for store apps, installed programs and games.

import pyautogui
import subprocess
import time
import os
import shutil
from pathlib import Path
from voice import say

def take_screenshot():
    try:
        desktop = Path.home() / "Desktop"
        desktop.mkdir(parents=True, exist_ok=True)
        filename = desktop / f"screenshot_{int(time.time())}.png"
        img = pyautogui.screenshot()
        img.save(str(filename))
        say(f"Screenshot saved to Desktop as {filename.name}.")
    except Exception as e:
        print("❌ Screenshot error:", e)
        say("Failed to take screenshot.")

def open_settings():
    try:
        subprocess.Popen("start ms-settings:", shell=True)
        say("Opening Settings.")
    except Exception as e:
        print("❌ open_settings error:", e)
        say("Could not open settings.")

def lock_pc():
    try:
        say("Locking the computer now.")
        subprocess.call("rundll32.exe user32.dll,LockWorkStation")
    except Exception as e:
        print("❌ lock_pc error:", e)
        say("Could not lock the computer.")

def shutdown_pc():
    try:
        say("Shutting down in 10 seconds. Please save your work.")
        subprocess.Popen("shutdown /s /t 10", shell=True)
    except Exception as e:
        print("❌ shutdown_pc error:", e)
        say("Could not schedule shutdown.")

def restart_pc():
    try:
        say("Restarting system now.")
        subprocess.Popen("shutdown /r /t 5", shell=True)
    except Exception as e:
        print("❌ restart_pc error:", e)
        say("Could not restart the computer.")

def open_app(app_name: str):
    """
    Attempt to open an app by searching with Windows Start.
    If that fails, fallback to Run dialog.
    """
    try:
        if not app_name:
            say("Which application should I open?")
            return

        app_name = app_name.strip()
        say(f"Opening {app_name}, please wait.")
        print(f"🔍 open_app: {app_name}")

        # Step 1: Windows Start search
        pyautogui.press("win")
        time.sleep(0.8)
        pyautogui.typewrite(app_name, interval=0.04)
        time.sleep(1.0)
        pyautogui.press("enter")
        time.sleep(1.5)

        # Basic check: give user a short confirmation
        say(f" open {app_name}.")

        # If app_name looks like an executable and exists, try direct
        lower = app_name.lower()
        known = {
            "notepad": "notepad.exe",
            "calculator": "calc.exe",
            "paint": "mspaint.exe",
            "chrome": r"C:\Program Files\Google\Chrome\Application\chrome.exe",
            "edge": r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
        }
        for key, path in known.items():
            if key in lower:
                if os.path.exists(path):
                    subprocess.Popen(path)
                    say(f"Opened {key}.")
                    return


    except Exception as e:
        print("❌ open_app error:", e)
        say(f"Sorry, I couldn't open {app_name}.")
