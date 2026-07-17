"""
FILE 2: Chains - the "|" pipe (THE big LangChain idea)
========================================================
This is the one thing to remember from today.

Every LangChain piece - a prompt, a model, a parser, even a retriever -
is a "Runnable." You connect Runnables with the "|" symbol, exactly
like Unix pipes:

    prompt | model | parser

Data flows left to right. Each piece does its one job and hands the
result to the next piece. That's a "chain."
"""

import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

load_dotenv()
MODEL = "llama-3.3-70b-versatile"
llm = ChatGroq(model=MODEL, temperature=0.7)

prompt = ChatPromptTemplate.from_messages([
    ("system", "Answer in exactly one short sentence."),
    ("human", "{question}"),
])


# ---------- DEMO 1: prompt | llm ----------
print("=" * 50)
print("DEMO 1: prompt | llm")
print("=" * 50)

chain = prompt | llm
result = chain.invoke({"question": "Why is the sky blue?"})
print(type(result))     # <- still an AIMessage object
print(result.content)


# ---------- DEMO 2: prompt | llm | parser ----------
print("=" * 50)
print("DEMO 2: prompt | llm | StrOutputParser")
print("=" * 50)

# Session 5 FILE 8 had to dig out the text with response.choices[0].message.content
# Add a parser to the end of the pipe and the chain just returns a plain string.
chain = prompt | llm | StrOutputParser()
result = chain.invoke({"question": "Why is the sky blue?"})
print(type(result))     # <- now it's just a str
print(result)


# ---------- DEMO 3: .batch() - run many inputs through the SAME chain ----------
print("=" * 50)
print("DEMO 3: .batch() - many questions, one call")
print("=" * 50)

# invoke = one input -> one output. batch = many inputs -> many outputs.
# Works because EVERY Runnable supports invoke / batch / stream the same way.
questions = [
    {"question": "Why is the sky blue?"},
    {"question": "Why do we dream?"},
    {"question": "Why is the ocean salty?"},
]

answers = chain.batch(questions)
for q, a in zip(questions, answers):
    print(f"Q: {q['question']}\nA: {a}\n")
