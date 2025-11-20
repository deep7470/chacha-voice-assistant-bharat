# Chacha – AI Voice Assistant

Chacha एक स्मार्ट AI Voice Assistant है जो आपकी आवाज़ को समझ कर कई काम कर सकता है।  
यह Google Gemini, Speech Recognition, YOLO object detection, और सिस्टम कंट्रोल्स का उपयोग करता है।

---

## 🔥 Features

### 🎤 Voice Commands
- "Chacha, play music" / "play music"  
- "Pause the music" / "resume music" / "next music" / "stop music"  
- "Volume 50 percent" / "awaaz 70%"  
- "Open Notepad" / "open chrome"  
- "Search Python tutorial"  
- "Take screenshot"

### 🎵 Music Control
- Local music play, pause, resume, next, stop  
- System volume control (NirCmd or platform helper)

### 🤖 AI Chat (Gemini)
- Chat responses via Gemini model (configured in `gemini_ai.py`)  
- Uses voice output (edge-tts / pyttsx3 fallback)

### 🌐 Web Features
- Auto Google / YouTube search via voice

### 🖥️ System Control
- Open apps, lock, shutdown, restart, open settings, take screenshot

### 🔋 Battery Status
- "Battery kitni hai?" — batata hai percentage aur charging state

### 🧠 YOLO Object Detection
- "Chacha, ye kya hai?" — camera se object detect karke describe karega

### 🕒 Reminders
- "Mujhe 10 second baad yaad dilana ki chai banani hai" — simple timer reminders

---

## 🛠️ Installation

1. **Clone the repo**
```bash
git clone https://github.com/<your-username>/chacha-voice-assistant.git
cd chacha-voice-assistant


2.Create virtual environment
python -m venv .venv
# Windows:
.venv\Scripts\activate
# macOS / Linux:
source .venv/bin/activate

3.Install requirements
pip install -r requirements.txt


4.NirCmd (Windows only — for system volume)

Download from: https://www.nirsoft.net/utils/nircmd.html

Place nircmd.exe at C:\Users\hp\nircmd.exe (ya path update kar lo music_control.py mein)


5.Set API keys (optional)

Gemini / ElevenLabs etc. ko agar use kar rahe ho to apni keys OS environment me set karo. Example (Windows PowerShell):
setx GEMINI_API_KEY "your_gemini_key_here"
setx ELEVENLABS_API_KEY "your_elevenlabs_key_here"
# close and reopen terminal to take effect

6.Run

python main_assistant.py

🧪 Quick tests (smoke)
---------------------------------------------------------------------------------------------------------------------------
play music / pause music / resume music / next music

volume 50 percent — system volume change

yaad dilana 10 second coffee — reminder fires after 10s

Chacha, ye kya hai — object detection (camera required)

open notepad / search python tutorial — app/search

------------------------------------------------------------------------------------------------------------------------------
❤️ Credits

Developed by Bharat Singh Chouhan
AI powered by Google Gemini

📜 License

This project is open-source under the MIT License.


































