"""
FILE 1: Groq -- Custom (raw HTTP) vs Usual (SDK)
==================================================
Two ways to ask Groq the same question. Both hit the EXACT same endpoint:
    https://api.groq.com/openai/v1/chat/completions
The SDK below is just a thin wrapper around that raw HTTP call -- it builds
the same JSON body and reads the same JSON reply for you.
"""

import os
import requests
from dotenv import load_dotenv
from groq import Groq

load_dotenv()
API_KEY = os.getenv("GROQ_API_KEY")
MODEL = "llama-3.3-70b-versatile"
QUESTION = "What is Groq famous for? Answer in one sentence."


# ---------- CUSTOM: raw HTTP request, no SDK ----------
print("=" * 50)
print("CUSTOM: raw requests.post()")
print("=" * 50)

response = requests.post(
    "https://api.groq.com/openai/v1/chat/completions",
    headers={
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json",
    },
    json={
        "model": MODEL,
        "messages": [{"role": "user", "content": QUESTION}],
    },
)
data = response.json()
print(data["choices"][0]["message"]["content"])


# ---------- USUAL: official Groq SDK ----------
print("=" * 50)
print("USUAL: groq.Groq() SDK")
print("=" * 50)

client = Groq(api_key=API_KEY)
completion = client.chat.completions.create(
    model=MODEL,
    messages=[{"role": "user", "content": QUESTION}],
)
print(completion.choices[0].message.content)


# NOTE:
# - Same URL, same JSON, same answer. The SDK just saves you from writing
#   headers / json= / response.json()["choices"][0]... by hand every time.
# - .env key used here: GROQ_API_KEY
