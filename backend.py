import cv2
import random
import time
import sys
import json
import os
import threading

# ─── Optional audio via pyttsx3 ──────────────────────────────────────────────
try:
    import pyttsx3
    AUDIO_ENABLED = True
    print("✅ pyttsx3 found — audio enabled!")
except ImportError:
    AUDIO_ENABLED = False
    print("⚠️  pyttsx3 not found — audio disabled. Run: pip install pyttsx3")

# Create a new engine per speak call to avoid "already running" lock
def speak(text):
    if not AUDIO_ENABLED:
        return
    def _run():
        
        
        try:
            engine = pyttsx3.init()
            engine.setProperty('rate', 155)
            engine.setProperty('volume', 1.0)
            # Pick a slightly robotic / fun voice if available
            voices = engine.getProperty('voices')
            if voices:
                engine.setProperty('voice', voices[0].id)
            engine.say(text)
            engine.runAndWait()
            engine.stop()
        except Exception as e:
            print(f"⚠️  Audio error: {e}")
    t = threading.Thread(target=_run, daemon=True)
    t.start()

# ─── Load cascades ────────────────────────────────────────────────────────────
face_cascade = cv2.CascadeClassifier(
    cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
)
eye_cascade = cv2.CascadeClassifier(
    cv2.data.haarcascades + 'haarcascade_eye.xml'
)

# ─── Camera ──────────────────────────────────────────────────────────────────
cap = cv2.VideoCapture(0)
if not cap.isOpened():
    print("❌ Could not open camera. Check permissions or try index 1.")
    sys.exit(1)

cap.set(cv2.CAP_PROP_FRAME_WIDTH,  1280)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

# ─── Roast bank ───────────────────────────────────────────────────────────────
roast_bank = {
    "sleep": [
        "Bro is sleeping like exams are optional",
        "Wake up! Reality is calling you",
        "Are you dreaming about being productive?",
        "Eyes open, brain offline. Reboot yourself!",
        "This is a hackathon, not a slumber party!",
        "ZZZ mode activated. Your teammates are judging you.",
    ],
    "away": [
        "Looking everywhere except at success",
        "Did something in the corner steal your GPA?",
        "The screen is right here bro, focus up!",
        "Your eyes are on vacation while your deadline isn't",
        "Wall more interesting than winning? Really?",
        "Looking away won't make the bugs fix themselves!",
    ],
    "noface": [
        "Bro disappeared like motivation on a Monday",
        "Invisible mode activated. Ghost protocol engaged.",
        "Where did you go? The code won't write itself!",
        "Running from responsibilities again?",
        "Bro really said I'm out and left the frame",
        "Come back! Your project misses you... kind of.",
    ],
    "normal": [
        "Your focus just rage quit",
        "Error 404: Focus not found",
        "Your attention span called — it wants a divorce",
        "Brain buffering... please wait",
        "Is that a distraction? Yes. Yes it is.",
        "Certified distracted dev moment right there",
    ],
}
recent_roasts: list[str] = []

EMOJI_MAP = {
    "sleep":  "😴",
    "away":   "👀",
    "noface": "👻",
    "normal": "💀",
}

def generate_roast(category: str) -> tuple[str, str]:
    options = roast_bank.get(category, roast_bank["normal"])
    available = [r for r in options if r not in recent_roasts]
    if not available:
        available = options
    roast = random.choice(available)
    recent_roasts.append(roast)
    if len(recent_roasts) > 8:
        recent_roasts.pop(0)
    emoji = EMOJI_MAP.get(category, "💀")
    return roast, emoji

# ─── State ────────────────────────────────────────────────────────────────────
focus_score    = 5
last_update    = 0.0
roast_cooldown = 4.5
display_text   = "Starting up..."
display_emoji  = "🚀"
color          = (0, 255, 0)

distractions   = 0
focused_frames = 0
start_time     = time.time()
frame_count    = 0
total_score    = 0.0
last_behavior  = "Initializing..."
last_category  = "normal"
last_faces     = []

# Live stats JSON file (for web dashboard to read)
STATS_FILE = os.path.join(os.path.dirname(__file__), "focus_stats.json")

