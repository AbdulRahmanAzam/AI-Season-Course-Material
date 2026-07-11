"""
Embedding model — local Hugging Face sentence-transformers (no API key).
"""
from langchain_huggingface import HuggingFaceEmbeddings

from .config import EMBEDDING_MODEL

_embedding_cache = {}


def get_embedding_model(model_name=EMBEDDING_MODEL):
    """Return a cached HuggingFaceEmbeddings instance."""
    if model_name not in _embedding_cache:
        print(f"Loading embedding model: {model_name}")
        print("(First run downloads the model — ~80MB for all-MiniLM-L6-v2)")
        _embedding_cache[model_name] = HuggingFaceEmbeddings(model_name=model_name)

    return _embedding_cache[model_name]
