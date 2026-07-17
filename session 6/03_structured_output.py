"""
FILE 3: Structured Output
===========================
FILE 4 in Session 5 (OCR pipeline) had to ask the model for JSON text,
then clean it up by hand before it was safe to use.

LangChain can skip that mess. Describe the shape you want with a
Pydantic class, call .with_structured_output(), and you get back a
REAL Python object - not text you have to parse yourself.
"""

import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from pydantic import BaseModel, Field # pydantic is the standard Python library for structured data validation and parsing
# structured data validation 

# frontend -> llm, model, prompt
# llm, model, prompt -> structured output (pydantic)


load_dotenv()
MODEL = "llama-3.3-70b-versatile"
llm = ChatGroq(model=MODEL, temperature=0)   # temperature=0 -> stay precise for data extraction


# ---------- DEMO 1: Ask for a Recipe object ----------
print("=" * 50)
print("DEMO 1: Get a real Python object back")
print("=" * 50)

class Recipe(BaseModel):
    name: str = Field(description="name of the dish")
    ingredients: list[str] = Field(description="short list of ingredients")
    minutes: int = Field(description="time to cook, in minutes")

structured_llm = llm.with_structured_output(Recipe)

result = structured_llm.invoke("Give me a simple recipe for pancakes.")
print(type(result), "\n\n")          # <- Recipe, not str!
print(result)
print("Just the name:", result.name)
print("Ingredient count:", len(result.ingredients))




# ---------- DEMO 2: Pull structured data out of messy free text ----------
print("=" * 50)
print("DEMO 2: Extract structured data from messy text")
print("=" * 50)

class Contact(BaseModel):
    name: str | None = Field(description="person's name, or null if not mentioned")
    email: str | None = Field(description="email address, or null if not mentioned")
    phone: str | None = Field(description="phone number, or null if not mentioned")

structured_llm = llm.with_structured_output(Contact)

messy_text = """
hey it's Ali again, sorry for the late reply!! you can reach me at
ali.dev99@gmail.com if the form doesn't work, no phone for now
"""

result = structured_llm.invoke(f"Extract the contact info from this message:\n{messy_text}")
print(result)

# NOTE: this is the SAME idea as the receipt -> JSON pipeline from Session 5,
# just without writing the JSON parsing / cleanup code by hand.



# name='Ali' email='ali.dev99@gmail.com' phone=None