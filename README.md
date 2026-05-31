# FOCUS GUARD 🎯

> **The productivity tool that roasts you back into focus.**  
> Built at hackathon speed by **Glitch Squad**

---

## 🚀 What is Focus Guard?

Focus Guard is a real-time attention monitoring system that uses your webcam to detect when you're losing focus — and roasts you out loud to snap you back.

No cloud. No subscription. No mercy.

---

## ⚡ Features

- 👁️ Real-time face & eye detection using OpenCV Haar cascades
- 😴 3 distraction states — Drowsy, Looking Away, No Face
- 🔊 Voice roasts via pyttsx3 — it literally talks back at you
- 📊 Live cyberpunk dashboard — focus score, distraction count, session timer
- 🔒 100% offline & private — your face never leaves your machine
- 🏆 Session report with final verdict at the end

---

## 🛠️ Tech Stack

| Layer | Tech |
|-------|------|
| Computer Vision | OpenCV, Haar Cascades |
| Audio | pyttsx3 |
| Backend API | Flask, Flask-CORS |
| Frontend | Vanilla HTML/CSS/JS |
| Data Bridge | Local JSON file |

---

## 📦 Setup & Run

1. Install dependencies
pip install -r requirements.txt
pip install opencv-python pyttsx3

2. Run the CV engine (Terminal 1)
python main.py

3. Run the Flask server (Terminal 2)
python server.py

4. Open the dashboard
http://localhost:5000

---

## 🧠 How It Works

Webcam → OpenCV detects face/eyes → classifies behavior
       → updates focus_stats.json
       → Flask serves it at /stats
       → Dashboard polls every second
       → You get roasted

3 distraction states:
- Drowsy — eyes closed or not detected
- Looking Away — face off-center
- No Face — you vanished entirely

---

## 💀 Sample Roasts

- "Bro is sleeping like exams are optional"
- "Error 404: Focus not found"
- "Your attention span called — it wants a divorce"

---

## 🔮 What's Next

- WebSocket for true real-time
- Custom roast packs
- Team dashboard
- Gamified focus streaks

---

## 👥 Team

Glitch Squad — Built with zero sleep and maximum chaos.
