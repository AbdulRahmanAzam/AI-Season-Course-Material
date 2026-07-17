"""
FILE 2: Gemini -- Custom (raw HTTP) vs Usual (SDK)
====================================================
Same idea as FILE 1, different company. Google's REST shape is different
from Groq/OpenAI's (no "messages" -- it calls them "contents" -> "parts"),
but the pattern is identical: raw HTTP call vs. SDK wrapper around it.
"""

import os
import requests
from dotenv import load_dotenv
from google import genai

load_dotenv()
API_KEY = os.getenv("")
MODEL = "gemini-2.5-flash"
QUESTION = "What is Gemini famous for? Answer in one sentence."


# ---------- CUSTOM: raw HTTP request, no SDK ----------
print("=" * 50)
print("CUSTOM: raw requests.post()")
print("=" * 50)

url = f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL}:generateContent"
response = requests.post(
    url,
    headers={
        "x-goog-api-key": API_KEY,
        "Content-Type": "application/json",
    },
    json={"contents": [{"parts": [{"text": QUESTION}]}]},
)
data = response.json()
print(data["candidates"][0]["content"]["parts"][0]["text"])


# ---------- USUAL: official google-genai SDK ----------
print("=" * 50)
print("USUAL: google.genai.Client() SDK")
print("=" * 50)

client = genai.Client(api_key=API_KEY)
result = client.models.generate_content(model=MODEL, contents=QUESTION)
print(result.text)


# NOTE:
# - Same model, same answer, different JSON shape than Groq/OpenAI.
#   That mismatch is exactly the pain FILE 4 (LangChain) makes disappear.
# - .env key used here: GEMINI_API_KEY (free key: https://aistudio.google.com/apikey)
