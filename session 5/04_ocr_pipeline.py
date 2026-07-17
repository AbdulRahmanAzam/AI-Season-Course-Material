"""
FILE 4: OCR Pipeline — CLASSIC (Tesseract) + LLM
=================================================
OCR = Optical Character Recognition = reading TEXT from images.

This is the CLASSIC pipeline: two separate tools, each with one job.

    image     --(Tesseract OCR engine)-->  raw text   (dumb: just characters)
    raw text  --(LLM)-->                    clean JSON  (smart: understands it)

Compare with the DIRECT way (a VLM like Gemini reads the image itself).
Here Tesseract does the READING, the LLM does the THINKING.
The LLM never sees the picture — only the text Tesseract produced.

Old OCR tools (Tesseract) only give raw, often-messy text.
The LLM then cleans it up and pulls out shop name, total, items, etc.

SETUP: pip install pytesseract  AND install the Tesseract engine itself:
  Windows: https://github.com/UB-Mannheim/tesseract/wiki  (get the installer)
  Mac:     brew install tesseract
  Linux:   sudo apt install tesseract-ocr
"""

import os
import json
import platform
from dotenv import load_dotenv
from google import genai
from google.genai import types
from PIL import Image
import pytesseract

# On Windows, Tesseract is NOT on the PATH by default, so point to the .exe.
# (Change this path if you installed it somewhere else.)
if platform.system() == "Windows":
    win_path = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
    if os.path.exists(win_path):
        pytesseract.pytesseract.tesseract_cmd = win_path

load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

MODEL = "gemini-3.1-flash-lite"

image = Image.open("receipt.jpg")


# ---------- STEP 1: Classic OCR engine reads the text ----------
print("=" * 50)
print("STEP 1: Tesseract OCR -> raw text")
print("=" * 50)

raw_text = pytesseract.image_to_string(image)
print(raw_text)


# ---------- STEP 2: LLM turns the messy text into clean JSON ----------
print("=" * 50)
print("STEP 2: LLM structures the text -> JSON  (no image, text only!)")
print("=" * 50)

prompt = f"""Here is raw OCR text from a receipt (it may be messy or misread):

{raw_text}

Extract a JSON object with these keys:
  shop_name  (string)
  date       (string)
  items      (list of {{name, price}})
  total      (number)
"""

response = client.models.generate_content(
    model=MODEL,
    contents=[prompt],   # <- TEXT ONLY. The LLM never sees the picture.
    config=types.GenerateContentConfig(response_mime_type="application/json"),
)

data = json.loads(response.text)      # now it is a real Python dictionary!
print(json.dumps(data, indent=2))


# ---------- STEP 3: Use + save the result ----------
print("=" * 50)
print("STEP 3: Save the result")
print("=" * 50)

print("Shop:", data.get("shop_name"))
print("Total:", data.get("total"))
print("Number of items:", len(data.get("items", [])))

with open("receipt_output.json", "w") as f:
    json.dump(data, f, indent=2)

print("Saved to receipt_output.json  <- other programs can now use this data!")
