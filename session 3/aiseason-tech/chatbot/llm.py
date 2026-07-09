"""
LLM answer generation — Groq API (or mock fallback when no key).
"""
import os

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_groq import ChatGroq

from .config import GROQ_MODEL, LLM_TEMPERATURE


def use_mock_llm():
    """Return True when Groq should be skipped (teaching / no API key)."""
    api_key = os.getenv("GROQ_API_KEY", "").strip()
    provider = os.getenv("LLM_PROVIDER", "mock").strip().lower()
    return provider == "mock" or not api_key or api_key == "your_groq_key_here"


def get_llm():
    """Return a ChatGroq instance."""
    return ChatGroq(model=GROQ_MODEL, temperature=LLM_TEMPERATURE)


def build_rag_prompt(question, context):
    """Prompt that includes retrieved context (RAG mode)."""
    return f"""Answer this question using ONLY the context below.

Context:
{context}

Question: {question}

If the answer is not in the context, say:
"I don't have enough information in the provided documents."
"""


def build_no_context_prompt(question):
    """Prompt with question only — no retrieved chunks (baseline mode)."""
    return f"""Answer this question about AI Season as best you can.

Question: {question}

If you are not sure, say you do not have enough information.
Do not invent specific prices, dates, or instructor details.
"""


def generate_answer(prompt, system_message="You are a helpful AI Season assistant."):
    """Call Groq (or return a mock answer)."""
    if use_mock_llm():
        return f"[MOCK LLM] Demo answer for prompt starting with: {prompt[:120]}..."

    llm = get_llm()
    result = llm.invoke([
        SystemMessage(content=system_message),
        HumanMessage(content=prompt),
    ])
    return result.content
