"""
STEP 0: Create sample files for the session.

Run this file ONE TIME before the session:
    python 00_create_samples.py

It creates:
    sample.jpg        -> a day scene image   (used in 01_vlm.py)
    sample2.jpg       -> a night scene image (used in 01_vlm.py)
    sample_audio.wav  -> a spoken voice file (used in 02_audio_lm.py)
    sample_video.mp4  -> a 3-scene clip      (used in 03_video_understanding.py)
    receipt.jpg       -> a fake shop receipt (used in 04_ocr_pipeline.py)
    sample.pdf        -> a 2-page report with table + chart (used in 05_document_understanding.py)
    images/           -> 4 small images      (used in 06_multimodal_rag.py)

You do NOT need to teach this file. It only creates demo data.
You can also replace these files with your own real photos / audio / PDFs.
"""

import os
import sys
import wave
import subprocess
import numpy as np
from PIL import Image, ImageDraw, ImageFont


def get_font(size):
    """Try to load a nice font, otherwise use the default one."""
    try:
        return ImageFont.truetype("arial.ttf", size)
    except OSError:
        return ImageFont.load_default()


def get_mono_font(size):
    """Monospace font for the receipt (so columns line up)."""
    try:
        return ImageFont.truetype("cour.ttf", size)
    except OSError:
        return get_font(size)


# ---------- 1. Day scene (for VLM demo) ----------
def make_day_scene(path):
    img = Image.new("RGB", (800, 600), "skyblue")
    d = ImageDraw.Draw(img)
    d.rectangle([0, 400, 800, 600], fill="green")            # grass
    d.ellipse([600, 50, 720, 170], fill="yellow")            # sun
    d.rectangle([150, 250, 400, 450], fill="red")            # house
    d.polygon([(130, 250), (275, 150), (420, 250)], fill="brown")  # roof
    d.rectangle([250, 350, 310, 450], fill="saddlebrown")    # door
    d.text((150, 500), "MY SWEET HOME", fill="white", font=get_font(40))
    img.save(path)


# ---------- 2. Night scene (for VLM compare demo) ----------
def make_night_scene(path):
    img = Image.new("RGB", (800, 600), "midnightblue")
    d = ImageDraw.Draw(img)
    d.rectangle([0, 400, 800, 600], fill="darkgreen")        # grass
    d.ellipse([600, 50, 700, 150], fill="lightyellow")       # moon
    for x, y in [(100, 80), (250, 120), (400, 60), (500, 150)]:
        d.ellipse([x, y, x + 8, y + 8], fill="white")        # stars
    d.rectangle([150, 250, 400, 450], fill="darkred")        # house
    d.polygon([(130, 250), (275, 150), (420, 250)], fill="black")  # roof
    d.rectangle([250, 350, 310, 450], fill="black")          # door
    img.save(path)


# ---------- 3. Receipt image (for OCR demo) ----------
def make_receipt(path):
    img = Image.new("RGB", (500, 620), "white")
    d = ImageDraw.Draw(img)
    font = get_mono_font(28)
    lines = [
        "       MEGA MART",
        "    Karachi, Pakistan",
        "    Receipt No: 1234",
        "------------------------",
        "Milk           Rs 350",
        "Bread          Rs 200",
        "Eggs (12)      Rs 425",
        "Rice 1kg       Rs 300",
        "------------------------",
        "TOTAL          Rs 1275",
        "",
        "Date: 10-07-2026",
        "  Thank you! Visit again",
    ]
    y = 30
    for line in lines:
        d.text((30, y), line, fill="black", font=font)
        y += 44
    img.save(path)


# ---------- 4. A 2-page PDF report (for document understanding demo) ----------
def make_report_page_1():
    img = Image.new("RGB", (1000, 1400), "white")
    d = ImageDraw.Draw(img)
    big, mid, small = get_font(46), get_font(32), get_font(24)

    # header
    d.rectangle([0, 0, 1000, 70], fill="navy")
    d.text((30, 15), "ACME CORP - Annual Report 2026", fill="white", font=mid)

    # title + paragraph
    d.text((30, 120), "Sales Performance Report", fill="black", font=big)
    d.text((30, 210), "This report shows the sales of ACME Corp for the year.", fill="black", font=small)
    d.text((30, 245), "Sales grew strongly in the last quarter of the year.", fill="black", font=small)

    # a simple table
    d.text((30, 330), "Table 1: Sales by Quarter", fill="black", font=mid)
    rows = [
        ["Quarter", "Sales (in $1000)", "Growth"],
        ["Q1", "100", "-"],
        ["Q2", "150", "+50%"],
        ["Q3", "120", "-20%"],
        ["Q4", "200", "+67%"],
    ]
    y = 400
    for row in rows:
        for c, cell in enumerate(row):
            x = 30 + c * 300
            d.rectangle([x, y, x + 300, y + 60], outline="black", width=2)
            d.text((x + 15, y + 15), cell, fill="black", font=small)
        y += 60

    # a simple bar chart
    d.text((30, 780), "Chart 1: Sales by Quarter (bar chart)", fill="black", font=mid)
    values = [("Q1", 100), ("Q2", 150), ("Q3", 120), ("Q4", 200)]
    base_y = 1200
    for i, (label, v) in enumerate(values):
        x = 100 + i * 200
        d.rectangle([x, base_y - v * 2, x + 100, base_y], fill="steelblue")
        d.text((x + 30, base_y + 10), label, fill="black", font=small)
        d.text((x + 25, base_y - v * 2 - 35), str(v), fill="black", font=small)

    # footer
    d.text((30, 1340), "Page 1 | Confidential | www.acme.example.com", fill="gray", font=small)
    return img


