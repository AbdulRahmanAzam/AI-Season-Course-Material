"""
Failure experiments — out-of-scope questions, top_k, weak vs strong prompts.
Run: python 8_failure_experiments.py
"""
import os

from dotenv import load_dotenv
from langchain_chroma import Chroma
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_groq import ChatGroq
from langchain_huggingface import HuggingFaceEmbeddings

load_dotenv()

PERSIST_DIR = "db/chroma_db"
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"

embeddings = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL)
db = Chroma(
    persist_directory=PERSIST_DIR,
    embedding_function=embeddings,
    collection_metadata={"hnsw:space": "cosine"},
)


def call_llm(prompt):
    api_key = os.getenv("GROQ_API_KEY", "").strip()
    provider = os.getenv("LLM_PROVIDER", "mock").strip().lower()
    if provider == "mock" or not api_key or api_key == "your_groq_key_here":
        return "[MOCK LLM] " + prompt[:180] + "..."

    llm = ChatGroq(model=os.getenv("GROQ_MODEL", "llama-3.1-8b-instant"), temperature=0.2)
    result = llm.invoke([
        SystemMessage(content="You are a careful assistant."),
        HumanMessage(content=prompt),
    ])
    return result.content


def run_query(question, top_k, prompt_style="normal"):
    docs = db.as_retriever(search_kwargs={"k": top_k}).invoke(question)
    context = "\n".join([d.page_content for d in docs])

    if prompt_style == "weak":
        prompt = f"Context: {context}\nQ: {question}\nA:"
    else:
        prompt = f"""Use ONLY this context. If missing, say you do not know.

Context:
{context}

Question: {question}
"""

    print(f"Query: {question}")
    print(f"top_k={top_k}, prompt={prompt_style}")
    print("Answer:", call_llm(prompt))
    print("-" * 60)


print("=== EXPERIMENT 1: Answer not in documents ===")
run_query("What is the capital of France?", top_k=3)

print("\n=== EXPERIMENT 2: top_k=1 vs top_k=3 ===")
run_query("Tell me about tuition and financial aid.", top_k=1)
run_query("Tell me about tuition and financial aid.", top_k=3)

print("\n=== EXPERIMENT 3: Weak vs strong prompt ===")
run_query("Can alumni borrow books from the library?", top_k=2, prompt_style="weak")
run_query("Can alumni borrow books from the library?", top_k=2, prompt_style="strong")

print("\nTeaching point: RAG helps but does not remove all failures.")
