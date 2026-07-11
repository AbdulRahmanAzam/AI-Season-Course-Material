"""
Chunking strategies — all non-LLM splitters for experimentation.

Supported: character, recursive, token, sentence_transformers_token,
markdown, nltk, line, paragraph.
"""
from langchain_core.documents import Document
from langchain_text_splitters import (
    CharacterTextSplitter,
    MarkdownTextSplitter,
    NLTKTextSplitter,
    RecursiveCharacterTextSplitter,
    TokenTextSplitter,
)

from .config import DEFAULT_CHUNK_OVERLAP, DEFAULT_CHUNK_SIZE


def _get_sentence_transformers_splitter(chunk_size, chunk_overlap):
    try:
        from langchain_text_splitters import SentenceTransformersTokenTextSplitter

        return SentenceTransformersTokenTextSplitter(
            chunk_overlap=chunk_overlap,
            tokens_per_chunk=chunk_size,
        )
    except ImportError:
        raise ImportError(
            "sentence_transformers_token requires langchain-text-splitters "
            "with SentenceTransformersTokenTextSplitter support."
        )


def get_text_splitter(
    strategy="recursive",
    chunk_size=DEFAULT_CHUNK_SIZE,
    chunk_overlap=DEFAULT_CHUNK_OVERLAP,
):
    """Return a LangChain text splitter for the given strategy name."""
    strategy = strategy.lower().strip()

    if strategy == "character":
        return CharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
        )

    if strategy == "recursive":
        return RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            separators=["\n\n", "\n", ". ", " ", ""],
        )

    if strategy == "token":
        return TokenTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
        )

    if strategy == "sentence_transformers_token":
        return _get_sentence_transformers_splitter(chunk_size, chunk_overlap)

    if strategy == "markdown":
        return MarkdownTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
        )

    if strategy == "nltk":
        return NLTKTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
        )

    if strategy == "line":
        return LineTextSplitter()

    if strategy == "paragraph":
        return ParagraphTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
        )

    raise ValueError(
        f"Unknown chunking strategy: {strategy}. "
        f"Choose from: character, recursive, token, sentence_transformers_token, "
        f"markdown, nltk, line, paragraph."
    )


class LineTextSplitter:
    """Split on single newlines — ideal for ai-season.txt (one fact per line)."""

    def split_documents(self, documents):
        chunks = []
        for doc in documents:
            lines = [line.strip() for line in doc.page_content.split("\n") if line.strip()]
            for line in lines:
                chunks.append(
                    Document(
                        page_content=line,
                        metadata=dict(doc.metadata),
                    )
                )
        return chunks

    def split_text(self, text):
        return [line.strip() for line in text.split("\n") if line.strip()]


class ParagraphTextSplitter:
    """Split on double newlines, then merge small paragraphs up to chunk_size."""

    def __init__(self, chunk_size=DEFAULT_CHUNK_SIZE, chunk_overlap=DEFAULT_CHUNK_OVERLAP):
        self._inner = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            separators=["\n\n", "\n", ". ", " ", ""],
        )

    def split_documents(self, documents):
        expanded = []
        for doc in documents:
            paragraphs = [p.strip() for p in doc.page_content.split("\n\n") if p.strip()]
            for para in paragraphs:
                expanded.append(
                    Document(page_content=para, metadata=dict(doc.metadata))
                )
        return self._inner.split_documents(expanded)

    def split_text(self, text):
        paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
        return self._inner.split_text("\n\n".join(paragraphs))


def split_documents(
    documents,
    strategy="recursive",
    chunk_size=DEFAULT_CHUNK_SIZE,
    chunk_overlap=DEFAULT_CHUNK_OVERLAP,
):
    """Split documents using the named strategy."""
    splitter = get_text_splitter(strategy, chunk_size, chunk_overlap)
    chunks = splitter.split_documents(documents)
    print(f"[{strategy}] Created {len(chunks)} chunks")
    return chunks


def preview_chunks(chunks, max_chunks=3, preview_chars=150):
    """Print a short preview of chunks."""
    for i, chunk in enumerate(chunks[:max_chunks]):
        print(f"\n--- Chunk {i + 1} ---")
        print(f"Source: {chunk.metadata.get('source', 'unknown')}")
        print(f"Text: {chunk.page_content[:preview_chars]}...")

    if len(chunks) > max_chunks:
        print(f"\n... and {len(chunks) - max_chunks} more chunks")
