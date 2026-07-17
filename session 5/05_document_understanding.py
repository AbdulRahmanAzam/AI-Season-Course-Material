"""
FILE 5: Document Understanding (complete PDF)
==============================================
OCR only reads text. Document understanding reads the WHOLE document:
  - tables
  - charts and images
  - headers and footers
  - sections and structure

We send the full PDF directly to the model - no page splitting,
no manual parsing. The model looks at every page like a human.
"""

import os
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

MODEL = "gemini-2.5-flash"

# 1. Read the PDF file as bytes
with open("sample.pdf", "rb") as f:
    pdf_bytes = f.read()

# 2. Wrap it into a Part so the model knows it is a PDF
pdf_part = types.Part.from_bytes(data=pdf_bytes, mime_type="application/pdf")


# small helper: ask one question about the PDF
def ask_pdf(question):
    response = client.models.generate_content(
        model=MODEL,
        contents=[pdf_part, question],
    )
    return response.text 


# ---------- DEMO 1: Summary of the whole document ----------
print("=" * 50)
print("DEMO 1: Summarize the document")
print("=" * 50)
print(ask_pdf("Summarize this document in 3 simple sentences."))


# ---------- DEMO 2: Extract TABLES ----------
print("=" * 50)
print("DEMO 2: Extract all tables")
print("=" * 50)
print(ask_pdf("Extract every table in this document as a markdown table."))


# ---------- DEMO 3: Understand CHARTS ----------
print("=" * 50)
print("DEMO 3: Understand the charts")
print("=" * 50)
print(ask_pdf("Describe the charts in this document. Which quarter was the best and worst?"))


# ---------- DEMO 4: Headers, footers and structure ----------
print("=" * 50)
print("DEMO 4: Document structure")
print("=" * 50)
print(ask_pdf("""Describe the structure of this document:
- What is written in the header of the pages?
- What is written in the footer of the pages?
- How many pages, tables and charts does it have?"""))
