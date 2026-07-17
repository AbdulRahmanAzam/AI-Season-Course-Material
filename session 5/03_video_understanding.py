"""
FILE 3: Video Pipeline — CLASSIC (OpenCV computer vision) + LLM
===============================================================
The DIRECT way (native video models) is to hand the whole video to the model
and let it WATCH every frame + listen to the audio at once. Here we do the
OLD-SCHOOL way instead: classic computer vision pulls real VALUES out of the
video first, and only those values are handed to the LLM.

    video  --(OpenCV / cv2)-->  numbers per moment  (brightness, colour, motion)
    numbers                 -->  a timeline of EVENTS (scene changes)
    timeline  --(LLM)-->         a plain-English story of the video

The LLM never sees a single pixel. It only reads the timeline of measurements
that OpenCV produced. A "video" is just many images (frames) in a row, so we:
  1. read frames one by one,
  2. measure each sampled frame (how bright? what colour? how much moved?),
  3. mark a "scene change" when things suddenly jump,
  4. let the LLM turn that number-timeline into a description.

SETUP:  pip install opencv-python
Make the sample video first:  python 00_create_samples.py   (creates sample_video.mp4)
Compare with the direct way: a native video model would watch it all itself.
"""

import os
import time
import json
import numpy as np
import cv2                       # OpenCV = the classic computer-vision library
from dotenv import load_dotenv
from google import genai

load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

MODEL = "gemini-3.1-flash-lite"      # a TEXT model is enough now — no video in

VIDEO_FILE = "sample_video.mp4"


def color_name(r, g, b):
    """Turn an average (R, G, B) colour into a rough human word."""
    if max(r, g, b) < 45:
        return "black/dark"
    if min(r, g, b) > 200:
        return "white/bright"
    top = max(r, g, b)
    if r == top and r > g + 25 and r > b + 25:
        return "red"
    if g == top and g > r + 25 and g > b + 25:
        return "green"
    if b == top and b > r + 25 and b > g + 25:
        return "blue"
    if r > 150 and g > 150 and b < 100:
        return "yellow"
    return "mixed/grey"


if not os.path.exists(VIDEO_FILE):
    print(f"No '{VIDEO_FILE}' found. Run:  python 00_create_samples.py")
    raise SystemExit


# ---------- STEP 1: OpenCV reads the video's basic facts ----------
print("=" * 50)
print("STEP 1: OpenCV -> basic video facts (no AI here)")
print("=" * 50)

cap = cv2.VideoCapture(VIDEO_FILE)
fps = cap.get(cv2.CAP_PROP_FPS) or 25
frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
duration = frame_count / fps if fps else 0

facts = {
    "duration_seconds": round(duration, 1),
    "fps": round(fps, 1),
    "total_frames": frame_count,
    "resolution": f"{width}x{height}",
}
print(json.dumps(facts, indent=2))


# ---------- STEP 2: measure sampled frames -> a timeline of events ----------
print("=" * 50)
print("STEP 2: measure frames (brightness, colour, motion) -> timeline")
print("=" * 50)

# We don't need every frame — sample ~12 moments spread across the video.
step = max(1, frame_count // 12)

timeline = []
prev_small = None
frame_idx = 0

while True:
    ok, frame = cap.read()         # frame is a numpy array in BGR colour order
    if not ok:
        break

    if frame_idx % step == 0:
        # Average colour of the whole frame (OpenCV is B, G, R — flip to R, G, B).
        avg_b, avg_g, avg_r = frame.reshape(-1, 3).mean(axis=0)
        brightness = int((avg_r + avg_g + avg_b) / 3 / 255 * 100)   # 0..100

        # Motion = how different this frame is from the previous sampled one.
        small = cv2.cvtColor(cv2.resize(frame, (64, 64)), cv2.COLOR_BGR2GRAY)
        if prev_small is None:
            motion = 0
        else:
            motion = int(np.mean(np.abs(small.astype(int) - prev_small.astype(int)))
                         / 255 * 100)
        prev_small = small

        # A big jump in motion means the scene probably changed (a classic cut).
        event = "scene change" if motion > 15 else "steady"

        timeline.append({
            "time_s": round(frame_idx / fps, 1),
            "color": color_name(int(avg_r), int(avg_g), int(avg_b)),
            "brightness_0_100": brightness,
            "motion_0_100": motion,
            "event": event,
        })

    frame_idx += 1

cap.release()
print(json.dumps(timeline, indent=2))


# ---------- STEP 3: LLM turns the number-timeline into a story ----------
print("=" * 50)
print("STEP 3: LLM describes the video (it never sees a pixel)")
print("=" * 50)

prompt = f"""You are given ONLY computer-vision measurements of a short video.
You cannot see the video itself.

Video facts:
{json.dumps(facts, indent=2)}

Timeline of sampled moments (time, dominant colour, brightness, motion, event):
{json.dumps(timeline, indent=2)}

Based only on these numbers, describe in 3 short lines what likely happens in
this video: how many scenes, their colours, and where the motion/action is.
"""

response = client.models.generate_content(
    model=MODEL,
    contents=[prompt],       # <- TEXT ONLY. The LLM never receives the frames.
)
print(response.text)


# ---------- STEP 4: the DIRECT way — hand the whole video to the model ----------
print("=" * 50)
print("STEP 4: DIRECT — the model WATCHES the video itself (every pixel)")
print("=" * 50)

# No OpenCV, no timeline. We upload the raw video and let the model see every
# frame + hear the audio on its own. Same model, same question as STEP 3 — the
# only change is WHAT we feed it: real footage instead of a table of numbers.
# Video is big, so it goes through Gemini's File API: upload -> wait -> ask.
uploaded = client.files.upload(file=VIDEO_FILE)
while uploaded.state.name == "PROCESSING":      # video takes a moment to ingest
    time.sleep(2)
    uploaded = client.files.get(name=uploaded.name)

direct_response = client.models.generate_content(
    model=MODEL,
    contents=[
        uploaded,                               # <- the ACTUAL video, every pixel
        "Based on this video, describe in 3 short lines what happens: "
        "how many scenes, their colours, and where the motion/action is.",
    ],
)
print(direct_response.text)


# NOTE:
# - CLASSIC (steps 1-3): OpenCV does the "seeing" (colour, brightness, motion,
#   scene cuts); the LLM only reasons over numbers — cheap, fast, explainable.
# - DIRECT (step 4): the model watches the raw video itself — one call, less
#   code, but you cannot SEE why it said what it said (no numbers to inspect).
# - Same model, same question in both; compare the answers to feel the trade-off.
