"""
File loading — load ai-season.txt (or any text file) into LangChain documents.
"""
import os

from langchain_community.document_loaders import TextLoader
from langchain_core.documents import Document

from .config import DATA_FILE


def load_text_file(file_path=DATA_FILE):
    """Load a single text file and return LangChain Document objects."""
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")

    loader = TextLoader(file_path, encoding="utf-8")
    documents = loader.load()

    if len(documents) == 0:
        raise ValueError(f"No content loaded from {file_path}")

    return documents


def load_as_single_document(file_path=DATA_FILE, source_name=None):
    """Load file content as one Document (useful for custom chunking)."""
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")

    with open(file_path, encoding="utf-8") as f:
        text = f.read()

    source = source_name or file_path
    return [Document(page_content=text, metadata={"source": source})]


def preview_documents(documents, max_docs=2, preview_chars=120):
    """Print a short preview of loaded documents."""
    print(f"Loaded {len(documents)} document(s)\n")

    for i, doc in enumerate(documents[:max_docs]):
        print(f"Document {i + 1}:")
        print(f"  Source: {doc.metadata.get('source', 'unknown')}")
        print(f"  Length: {len(doc.page_content)} characters")
        print(f"  Preview: {doc.page_content[:preview_chars]}...")
        print()
