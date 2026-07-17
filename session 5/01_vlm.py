"""
FILE 1: VLM = Vision Language Model
====================================
A VLM is a model that can SEE images and TALK about them.
We send: image + text question  ->  model returns: text answer.

That's it. That is the whole idea of a VLM.
"""

import os
from dotenv import load_dotenv
from google import genai
from PIL import Image

# 1. Load the API key from the .env file
load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

MODEL = "gemini-3.1-flash-lite"

# 2. Open an image from our computer
image = Image.open("sample.jpg")


# ---------- DEMO 1: Describe an image ----------
print("=" * 50)
print("DEMO 1: Describe the image")
print("=" * 50)

response = client.models.generate_content(
    model=MODEL,
    contents=[image, "Describe this image in 2 simple sentences."],
)
print(response.text)


# ---------- DEMO 2: Ask a question about the image ----------
print("=" * 50)
print("DEMO 2: Ask a question about the image")
print("=" * 50)

response = client.models.generate_content(
    model=MODEL,
    contents=[image, "What colors do you see? Is it day or night?"],
)
print(response.text)


# ---------- DEMO 3: Compare TWO images ----------
print("=" * 50)
print("DEMO 3: Compare two images")
print("=" * 50)

image2 = Image.open("sample2.jpg")

response = client.models.generate_content(
    model=MODEL,
    contents=[image, image2, "What is different between these two images?"],
)
print(response.text)
