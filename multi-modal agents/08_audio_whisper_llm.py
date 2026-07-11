"""
FILE 8: Audio -> Whisper -> LLM  (the CLASSIC two-step pipeline)
================================================================
FILE 2 already splits audio into two steps using a CLASSIC offline engine
(CMU Sphinx) — dumb, but free and private. Here we keep the SAME two steps,
but STEP 1 uses a MODERN speech model (Whisper) that is far more accurate:

    STEP 1:  audio  --(Whisper STT model)-->  text
    STEP 2:  text   --(LLM)-->                 answer

Same final result, but now you can SEE the text in the middle.
This is how most real apps worked before native audio models existed,
and it is still very common today.

We use Groq because it runs BOTH models (Whisper + Llama) and is very fast.
The big idea to teach: the LLM never hears sound. It only reads the
text that Whisper produced. Two models, two jobs.
"""

import os
from dotenv import load_dotenv
from groq import Groq

# 1. Load the API key from the .env file
load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

STT_MODEL = "whisper-large-v3"          # the EARS:  speech -> text
LLM_MODEL = "llama-3.3-70b-versatile"   # the BRAIN: text  -> answer

AUDIO_FILE = "sample_audio.wav"


# ---------- STEP 1: Whisper turns speech into text ----------
print("=" * 50)
print("STEP 1: Whisper transcribes the audio -> text")
print("=" * 50)

with open(AUDIO_FILE, "rb") as f:
    transcription = client.audio.transcriptions.create(
        file=(AUDIO_FILE, f.read()),   # (filename, raw bytes)
        model=STT_MODEL,
    )

text = transcription.text
print(text)


# ---------- STEP 2: LLM reads that text and answers ----------
print("=" * 50)
print("STEP 2: LLM understands the text (never hears the audio)")
print("=" * 50)

completion = client.chat.completions.create(
    model=LLM_MODEL,
    messages=[
        {
            "role": "user",
            "content": (
                "Here is a transcript of an audio clip:\n\n"
                f"{text}\n\n"
                "What is it about? What is the mood of the speaker? "
                "Answer in 2 short lines."
            ),
        }
    ],
)
print(completion.choices[0].message.content)


# NOTE:
# - Whisper on Groq accepts .wav .mp3 .m4a .flac ... up to 25 MB.
# - Compare with FILE 2: same two steps, but Sphinx (old, offline, messy).
#   Here Whisper does the hearing far better; the LLM does the thinking.
