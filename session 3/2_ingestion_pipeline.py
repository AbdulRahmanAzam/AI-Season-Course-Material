"""
Ingestion pipeline — load docs/, chunk, embed (local), store in ChromaDB.
Same style as rag-for-beginners/1_ingestion_pipeline.py but with free local embeddings.

Run: python 2_ingestion_pipeline.py
"""
import os

from dotenv import load_dotenv
from langchain_chroma import Chroma
from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_text_splitters import CharacterTextSplitter

load_dotenv()

DOCS_PATH = "docs"
PERSIST_DIR = "db/chroma_db"
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"


def load_documents(docs_path=DOCS_PATH):
    print(f"Loading documents from {docs_path}...")

    if not os.path.exists(docs_path):
        raise FileNotFoundError(f"Folder not found: {docs_path}. Run 1_file_conversion.py first.")

    loader = DirectoryLoader(
        path=docs_path,
        glob="*.txt",
        loader_cls=TextLoader,
    )
    documents = loader.load()

    if len(documents) == 0:
        raise FileNotFoundError(f"No .txt files in {docs_path}")

    for i, doc in enumerate(documents[:2]):
        print(f"\nDocument {i + 1}:")
        print(f"  Source: {doc.metadata['source']}")
        print(f"  Length: {len(doc.page_content)} characters")
        print(f"  Preview: {doc.page_content[:120]}...")

    return documents


def split_documents(documents, chunk_size=500, chunk_overlap=50):
    print("\nSplitting documents into chunks...")

    splitter = CharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
    )
    chunks = splitter.split_documents(documents)
    print(f"Created {len(chunks)} chunks")

    for i, chunk in enumerate(chunks[:3]):
        print(f"\n--- Chunk {i + 1} ---")
        print(f"Source: {chunk.metadata['source']}")
        print(f"Text: {chunk.page_content[:150]}...")

    if len(chunks) > 3:
        print(f"\n... and {len(chunks) - 3} more chunks")

    return chunks


def create_vector_store(chunks, persist_directory=PERSIST_DIR):
    print("\nCreating embeddings and storing in ChromaDB...")
    print("(First run downloads the local embedding model ~80MB)")

    embedding_model = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL)

    vectorstore = Chroma.from_documents(
        documents=chunks,
        embedding=embedding_model,
        persist_directory=persist_directory,
        collection_metadata={"hnsw:space": "cosine"},
    )

    print(f"Vector store saved to {persist_directory}")
    return vectorstore


def main():
    print("=== RAG Ingestion Pipeline ===\n")

    if os.path.exists(PERSIST_DIR):
        print("Vector store already exists. Loading it instead of re-ingesting.\n")
        embedding_model = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL)
        vectorstore = Chroma(
            persist_directory=PERSIST_DIR,
            embedding_function=embedding_model,
            collection_metadata={"hnsw:space": "cosine"},
        )
        print(f"Loaded {vectorstore._collection.count()} chunks from {PERSIST_DIR}")
        return vectorstore

    documents = load_documents()
    chunks = split_documents(documents)
    vectorstore = create_vector_store(chunks)

    print("\nIngestion complete. Run 3_retrieval_pipeline.py next.")
    return vectorstore


if __name__ == "__main__":
    main()
