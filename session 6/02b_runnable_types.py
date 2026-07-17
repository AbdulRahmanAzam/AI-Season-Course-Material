"""
FILE 2B: Runnable Types - the building blocks behind "|"
===========================================================
FILE 2 showed prompt | llm | parser. That "|" only works because every
piece is a "Runnable" - one shared interface (.invoke/.batch/.stream).

There isn't just one kind of Runnable. Here are the ones you'll
actually meet:

  RunnableSequence   - what "|" builds. Runs steps LEFT TO RIGHT,
                        each step's output feeds the next step's input.

  RunnableLambda      - turns a normal Python function into a Runnable,
                        so YOUR code can sit inside a "|" chain too.

  RunnableParallel     - runs several Runnables on the SAME input at
                        the same time, returns a dict of their results.
                        (write it as a plain {..} dict inside a chain)

  RunnablePassthrough  - does nothing. Just hands the input straight
                        through. Useful inside RunnableParallel when
                        one branch needs the ORIGINAL input untouched
                        (e.g. RAG: keep the question while another
                        branch fetches documents for it).

All four are Runnables, so all four support .invoke() / .batch() /
.stream() the exact same way. That sameness is the whole point.
"""

import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnableLambda, RunnableParallel, RunnablePassthrough

load_dotenv()
MODEL = "llama-3.3-70b-versatile"
llm = ChatGroq(model=MODEL, temperature=0.7)

prompt = ChatPromptTemplate.from_messages([
    ("system", "Answer in exactly one short sentence.{aaj ke halaat kia he, 14-7-2026} asdfjakldsfjas;dfasdjf(5000 tokens)zxcsdf"),
    ("human", "{question}"),
])

# cached input -> 1 dollars / 1 million tokens
# input -> 5 dollars / 1 million tokens
# output -> 15 dollars / 1 milltion tokens


# ---------- DEMO 1: RunnableSequence - what "|" already builds ----------
print("=" * 50)
print("DEMO 1: RunnableSequence (prompt | llm | parser)")
print("=" * 50)

# You already wrote this in FILE 2. This IS a RunnableSequence -
# "|" is just shorthand for building one.
chain = prompt | llm | StrOutputParser()

# formatted_prompt = prompt.format(input_variable="value")
# response = llm.invoke(formatted_prompt)
# output = StrOutputParser().parse(response.content)

# print(type(chain).__name__)      # <- RunnableSequence
print(chain.invoke({"question": "Why is the sky blue?"}))




# # ---------- DEMO 2: RunnableLambda - plug a plain function into "|" ----------
print("\n\n","=" * 50)
print("DEMO 2: RunnableLambda - your own function in the chain")
print("=" * 50)

shout = RunnableLambda(lambda text: text.upper() + "!!!")

# Now a normal Python function is a chain step, same as prompt or llm.
chain = prompt | llm | StrOutputParser() | shout
print(chain.invoke({"question": "Why is the sky blue?"}))




# ---------- DEMO 3: RunnableParallel - run steps side by side ----------
print("\n\n","=" * 50)
print("DEMO 3: RunnableParallel - same input, multiple branches at once")
print("=" * 50)


# A plain {..} dict inside a chain IS a RunnableParallel. Each key runs
# on the SAME input, all at once, results come back keyed the same way.
parallel = RunnableParallel(
    answer=prompt | llm | StrOutputParser(),
    shouted=prompt | llm | StrOutputParser() | shout,
)
result = parallel.invoke({"question": "Why is the sky blue?"})
print(result)          # <- {"answer": "...", "shouted": "...!!!"}




# ---------- DEMO 4: RunnablePassthrough - keep the original input ----------
print("\n\n","=" * 50)
print("DEMO 4: RunnablePassthrough - pass input through untouched")
print("=" * 50)

# Common in RAG: one branch answers the question, the other branch just
# hands back the original question so you still have it at the end.
parallel_with_passthrough = RunnableParallel(
    original_question=RunnablePassthrough(),
    answer=prompt | llm | StrOutputParser(),
)
result = parallel_with_passthrough.invoke({"question": "Why is the sky blue?"})
print(result)           # <- {"original_question": {"question": "..."}, "answer": "..."}
