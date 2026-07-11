"""
Vector DB storage — ChromaDB with one collection per chunking strategy.
"""
import os

from langchain_chroma import Chroma

from .config import CHROMA_BASE_DIR
from .embeddings import get_embedding_model


def get_persist_directory(chunking_strategy, base_dir=CHROMA_BASE_DIR):
    """Return the Chroma persist path for a chunking strategy."""
    return os.path.join(base_dir, chunking_strategy)


def create_vector_store(chunks, chunking_strategy, base_dir=CHROMA_BASE_DIR):
    """Embed chunks and store them in a new Chroma collection."""
    persist_dir = get_persist_directory(chunking_strategy, base_dir)
    embedding_model = get_embedding_model()

    print(f"Creating vector store at {persist_dir}...")

    vectorstore = Chroma.from_documents(
        documents=chunks,
        embedding=embedding_model,
        persist_directory=persist_dir,
        collection_name=f"aiseason_{chunking_strategy}",
        collection_metadata={"hnsw:space": "cosine"},
    )

    count = vectorstore._collection.count()
    print(f"Stored {count} chunks in ChromaDB ({chunking_strategy})")
    return vectorstore


def load_vector_store(chunking_strategy, base_dir=CHROMA_BASE_DIR):
    """Load an existing Chroma vector store for a chunking strategy."""
    persist_dir = get_persist_directory(chunking_strategy, base_dir)

    if not os.path.exists(persist_dir):
        raise FileNotFoundError(
            f"No vector store for '{chunking_strategy}' at {persist_dir}. "
            f"Run run_ingestion.py first."
        )

    embedding_model = get_embedding_model()
    vectorstore = Chroma(
        persist_directory=persist_dir,
        embedding_function=embedding_model,
        collection_name=f"aiseason_{chunking_strategy}",
        collection_metadata={"hnsw:space": "cosine"},
    )

    print(f"Loaded {vectorstore._collection.count()} chunks ({chunking_strategy})")
    return vectorstore


def vector_store_exists(chunking_strategy, base_dir=CHROMA_BASE_DIR):
    """Check whether a persisted vector store exists."""
    return os.path.exists(get_persist_directory(chunking_strategy, base_dir))
