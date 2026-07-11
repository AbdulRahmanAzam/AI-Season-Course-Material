# LESSON 1: Basic API Call
# Digital Ocean Serverless Inference is OpenAI-compatible.
# We use the official OpenAI Python SDK — just swap the base URL.

import os # operating system
import sys
from openai import OpenAI
from dotenv import load_dotenv

sys.stdout.reconfigure(encoding="utf-8")

load_dotenv()

client = OpenAI(
    api_key=os.getenv("DO_API_KEY"),  # environment variable 
    base_url=os.getenv("DO_BASE_URL"),
)

response = client.chat.completions.create( 
    model= "openai-gpt-oss-120b", #os.getenv("MODEL"),
    messages=[
        {
            "role": "user",
            "content": "What is 2 + 2? Answer in one sentence.",
        }
    ],
)

print("Row response:", response, "\n\n---\n\n")  # raw response object


# Response is nested — dig to get the text
text = response.choices[0].message.content
print("Model replied:", text)


# # Always track token usage in production
print("\nToken usage:", response.usage)