def write_stats(behavior, score, distractions, focused, elapsed, roast, emoji):
    data = {
        "behavior":    behavior,
        "score":       score,
        "distractions": distractions,
        "focused":     focused,
        "elapsed":     elapsed,
        "roast":       roast,
        "emoji":       emoji,
        "ts":          time.time(),
    }
    try:
        with open(STATS_FILE, "w") as f:
            json.dump(data, f)
    except Exception:
        pass

# ─── Text helpers ─────────────────────────────────────────────────────────────
FONT       = cv2.FONT_HERSHEY_DUPLEX
FONT_LARGE = 1.1
FONT_MED   = 0.85
FONT_SMALL = 0.65
THICK_FAT  = 2
THICK_NORM = 1

def put_text_shadow(img, text, pos, scale, color, thickness=2):
    x, y = pos
    cv2.putText(img, text, (x+2, y+2), FONT, scale, (0,0,0),   thickness+1, cv2.LINE_AA)
    cv2.putText(img, text, (x, y),     FONT, scale, color,      thickness,   cv2.LINE_AA)

# ─── Window ───────────────────────────────────────────────────────────────────
WIN_NAME = "Focus Guard "
cv2.namedWindow(WIN_NAME, cv2.WINDOW_NORMAL)
cv2.setWindowProperty(WIN_NAME, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)

print("\n🚀 Focus Guard is LIVE! Press Q or Esc to quit.\n")
speak("Focus Guard activated. . Let's see how long you last.")

