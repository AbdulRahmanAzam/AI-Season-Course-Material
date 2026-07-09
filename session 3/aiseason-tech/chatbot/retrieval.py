"""
Retrieval — similarity, score threshold, and MMR search over ChromaDB.
"""
from langchain_community.retrievers import BM25Retriever
from langchain_classic.retrievers import EnsembleRetriever

from .config import DEFAULT_RETRIEVAL_METHOD, DEFAULT_TOP_K


def get_retriever(
    vectorstore,
    method=DEFAULT_RETRIEVAL_METHOD,
    top_k=DEFAULT_TOP_K,
    score_threshold=0.3,
    fetch_k=10,
    lambda_mult=0.5,
    bm25_documents=None,
    hybrid_weights=(0.7, 0.3),
):
    """
    Build a retriever from a Chroma vector store.

    Methods: similarity, similarity_score_threshold, mmr, hybrid
    """
    method = method.lower().strip()

    if method == "similarity":
        return vectorstore.as_retriever(search_kwargs={"k": top_k})

    if method == "similarity_score_threshold":
        return vectorstore.as_retriever(
            search_type="similarity_score_threshold",
            search_kwargs={"k": top_k, "score_threshold": score_threshold},
        )

    if method == "mmr":
        return vectorstore.as_retriever(
            search_type="mmr",
            search_kwargs={
                "k": top_k,
                "fetch_k": fetch_k,
                "lambda_mult": lambda_mult,
            },
        )

    if method == "hybrid":
        if not bm25_documents:
            raise ValueError("hybrid retrieval requires bm25_documents (chunk list).")

        vector_retriever = vectorstore.as_retriever(search_kwargs={"k": top_k})
        bm25_retriever = BM25Retriever.from_documents(bm25_documents)
        bm25_retriever.k = top_k

        return EnsembleRetriever(
            retrievers=[vector_retriever, bm25_retriever],
            weights=list(hybrid_weights),
        )

    raise ValueError(
        f"Unknown retrieval method: {method}. "
        f"Choose from: similarity, similarity_score_threshold, mmr, hybrid."
    )


def retrieve(retriever, query):
    """Run retrieval and return a list of Document objects."""
    return retriever.invoke(query)


def format_retrieved_context(documents):
    """Format retrieved chunks as bullet list for prompts."""
    if not documents:
        return "(no relevant documents retrieved)"

    return "\n".join(f"- {doc.page_content}" for doc in documents)
