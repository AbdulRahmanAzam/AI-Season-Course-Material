"""
FILE 2: Audio Pipeline — CLASSIC (signal processing + offline speech) + LLM
===========================================================================
The DIRECT way (native audio models) is to hand the raw sound to the model
and let it HEAR everything at once. Here we do the OLD-SCHOOL way instead:
classic Python libraries pull real VALUES out of the sound first, and only
those values are handed to the LLM.

    audio  --(wave + numpy)--------->  numbers  (duration, loudness, silence...)
    audio  --(CMU Sphinx, offline)-->  text     (a rough transcript)
    numbers + text  --(LLM)-->         answer    (what is it? what is the mood?)

The LLM never hears a single sound wave. It only reads the measurements and
the transcript that the classic libraries produced. Two dumb tools do the
"sensing", one smart model does the "thinking".

  - `wave`  is Python's built-in library for reading .wav files (no install).
  - `numpy` does the math on the raw samples (loudness, silence, energy...).
  - CMU Sphinx (via SpeechRecognition) is a CLASSIC, fully offline speech
    engine from the pre-deep-learning era. It is not very accurate, which is
    exactly the point: old engines give messy text, the LLM cleans it up.

SETUP (Sphinx step is optional — the file still runs without it):
    pip install SpeechRecognition pocketsphinx
Compare with FILE 8, which uses a modern STT model (Whisper) for the same job.
"""

import os
import wave
import json
import numpy as np
from dotenv import load_dotenv
from google import genai

load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

MODEL = "gemini-3.1-flash-lite"      # a TEXT model is enough now — no audio in

AUDIO_FILE = "sample_audio.wav"


# ---------- STEP 1: wave + numpy measure the sound -> numbers ----------
print("=" * 50)
print("STEP 1: wave + numpy -> signal measurements (no AI here)")
print("=" * 50)

# 1a. Read the WAV header + raw samples with the built-in `wave` library.
with wave.open(AUDIO_FILE, "rb") as wf:
    channels = wf.getnchannels()        # 1 = mono, 2 = stereo
    samp_width = wf.getsampwidth()      # bytes per sample (2 = 16-bit audio)
    sample_rate = wf.getframerate()     # samples per second (e.g. 22050)
    n_frames = wf.getnframes()          # total samples
    raw_bytes = wf.readframes(n_frames)

duration = n_frames / float(sample_rate)

# 1b. Turn the raw bytes into a numpy array of numbers we can do math on.
dtype = {1: np.uint8, 2: np.int16, 4: np.int32}.get(samp_width, np.int16)
samples = np.frombuffer(raw_bytes, dtype=dtype).astype(np.float32)

if channels > 1:                        # mix stereo down to a single mono track
    samples = samples.reshape(-1, channels).mean(axis=1)

# Scale samples to the range -1.0 .. 1.0 so loudness is easy to read.
if dtype == np.uint8:                   # 8-bit audio is unsigned (0..255)
    samples = (samples - 128) / 128.0
else:
    samples = samples / float(2 ** (8 * samp_width - 1))

# 1c. Compute simple, classic features from the samples.
loudness = float(np.sqrt(np.mean(samples ** 2)))          # RMS energy, 0..1
peak = float(np.max(np.abs(samples)))                     # loudest single point
silence_ratio = float(np.mean(np.abs(samples) < 0.02))    # fraction that is quiet

# Energy over time: split into 10 chunks, measure loudness of each (0..100).
chunks = np.array_split(samples, 10)
energy_over_time = [int(np.sqrt(np.mean(c ** 2)) * 100) for c in chunks if c.size]

measurements = {
    "duration_seconds": round(duration, 1),
    "sample_rate_hz": sample_rate,
    "channels": channels,
    "loudness_0_to_100": int(loudness * 100),
    "peak_0_to_100": int(peak * 100),
    "silence_percent": int(silence_ratio * 100),
    "energy_over_time": energy_over_time,
}
print(json.dumps(measurements, indent=2))


# ---------- STEP 2: classic offline speech engine -> rough transcript ----------
print("=" * 50)
print("STEP 2: CMU Sphinx (offline, classic) -> transcript")
print("=" * 50)

transcript = ""
try:
    import speech_recognition as sr

    recognizer = sr.Recognizer()
    with sr.AudioFile(AUDIO_FILE) as source:
        audio_data = recognizer.record(source)          # read whole file
    transcript = recognizer.recognize_sphinx(audio_data)  # 100% offline
    print(transcript)
except Exception as e:
    # No Sphinx installed, or it failed — that's fine, we keep going with
    # just the numbers from STEP 1. (Install: pip install SpeechRecognition pocketsphinx)
    print(f"(Sphinx not available: {e})")
    print("Skipping transcript — the LLM will work from the measurements only.")


# ---------- STEP 3: LLM reads the extracted values and answers ----------
print("=" * 50)
print("STEP 3: LLM interprets the values (it never hears the audio)")
print("=" * 50)

prompt = f"""You are given ONLY classic audio measurements and a rough,
possibly-wrong offline transcript of an audio clip. You cannot hear the audio.

Signal measurements:
{json.dumps(measurements, indent=2)}

Rough offline transcript (may contain mistakes, may be empty):
"{transcript}"

Based only on this, answer in 2 short lines:
1) What is this audio probably about?
2) What is the likely mood / energy of the speaker?
"""

response = client.models.generate_content(
    model=MODEL,
    contents=[prompt],       # <- TEXT ONLY. The LLM never receives the sound.
)
print(response.text)


# NOTE:
# - STEP 1 (wave + numpy) always runs and needs no internet and no install.
# - STEP 2 (Sphinx) is a classic offline engine: dumb but private and free.
# - Compare FILE 8: same idea, but a modern Whisper model does the hearing.
#   Compare the old direct way: the model ate the raw audio and heard it all.