# ─── Main loop ────────────────────────────────────────────────────────────────
while True:
    ret, frame = cap.read()
    if not ret:
        print("⚠️  Frame grab failed — camera disconnected?")
        break

    h, w = frame.shape[:2]
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    if frame_count % 2 == 0:
        last_faces = face_cascade.detectMultiScale(
            gray, scaleFactor=1.1, minNeighbors=5, minSize=(80, 80)
        )

    frame_count += 1
    faces = last_faces

    behavior = "No Face 👻"
    category = "noface"

    if len(faces) > 0:
        x, y, face_w, face_h = max(faces, key=lambda f: f[2] * f[3])

        # Neon green face box
        cv2.rectangle(frame, (x, y), (x+face_w, y+face_h), (0, 255, 80), 2)
        # Corner accents
        corner_len = 20
        for cx, cy, dx, dy in [(x,y,-1,-1),(x+face_w,y,1,-1),(x,y+face_h,-1,1),(x+face_w,y+face_h,1,1)]:
            cv2.line(frame, (cx, cy), (cx - dx*corner_len, cy), (0,255,180), 3)
            cv2.line(frame, (cx, cy), (cx, cy - dy*corner_len), (0,255,180), 3)

        face_center  = x + face_w // 2
        frame_center = w // 2
        off_center   = abs(face_center - frame_center)
        threshold    = w // 6

        if off_center > threshold:
            behavior = "Looking Away 👀"
            category = "away"
            focus_score -= 2
            distractions += 1
        else:
            roi_gray = gray[y: y+face_h, x: x+face_w]
            eyes = eye_cascade.detectMultiScale(
                roi_gray, scaleFactor=1.1, minNeighbors=6, minSize=(20, 20)
            )
            if len(eyes) < 1:
                behavior = "Drowsy 😴"
                category = "sleep"
                focus_score -= 3
                distractions += 1
            else:
                behavior = "Focused 👍"
                category = "normal"
                focus_score += 2
                focused_frames += 1
                for (ex, ey, ew, eh) in eyes[:2]:
                    cv2.rectangle(frame,
                                  (x+ex, y+ey), (x+ex+ew, y+ey+eh),
                                  (255, 220, 0), 1)
    else:
        focus_score -= 3
        distractions += 1

    focus_score  = max(0, min(focus_score, 10))
    total_score += focus_score
    last_behavior = behavior
    last_category = category

    current_time = time.time()
    elapsed = int(current_time - start_time)

    # ── Roast logic: fire every N seconds and SPEAK each new roast ──
    if current_time - last_update > roast_cooldown:
        if focus_score >= 7:
            display_text  = "BEAST MODE ACTIVATED"
            display_emoji = "🔥"
            color         = (0, 255, 80)
            speak("Nice! You are actually focused. ")
        elif focus_score >= 5:
            display_text  = "Holding it together... barely"
            display_emoji = "😬"
            color         = (0, 200, 220)
            speak("Okay. You are kind of focused. Keep it up, maybe.")
        else:
            roast_text, roast_emoji = generate_roast(category)
            display_text  = roast_text
            display_emoji = roast_emoji
            color         = (30, 80, 255)  # red-ish BGR
            speak(roast_text)             # 🔊 Each new roast is spoken!
        last_update = current_time

    # Write live stats for web dashboard
    write_stats(behavior, focus_score, distractions, focused_frames,
                elapsed, display_text, display_emoji)

    # ── HUD overlay ───────────────────────────────────────────────────────
    # Semi-transparent dark top bar
    overlay = frame.copy()
    cv2.rectangle(overlay, (0, 0), (w, 110), (10, 10, 20), -1)
    cv2.addWeighted(overlay, 0.65, frame, 0.35, 0, frame)

    # Gradient-like side accent line
    cv2.line(frame, (0, 0), (0, h), (0, 255, 80), 4)

    # Roast text
    put_text_shadow(frame, display_text[:55], (20, 50), FONT_LARGE, color, THICK_FAT)
    put_text_shadow(frame, behavior,         (20, 90), FONT_MED,   (255, 230, 60), THICK_NORM)

    # Focus score bar
    bar_x, bar_y = 20, h - 55
    bar_w, bar_h = 300, 24
    fill      = int((focus_score / 10) * bar_w)
    bar_color = (0, 220, 90) if focus_score >= 6 else (30, 80, 255)
    cv2.rectangle(frame, (bar_x, bar_y), (bar_x+bar_w, bar_y+bar_h), (40,40,40), -1)
    cv2.rectangle(frame, (bar_x, bar_y), (bar_x+fill,  bar_y+bar_h), bar_color, -1)
    cv2.rectangle(frame, (bar_x, bar_y), (bar_x+bar_w, bar_y+bar_h), (120,120,120), 1)
    put_text_shadow(frame, f"Focus  {focus_score}/10",
                    (bar_x+bar_w+14, bar_y+17), FONT_SMALL, (220,220,220), THICK_NORM)

    # Stats panel
    mins, secs = divmod(elapsed, 60)
    stats_x = w - 290
    cv2.rectangle(frame, (stats_x-10, h-100), (w-5, h-5), (10,10,20), -1)
    put_text_shadow(frame, f"Session : {mins:02d}:{secs:02d}",
                    (stats_x, h-78), FONT_SMALL, (200,200,200), THICK_NORM)
    put_text_shadow(frame, f"Distractions : {distractions}",
                    (stats_x, h-52), FONT_SMALL, (200,200,200), THICK_NORM)
    put_text_shadow(frame, f"Focused frames : {focused_frames}",
                    (stats_x, h-26), FONT_SMALL, (200,200,200), THICK_NORM)

    # Quit hint
    put_text_shadow(frame, "Q / Esc  to quit",
                    (w//2 - 80, h-15), FONT_SMALL, (140,140,140), THICK_NORM)

    cv2.imshow(WIN_NAME, frame)

    key = cv2.waitKey(10) & 0xFF
    if key == ord('q') or key == 27:
        break

# ─── Cleanup ──────────────────────────────────────────────────────────────────
cap.release()
cv2.destroyAllWindows()

session_secs = int(time.time() - start_time)
avg_focus    = total_score / frame_count if frame_count > 0 else 0.0
mins, secs   = divmod(session_secs, 60)

print("\n" + "=" * 50)
print("   🏆  FOCUS GUARD — HACKATHON SESSION REPORT")
print("=" * 50)
print(f"  Session length   : {mins:02d}m {secs:02d}s")
print(f"  Total frames     : {frame_count}")
print(f"  Focused frames   : {focused_frames}")
print(f"  Distractions     : {distractions}")
print(f"  Avg focus score  : {avg_focus:.2f} / 10")
print("-" * 50)
if distractions > focused_frames:
    verdict = "Bro was distracted more than focused 💀"
elif avg_focus >= 7:
    verdict = "Beast mode. Actual focus achieved 🔥"
else:
    verdict = "Not bad — you survived the roast 😎"
print(f"  Verdict : {verdict}")
print("=" * 50 + "\n")
speak(f"Session over. {verdict.replace('💀','').replace('🔥','').replace('😎','')}")