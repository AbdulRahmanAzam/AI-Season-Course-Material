"""
FILE 4: LangChain -- one shape for all three
===============================================
FILES 1-3 each had their own JSON shape, their own SDK, their own way of
reading the answer back out. LangChain hides all three behind ONE shape:
build a chat model object, then always call the same .invoke(question).

Three different providers below (one of them via DigitalOcean), zero
custom parsing, same loop for all three.
"""

import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_openai import ChatOpenAI

load_dotenv()
QUESTION = "In one sentence, what makes you different from other LLM providers?"

models = {
    # ChatGroq auto-reads GROQ_API_KEY from the environment -- no api_key= needed
    "Groq": ChatGroq(model="llama-3.3-70b-versatile"),

    "Gemini": ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
        api_key=os.getenv("GEMINI_API_KEY"),
    ),

    "OpenAI SDK via DigitalOcean": ChatOpenAI(
        model="llama3-8b-instruct",
        base_url="https://inference.do-ai.run/v1/",
        api_key=os.getenv("DIGITAL_OCEAN_MODEL_ACCESS_KEY"),
    ),
}

# model = ChatGroq()

for name, llm in models.items():
    print("=" * 50)
    print(name)
    print("=" * 50)

    response = llm.invoke(QUESTION)   # <- SAME call, every provider, every time
    print(response.content)           # <- SAME attribute, every provider, every time


# NOTE:
# - Compare this file to FILES 1-3: no requests.post, no headers=, no
#   response.json()["choices"][0]... -- every provider became the same
#   3 lines: build the model once, call .invoke(), read .content.
# - That's the whole pitch for LangChain: not a new AI, a standard socket
#   that any provider's SDK plugs into.
