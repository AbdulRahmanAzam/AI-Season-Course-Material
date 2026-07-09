"""
Answer generation — retrieve chunks, build prompt, call Groq (or mock fallback).
Same style as rag-for-beginners/3_answer_generation.py but uses ChatGroq.

Run: python 4_answer_generation.py
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

embedding_model = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL)

db = Chroma(
    persist_directory=PERSIST_DIR,
    embedding_function=embedding_model,
    collection_metadata={"hnsw:space": "cosine"},
)

query = "How do I request a refund?"

retriever = db.as_retriever(search_kwargs={"k": 3})
relevant_docs = retriever.invoke(query)

print(f"User Query: {query}\n")
print("--- Context ---")
for i, doc in enumerate(relevant_docs, 1):
    print(f"Document {i}:\n{doc.page_content}\n")

combined_input = f"""Based on the following documents, please answer this question: {query}

Documents:
{chr(10).join([f"- {doc.page_content}" for doc in relevant_docs])}

Answer using ONLY the documents above. If the answer is not there, say:
"I don't have enough information in the provided documents."
"""

print("--- Prompt sent to LLM ---")
print(combined_input)
print("-" * 60)

messages = [
    SystemMessage(content="You are a helpful assistant."),
    HumanMessage(content=combined_input),
]


def use_mock_llm():
    api_key = os.getenv("GROQ_API_KEY", "").strip()
    provider = os.getenv("LLM_PROVIDER", "mock").strip().lower()
    return provider == "mock" or not api_key or api_key == "your_groq_key_here"


if use_mock_llm():
    print("\n[MOCK MODE] No Groq key — returning a simple demo answer.\n")
    snippet = relevant_docs[0].page_content[:200] if relevant_docs else ""
    answer = f"[MOCK LLM] Based on the retrieved documents about '{query}': {snippet}..."
else:
    model = ChatGroq(
        model=os.getenv("GROQ_MODEL", "llama-3.1-8b-instant"),
        temperature=0.2,
    )
    result = model.invoke(messages)
    answer = result.content

print("--- Generated Response ---")
print(answer)
