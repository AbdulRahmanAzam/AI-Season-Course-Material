"""
AI Season Knowledge Assistant — Streamlit app (flat single-file style).
Run: streamlit run 10_streamlit_app.py
"""
import os

import streamlit as st
from dotenv import load_dotenv
from langchain_chroma import Chroma
from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain_core.documents import Document
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_groq import ChatGroq
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_text_splitters import CharacterTextSplitter

load_dotenv()

PERSIST_DIR = "db/chroma_db_app"
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"

AI_SEASON_TEXT = """
AI Season — Program Guide

AI Season is a hands-on learning program for practical AI skills.
This session teaches RAG: convert documents to searchable knowledge, retrieve chunks, and ground LLM answers.

Schedule:
- Week 1: RAG and document ingestion
- Week 2: Embeddings and vector databases
- Week 3: Prompting and failure modes
- Week 4: Build your knowledge assistant

Tools: Python, sentence-transformers, ChromaDB, Groq API, Streamlit.
Office hours: Tuesdays 4-6 PM. Email: aiseason@example.edu
Certificate: attend 3 of 4 sessions and demo your final RAG project.
"""


def use_mock():
    key = os.getenv("GROQ_API_KEY", "").strip()
    provider = os.getenv("LLM_PROVIDER", "mock").strip().lower()
    return provider == "mock" or not key or key == "your_groq_key_here"


def index_text(text, source_name="knowledge.txt"):
    splitter = CharacterTextSplitter(chunk_size=400, chunk_overlap=40)
    doc = Document(page_content=text, metadata={"source": source_name})
    chunks = splitter.split_documents([doc])

    embeddings = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL)
    return Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory=PERSIST_DIR,
        collection_metadata={"hnsw:space": "cosine"},
    )


def answer_question(db, question, top_k=3):
    docs = db.as_retriever(search_kwargs={"k": top_k}).invoke(question)
    context = "\n".join([f"- {d.page_content}" for d in docs])
    prompt = f"""Answer using ONLY this context. If missing, say you do not know.

Context:
{context}

Question: {question}
"""

    if use_mock():
        llm_answer = f"[MOCK LLM] Demo answer for: {question}"
    else:
        llm = ChatGroq(model=os.getenv("GROQ_MODEL", "llama-3.1-8b-instant"), temperature=0.2)
        llm_answer = llm.invoke([
            SystemMessage(content="You are a helpful assistant."),
            HumanMessage(content=prompt),
        ]).content

    return docs, prompt, llm_answer


st.set_page_config(page_title="AI Season RAG App", layout="wide")
st.title("AI Season Knowledge Assistant")
st.caption("How AI Answers From Your Data")

with st.sidebar:
    st.header("Settings")
    st.write("LLM:", "mock" if use_mock() else "groq")
    top_k = st.slider("top_k", 1, 5, 3)

use_sample = st.checkbox("Use built-in AI Season sample text", value=True)
uploaded = st.file_uploader("Or upload a .txt file", type=["txt"])

text = AI_SEASON_TEXT if use_sample and uploaded is None else None
source = "ai_season_sample.txt"
if uploaded:
    text = uploaded.read().decode("utf-8")
    source = uploaded.name

if text is None:
    st.warning("Provide sample text or upload a file.")
    st.stop()

if st.button("Build Index", type="primary"):
    with st.spinner("Indexing..."):
        st.session_state.db = index_text(text, source)
    st.success("Index ready")

if "db" not in st.session_state:
    st.info("Click Build Index first.")
    st.stop()

question = st.text_input("Ask a question", "When are office hours?")
if st.button("Get Answer"):
    docs, prompt, answer = answer_question(st.session_state.db, question, top_k)

    c1, c2 = st.columns(2)
    with c1:
        st.subheader("Answer")
        st.write(answer)
        st.subheader("Sources")
        for i, d in enumerate(docs, 1):
            st.markdown(f"**{i}.** `{d.metadata.get('source')}`")
            st.caption(d.page_content[:250])
    with c2:
        st.subheader("Retrieved chunks")
        for i, d in enumerate(docs, 1):
            with st.expander(f"Chunk {i}"):
                st.text(d.page_content)
        st.subheader("Prompt")
        st.code(prompt)
