# LESSON 3: Multi-turn Chat (Conversation History)
# LLMs are stateless — they forget everything after each call.
# YOU must send the full conversation history every time.

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


def chat(history: list, user_message: str) -> str:
    # Push new user message into history
    history.append({"role": "user", "content": user_message})

    response = client.chat.completions.create(
        model=os.getenv("MODEL"),
        messages=history,  # send FULL history every call
    )

    assistant_message = response.choices[0].message

    # Push assistant reply so next turn remembers it
    history.append({"role": "assistant", "content": assistant_message.content})

    return assistant_message.content


# Simulate a 3-turn conversation
history = [
    {"role": "system", "content": "You are a helpful assistant. Keep answers short."}
]

reply1 = chat(history, "My name is Abdul Rahman.")
print("Turn 1:", reply1)

reply2 = chat(history, "What is the capital of France?")
print("Turn 2:", reply2)

# This proves model remembers earlier context
reply3 = chat(history, "What is my name?")
print("Turn 3:", reply3)

import json
print("\nFull history sent on last call:")
print(json.dumps(history, indent=2))




# role: system, assistant, user


# system -> ai ko particular kaam ke lea assign kar dete ho

# assitant -> ai jo bhi jawab deta he, wo save karleta he

# user -> user ka jo bhi input he, wo save karleta he