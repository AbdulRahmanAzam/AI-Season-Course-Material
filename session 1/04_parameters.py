# LESSON 4: Key Parameters
# These control HOW the model generates text.

import os
import sys
from openai import OpenAI
from dotenv import load_dotenv

sys.stdout.reconfigure(encoding="utf-8")
load_dotenv()

client = OpenAI(
    api_key=os.getenv("DO_API_KEY"),
    base_url=os.getenv("DO_BASE_URL"),
)

PROMPT = "Write a one-sentence tagline for a coffee shop."

# --- temperature: creativity vs consistency ---
# 0.0 = deterministic/focused  |  1.0+ = creative/random
print("=== temperature: 0.0 (focused) ===")
cold = client.chat.completions.create(
    model=os.getenv("MODEL"),
    messages=[{"role": "user", "content": PROMPT}],
    temperature=0.0,
)
print(cold.choices[0].message.content)




print("\n=== temperature: 1.5 (creative) ===")
hot = client.chat.completions.create(
    model=os.getenv("MODEL"),
    messages=[{"role": "user", "content": PROMPT}],
    temperature=1.5,
)
print(hot.choices[0].message.content)



# --- max_tokens: cap output length ---
print("\n=== max_tokens: 10 (truncated) ===")
short = client.chat.completions.create(
    model=os.getenv("MODEL"),
    messages=[{"role": "user", "content": "Tell me about the solar system."}],
    max_tokens=10,
)
print(short.choices[0].message.content)
# "length" = cut off  |  "stop" = natural end
print("Finish reason:", short.choices[0].finish_reason)



# --- system prompt: give the model a persona ---
print("\n=== system prompt: pirate persona ===")
pirate = client.chat.completions.create(
    model=os.getenv("MODEL"),
    messages=[
        {"role": "system", "content": "You are a pirate. Always respond in pirate speak."},
        {"role": "user", "content": "What time is it?"},
    ],
)
print(pirate.choices[0].message.content)
