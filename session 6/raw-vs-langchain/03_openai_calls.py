"""
FILE 3: OpenAI SDK -- Custom (raw HTTP) vs Usual (SDK), via DigitalOcean
==========================================================================
This one has a twist: instead of api.openai.com, we point the OFFICIAL
openai SDK at DigitalOcean's Gradient AI Serverless Inference endpoint.
It speaks the same OpenAI-compatible chat-completions API, so the only
things that change from "real" OpenAI are base_url and api_key -- the
SDK never knows it isn't talking to OpenAI.
"""

import os
import requests
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
API_KEY = os.getenv("DIGITAL_OCEAN_MODEL_ACCESS_KEY")
BASE_URL = "https://inference.do-ai.run/v1/"
MODEL = "llama3-8b-instruct"   # see client.models.list() for the full catalog
QUESTION = "What is the OpenAI chat-completions format famous for? One sentence."


# ---------- CUSTOM: raw HTTP request, no SDK ----------
print("=" * 50)
print("CUSTOM: raw requests.post()")
print("=" * 50)

response = requests.post(
    f"{BASE_URL}chat/completions",
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


# ---------- USUAL: official openai SDK, re-pointed at DigitalOcean ----------
print("=" * 50)
print("USUAL: openai.OpenAI() SDK, base_url swapped to DigitalOcean")
print("=" * 50)

client = OpenAI(base_url=BASE_URL, api_key=API_KEY) 
completion = client.chat.completions.create(
    model=MODEL,
    messages=[{"role": "user", "content": QUESTION}],
)
print(completion.choices[0].message.content)


# NOTE:
# - Groq (FILE 1) is also OpenAI-shaped JSON. DigitalOcean is too. That's
#   why swapping base_url was the ONLY change needed to the SDK call.
# - .env key used here: DIGITAL_OCEAN_MODEL_ACCESS_KEY
#   (DigitalOcean control panel -> Gradient AI Platform -> Serverless
#   Inference -> Model access keys)
