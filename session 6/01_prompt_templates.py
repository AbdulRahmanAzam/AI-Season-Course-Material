"""
FILE 1: Prompt Templates
=========================
You already know prompt engineering: writing a good instruction, maybe
gluing user input into an f-string. That gets messy fast.

A PromptTemplate is a prompt with BLANKS in it ({like_this}) that you
fill in later. Write the prompt once, reuse it forever with different
inputs. That's the whole idea.
"""

import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate

load_dotenv()
MODEL = "llama-3.3-70b-versatile"
llm = ChatGroq(model=MODEL, temperature=0.7)


# ---------- DEMO 1: A template just builds messages (no model yet!) ----------
print("=" * 50)
print("DEMO 1: A template is just a message builder")
print("=" * 50)

template = ChatPromptTemplate.from_messages([
    ("system", "You are a friendly {role}."),
    ("human", "{question}"),
])

# .invoke() on a TEMPLATE doesn't call any model - it just fills the blanks
filled = template.invoke({
    "role": "math teacher", 
    "question": "What is 12 * 12?"
})
print(filled.to_messages())   # <- see? just a list of message objects, no AI involved yet


# ---------- DEMO 2: One template, many uses ----------
print("=" * 50)
print("DEMO 2: Reuse the same template with different inputs")
print("=" * 50)

chain = template | llm   # now we connect it to the model (more on "|" in FILE 2)

questions = [
    {"role": "math teacher", "question": "What is 12 * 12?"},
    {"role": "pirate", "question": "What is 12 * 12?"},
    {"role": "poet", "question": "What is 12 * 12?"},
]

for q in questions:
    result = chain.invoke(q)
    print(f"[{q['role']}] {result.content}")
    


# ---------- DEMO 3: Few-shot - show examples instead of just instructions ----------
print("=" * 50)
print("DEMO 3: Few-shot - teach by example")
print("=" * 50)

few_shot_template = ChatPromptTemplate.from_messages([
    ("system", "Convert product names into short, punchy taglines. Follow the style below."),
    ("human", "Product: wireless earbuds"),
    ("ai", "Cut the cord. Keep the beat."),
    ("human", "Product: standing desk"),
    ("ai", "Sit less. Stand tall."),
    ("human", "Product: {product}"),   # <- the model copies the PATTERN of the examples above
])

chain = few_shot_template | llm
result = chain.invoke({"product": "noise-cancelling headphones"})
print(result.content)
