# LESSON 2: Streaming
# Without streaming: wait for full response, then print.
# With streaming:    tokens arrive and print one-by-one (feels instant to user).

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

print("--- WITHOUT STREAMING ---")
full = client.chat.completions.create(
    model=os.getenv("MODEL"),
    messages=[{"role": "user", "content": "Count from 1 to 20, one per line."}],
)
print(full.choices[0].message.content)




print("\n--- WITH STREAMING ---")
stream = client.chat.completions.create(
    model=os.getenv("MODEL"),
    messages=[{"role": "user", "content": "Count from 1 to 20, one per line."}],
    stream=True,  # <-- only change needed
)

for chunk in stream:
    if not chunk.choices:
        continue
    delta = chunk.choices[0].delta.content or ""
    print(delta, end="", flush=True)  # print each token as it arrives

print("\n\n[stream ended]")
