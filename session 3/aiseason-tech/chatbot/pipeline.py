"""
RAG pipeline — orchestrates load, chunk, embed, retrieve, and answer.
"""
from .chunking import split_documents
from .file_loader import load_text_file
from .llm import build_no_context_prompt, build_rag_prompt, generate_answer
from .retrieval import format_retrieved_context, get_retriever, retrieve
from .vector_store import create_vector_store, load_vector_store, vector_store_exists


def ingest(
    chunking_strategy="recursive",
    file_path=None,
    chunk_size=None,
    chunk_overlap=None,
    force=False,
):
    """Load ai-season.txt, chunk, embed, and store in ChromaDB."""
    from .config import DATA_FILE, DEFAULT_CHUNK_OVERLAP, DEFAULT_CHUNK_SIZE

    path = file_path or DATA_FILE

    if vector_store_exists(chunking_strategy) and not force:
        print(f"Vector store already exists for '{chunking_strategy}'. Loading...")
        return load_vector_store(chunking_strategy)

    documents = load_text_file(path)
    chunks = split_documents(
        documents,
        strategy=chunking_strategy,
        chunk_size=chunk_size or DEFAULT_CHUNK_SIZE,
        chunk_overlap=chunk_overlap or DEFAULT_CHUNK_OVERLAP,
    )
    return create_vector_store(chunks, chunking_strategy)


def ask(
    question,
    chunking_strategy="recursive",
    top_k=3,
    retrieval_method="similarity",
    use_retrieved_context=True,
    bm25_documents=None,
):
    """
    Answer a question.

    use_retrieved_context=True  -> RAG (chunks sent to LLM)
    use_retrieved_context=False -> baseline (question only, no chunks)
    """
    vectorstore = load_vector_store(chunking_strategy)
    retriever = get_retriever(
        vectorstore,
        method=retrieval_method,
        top_k=top_k,
        bm25_documents=bm25_documents,
    )
    docs = retrieve(retriever, question)
    context = format_retrieved_context(docs)

    if use_retrieved_context:
        prompt = build_rag_prompt(question, context)
    else:
        prompt = build_no_context_prompt(question)

    answer = generate_answer(prompt)

    return {
        "question": question,
        "answer": answer,
        "prompt": prompt,
        "retrieved_docs": docs,
        "use_retrieved_context": use_retrieved_context,
        "chunking_strategy": chunking_strategy,
        "retrieval_method": retrieval_method,
    }
