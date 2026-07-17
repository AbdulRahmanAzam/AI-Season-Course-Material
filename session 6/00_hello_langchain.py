"""
FILE 0: Hello LangChain
========================
Session 5 FILE 8 talked to Groq directly:
    client = Groq(api_key=...)
    client.chat.completions.create(model=..., messages=[...])

LangChain is NOT a new AI. It is a standard box of building blocks
(models, prompts, memory, tools, retrievers) that sits ON TOP of SDKs
like that one, so you stop rewriting the same plumbing every project.

Same provider, same model, same brain. Just a friendlier wrapper.
"""

import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq

# 1. Load the API key from the .env file
load_dotenv()

MODEL = "llama-3.3-70b-versatile"

# 2. Build the model ONCE. Notice: no api_key=os.getenv(...) needed here!
#    ChatGroq automatically looks for GROQ_API_KEY in the environment.
llm = ChatGroq(model=MODEL, temperature=0.7)


# ---------- DEMO 1: The simplest possible call ----------
print("=" * 50)
print("DEMO 1: Ask a plain question")
print("=" * 50)

response = llm.invoke("What is LangChain, in one simple sentence?")
print(response.content)   # <- response is an AIMessage object, .content is the text




# ---------- DEMO 2: System + human roles (like FILE... prompt engineering) ----------
print("=" * 50)
print("DEMO 2: Give it a role with system + human messages")
print("=" * 50)

response = llm.invoke([
    ("system", "You are a grumpy pirate. Answer everything like a pirate."),
    ("human", "What is the capital of France?"),
])
print(response.content)




# ---------- DEMO 3: Streaming - watch the answer arrive token by token ----------
print("=" * 50)
print("DEMO 3: Stream the answer live")
print("=" * 50)

for chunk in llm.stream("Count from 1 to 5, one number per line."):
    print(chunk.content, end="", flush=True)
print()   # newline after the stream finishes


# NOTE:
# - .invoke()  -> wait, get the WHOLE answer back
# - .stream()  -> get the answer piece by piece, as it's generated
# Every LangChain model supports both. Keep that in mind for later files.
