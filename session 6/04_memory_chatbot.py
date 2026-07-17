"""
FILE 4: Memory - let the model remember the conversation
============================================================
Session 5 FILE 7 kept memory by hand:
    conversation.append(...)
    conversation.append(...)
and re-sent that growing list every time.

RunnableWithMessageHistory does that bookkeeping for you. You just
give every conversation a session_id, and it remembers each session
separately - like separate WhatsApp chats with different people.
"""

import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.chat_history import InMemoryChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory

load_dotenv()
MODEL = "llama-3.3-70b-versatile"
llm = ChatGroq(model=MODEL, temperature=0.7)

prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a helpful assistant. Keep answers short."),
    MessagesPlaceholder("history"),   # <- past messages get inserted right here
    ("human", "{input}"),
])

chain = prompt | llm

# ---------- The memory store: one chat history per session_id ----------
store = {}   # in real apps this would be a database, here a plain dict is enough

def get_session_history(session_id: str) -> InMemoryChatMessageHistory:
    if session_id not in store:
        store[session_id] = InMemoryChatMessageHistory()
    return store[session_id]

chatbot = RunnableWithMessageHistory(
    chain,
    get_session_history,
    input_messages_key="input",
    history_messages_key="history",
)


# ---------- DEMO: same session remembers, different session doesn't ----------
print("=" * 50)
print("DEMO: session 'ali' - tell it a name, then ask for it back")
print("=" * 50)

config = {"configurable": {"session_id": "ali"}}

r1 = chatbot.invoke({"input": "Hi! My name is Ali."}, config=config)
print("Bot:", r1.content)

r2 = chatbot.invoke({"input": "What is my name?"}, config=config)
print("Bot:", r2.content)   # <- remembers, same session_id


print("=" * 50)
print("DEMO: session 'sara' - a totally different, empty conversation")
print("=" * 50)

other_config = {"configurable": {"session_id": "sara"}}

r3 = chatbot.invoke({"input": "What is my name?"}, config=other_config)
print("Bot:", r3.content)   # <- doesn't know - different session_id, fresh history