def make_report_page_2():
    img = Image.new("RGB", (1000, 1400), "white")
    d = ImageDraw.Draw(img)
    mid, small = get_font(32), get_font(24)

    d.rectangle([0, 0, 1000, 70], fill="navy")
    d.text((30, 15), "ACME CORP - Annual Report 2026", fill="white", font=mid)

    d.text((30, 130), "Conclusion", fill="black", font=mid)
    d.text((30, 200), "Q4 was the best quarter with sales of 200 thousand dollars.", fill="black", font=small)
    d.text((30, 240), "Next year the company plans to open 5 new stores.", fill="black", font=small)

    d.text((30, 1340), "Page 2 | Confidential | www.acme.example.com", fill="gray", font=small)
    return img


def make_pdf(path):
    page1 = make_report_page_1()
    page2 = make_report_page_2()
    page1.save(path, save_all=True, append_images=[page2])


# ---------- 5. Small images for multimodal RAG ----------
def make_shape(path, shape, color, bg="white"):
    img = Image.new("RGB", (400, 400), bg)
    d = ImageDraw.Draw(img)
    if shape == "circle":
        d.ellipse([100, 100, 300, 300], fill=color)
    elif shape == "square":
        d.rectangle([100, 100, 300, 300], fill=color)
    elif shape == "triangle":
        d.polygon([(200, 100), (100, 300), (300, 300)], fill=color)
    img.save(path)


# ---------- 6. Audio file with a spoken sentence ----------
def make_audio(path):
    """Use Windows text-to-speech to create a real spoken audio file.
    If that fails (e.g. not on Windows), create a simple beep sound instead."""
    text = ("Hello students, welcome to the multimodal agents session. "
            "Today we will learn how AI models can see images, "
            "hear audio, and watch videos.")
    try:
        if sys.platform != "win32":
            raise RuntimeError("not windows")
        abs_path = os.path.abspath(path)
        ps = (
            "Add-Type -AssemblyName System.Speech; "
            "$s = New-Object System.Speech.Synthesis.SpeechSynthesizer; "
            f"$s.SetOutputToWaveFile('{abs_path}'); "
            f"$s.Speak('{text}'); "
            "$s.Dispose()"
        )
        subprocess.run(["powershell", "-NoProfile", "-Command", ps], check=True)
    except Exception:
        # fallback: 2 seconds of a simple beep tone
        sr = 16000
        t = np.linspace(0, 2, sr * 2)
        tone = (np.sin(2 * np.pi * 440 * t) * 0.5 * 32767).astype(np.int16)
        with wave.open(path, "w") as f:
            f.setnchannels(1)
            f.setsampwidth(2)
            f.setframerate(sr)
            f.writeframes(tone.tobytes())


# ---------- 7. A short video with 3 clear scenes (for OpenCV video demo) ----------
def make_video(path):
    """Write a tiny 3-scene .mp4 so 03_video_understanding.py has a local file.
    Needs OpenCV. If it is missing, we just skip (that demo won't run)."""
    try:
        import cv2
    except ImportError:
        print("  (skipping sample_video.mp4 - run: pip install opencv-python)")
        return

    w, h, fps = 480, 360, 20
    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    writer = cv2.VideoWriter(path, fourcc, fps, (w, h))
    if not writer.isOpened():                     # some builds lack mp4 -> use .avi
        path = os.path.splitext(path)[0] + ".avi"
        writer = cv2.VideoWriter(path, cv2.VideoWriter_fourcc(*"MJPG"), fps, (w, h))

    font = cv2.FONT_HERSHEY_SIMPLEX
    secs = 1.5                                     # each scene lasts 1.5 seconds

    # Scene 1: a still RED screen.
    for _ in range(int(fps * secs)):
        frame = np.full((h, w, 3), (0, 0, 200), dtype=np.uint8)   # BGR red
        cv2.putText(frame, "SCENE 1: RED", (90, h // 2), font, 1.2, (255, 255, 255), 3)
        writer.write(frame)

    # Scene 2: a BLUE screen with a white ball moving left -> right (lots of motion).
    n = int(fps * secs)
    for i in range(n):
        frame = np.full((h, w, 3), (200, 0, 0), dtype=np.uint8)   # BGR blue
        x = int(40 + (w - 80) * i / n)
        cv2.circle(frame, (x, h // 2), 30, (255, 255, 255), -1)   # moving ball
        cv2.putText(frame, "SCENE 2: MOVING BALL", (40, 40), font, 0.8, (255, 255, 255), 2)
        writer.write(frame)

    # Scene 3: a GREEN screen with a growing yellow square.
    for i in range(n):
        frame = np.full((h, w, 3), (0, 150, 0), dtype=np.uint8)   # BGR green
        s = int(20 + 120 * i / n)
        cv2.rectangle(frame, (w // 2 - s, h // 2 - s), (w // 2 + s, h // 2 + s),
                      (0, 255, 255), -1)                          # yellow square
        cv2.putText(frame, "SCENE 3: GREEN", (100, 40), font, 0.9, (255, 255, 255), 2)
        writer.write(frame)

    writer.release()


if __name__ == "__main__":
    make_day_scene("sample.jpg")
    make_night_scene("sample2.jpg")
    make_receipt("receipt.jpg")
    make_pdf("sample.pdf")

    os.makedirs("images", exist_ok=True)
    make_shape("images/red_circle.jpg", "circle", "red")
    make_shape("images/blue_square.jpg", "square", "blue")
    make_shape("images/green_triangle.jpg", "triangle", "green")
    make_receipt("images/shop_receipt.jpg")

    make_audio("sample_audio.wav")
    make_video("sample_video.mp4")

    print("All sample files created!")
    print("  sample.jpg, sample2.jpg, receipt.jpg, sample.pdf, sample_audio.wav, sample_video.mp4, images/")
    print("Tip: you can replace any of them with your own real files.")
