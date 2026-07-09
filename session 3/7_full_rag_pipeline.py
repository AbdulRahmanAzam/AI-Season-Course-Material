"""
Full RAG pipeline in one script — ingest, retrieve, prompt, Groq answer, sources.
Run: python 7_full_rag_pipeline.py
"""
import os

from dotenv import load_dotenv
from langchain_chroma import Chroma
from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_groq import ChatGroq
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_text_splitters import CharacterTextSplitter

load_dotenv()

DOCS_PATH = "docs"
PERSIST_DIR = "db/chroma_db"
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"


def build_vector_store():
    print("[1] Loading and chunking documents...")
    loader = DirectoryLoader(path=DOCS_PATH, glob="*.txt", loader_cls=TextLoader)
    documents = loader.load()

    splitter = CharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    chunks = splitter.split_documents(documents)
    print(f"    {len(documents)} docs -> {len(chunks)} chunks")

    print("[2] Embedding and storing in ChromaDB...")
    embeddings = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL)
    return Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory=PERSIST_DIR,
        collection_metadata={"hnsw:space": "cosine"},
    )


def ask(db, question, top_k=3):
    print(f"\nQuestion: {question}")

    print("[3] Retrieving relevant chunks...")
    retriever = db.as_retriever(search_kwargs={"k": top_k})
    docs = retriever.invoke(question)
    print(f"    Retrieved {len(docs)} chunk(s)")

    context = "\n".join([f"- {d.page_content}" for d in docs])
    prompt = f"""Answer this question using ONLY the context below.

Context:
{context}

Question: {question}

If the answer is not in the context, say you do not have enough information.
"""

    print("[4] Calling LLM...")
    print("\n--- Prompt ---")
    print(prompt)

    api_key = os.getenv("GROQ_API_KEY", "").strip()
    provider = os.getenv("LLM_PROVIDER", "mock").strip().lower()
    use_mock = provider == "mock" or not api_key or api_key == "your_groq_key_here"

    if use_mock:
        answer = f"[MOCK LLM] Summary from retrieved docs for: {question}"
    else:
        llm = ChatGroq(model=os.getenv("GROQ_MODEL", "llama-3.1-8b-instant"), temperature=0.2)
        result = llm.invoke([
            SystemMessage(content="You are a helpful assistant."),
            HumanMessage(content=prompt),
        ])
        answer = result.content

    print("\n--- Answer ---")
    print(answer)

    print("\n--- Sources ---")
    for i, doc in enumerate(docs, 1):
        print(f"  [{i}] {doc.metadata.get('source')}")
        print(f"      {doc.page_content[:120]}...")


def main():
    print("=== Full RAG Pipeline ===\n")

    if os.path.exists(PERSIST_DIR):
        embeddings = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL)
        db = Chroma(
            persist_directory=PERSIST_DIR,
            embedding_function=embeddings,
            collection_metadata={"hnsw:space": "cosine"},
        )
        print(f"Loaded existing vector store ({db._collection.count()} chunks)\n")
    else:
        db = build_vector_store()

    ask(db, "What is the in-state tuition at Riverside University?")
    ask(db, "How do I request a refund from ACME store?")


if __name__ == "__main__":
    main()
