# whatsapp_control.py
import pyautogui
import time
import subprocess
from voice import say

def send_whatsapp_message(contact_name: str, message: str):
    try:
        if not contact_name or not message:
            say("Contact name ya message missing hai.")
            return

        say(f"{contact_name} ko WhatsApp par message bhej raha hoon.")
        print(f"📩 Preparing to send message to {contact_name}: {message}")

        subprocess.Popen("start whatsapp:", shell=True)
        time.sleep(6)

        # try to activate window
        try:
            subprocess.Popen(
                'powershell -Command "$ws = New-Object -ComObject WScript.Shell; $ws.AppActivate(\'WhatsApp\')"',
                shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
            )
            time.sleep(1.2)
        except Exception:
            pass

        pyautogui.hotkey("ctrl", "f")
        time.sleep(0.8)
        pyautogui.typewrite(contact_name, interval=0.08)
        time.sleep(2)
        pyautogui.press("down")
        time.sleep(0.3)
        pyautogui.press("enter")
        time.sleep(1)

        pyautogui.typewrite(message, interval=0.05)
        pyautogui.press("enter")

        say(f"Message {contact_name} ko bhej diya gaya hai.")
        print(f"✅ Message sent to {contact_name}: {message}")

    except Exception as e:
        print("❌ WhatsApp send error:", e)
        say("WhatsApp message bhejte waqt koi error aaya.")
