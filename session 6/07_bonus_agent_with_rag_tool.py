"""
FILE 7 (BONUS): Agent + RAG + Tools, all together
====================================================
OPTIONAL - show this if time allows, don't have to live-code it.

Everything so far was separate: FILE 5 gave the model tools, FILE 6 gave
it a knowledge base. This file does both at once: a search over our
knowledge base is JUST ANOTHER TOOL. The agent decides by itself
whether to search the FAQ, check the weather, or just answer directly.

No if/else routing written by hand - the model chooses.
"""

from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.tools import tool
from langchain.agents import create_agent

load_dotenv()
MODEL = "llama-3.3-70b-versatile"
llm = ChatGroq(model=MODEL, temperature=0)

# ---------- Rebuild the same tiny knowledge base from FILE 6 ----------
bootcamp_facts = [
    "The AI Season bootcamp runs live sessions every week covering practical AI engineering.",
    "Session 6 covers LangChain: prompts, chains, memory, tools, agents, and RAG, using the Groq API.",
    "Students must bring their own laptop with Python 3.10 or newer installed.",
    "The instructor's office hours are on Sunday evenings for anyone stuck on an assignment.",
    "There is no final exam - the bootcamp is graded entirely on session projects.",
]
embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
retriever = FAISS.from_texts(bootcamp_facts, embedding=embeddings).as_retriever(search_kwargs={"k": 2})


# ---------- Tool 1: search the FAQ (wraps the retriever from FILE 6) ----------
@tool
def search_bootcamp_faq(query: str) -> str:
    """Searches the bootcamp FAQ for anything related to the course, sessions, or grading."""
    print(f"   [tool running] search_bootcamp_faq('{query}')")
    docs = retriever.invoke(query)
    return "\n".join(doc.page_content for doc in docs)


# ---------- Tool 2: same weather tool from FILE 5, for contrast ----------
@tool
def get_weather(city: str) -> str:
    """Gets the current weather for a city."""
    print(f"   [tool running] get_weather(city='{city}')")
    fake_weather = {"karachi": "34 C, sunny", "london": "18 C, rainy", "tokyo": "25 C, cloudy"}
    return fake_weather.get(city.lower(), "22 C, clear sky")


agent = create_agent(
    model=llm,
    tools=[search_bootcamp_faq, get_weather],
    system_prompt=(
        "You are the bootcamp assistant. Use search_bootcamp_faq for questions about the "
        "course. Use get_weather for weather questions. Answer directly if no tool is needed."
    ),
)


def ask(question: str):
    result = agent.invoke({"messages": [{"role": "user", "content": question}]})
    for msg in result["messages"]:
        if getattr(msg, "tool_calls", None):
            for call in msg.tool_calls:
                print(f"   [agent chose] {call['name']}({call['args']})")
    print("Final answer:", result["messages"][-1].content)


# ---------- DEMO: three questions, three different situations ----------
print("=" * 50)
print("Q1: needs the FAQ tool")
print("=" * 50)
ask("How are students graded in the bootcamp?")

print("=" * 50)
print("Q2: needs the weather tool")
print("=" * 50)
ask("What's the weather like in London right now?")

print("=" * 50)
print("Q3: needs no tool at all")
print("=" * 50)
ask("What is 15 + 27?")
