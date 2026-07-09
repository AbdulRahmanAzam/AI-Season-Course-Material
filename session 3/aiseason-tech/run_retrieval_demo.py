"""
Retrieval methods demo — similarity, threshold, MMR on AI Season index.

Run from repo root:
  python aiseason-tech/run_retrieval_demo.py
  python aiseason-tech/run_retrieval_demo.py --method mmr
"""
import argparse
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from chatbot.config import DEFAULT_TOP_K  # noqa: E402
from chatbot.pipeline import ingest  # noqa: E402
from chatbot.retrieval import get_retriever, retrieve  # noqa: E402
from chatbot.vector_store import load_vector_store, vector_store_exists  # noqa: E402

DEFAULT_QUERY = "What is the early-bird price of AI Season?"


def main():
    parser = argparse.ArgumentParser(description="Retrieval methods demo")
    parser.add_argument("--strategy", default="recursive")
    parser.add_argument("--query", default=DEFAULT_QUERY)
    parser.add_argument(
        "--method",
        default="all",
        choices=["all", "similarity", "similarity_score_threshold", "mmr"],
    )
    parser.add_argument("--top-k", type=int, default=DEFAULT_TOP_K)
    args = parser.parse_args()

    print("=== AI Season Retrieval Demo ===\n")
    print(f"Query: {args.query}\n")

    if not vector_store_exists(args.strategy):
        print(f"Building index for '{args.strategy}'...\n")
        ingest(chunking_strategy=args.strategy)

    db = load_vector_store(args.strategy)
    methods = (
        ["similarity", "similarity_score_threshold", "mmr"]
        if args.method == "all"
        else [args.method]
    )

    for method in methods:
        print(f"--- {method.upper()} (k={args.top_k}) ---")
        retriever = get_retriever(db, method=method, top_k=args.top_k)
        docs = retrieve(retriever, args.query)
        for i, doc in enumerate(docs, 1):
            print(f"  [{i}] {doc.page_content[:200]}...")
        print()

    print("Teaching point: retrieval happens BEFORE the LLM sees anything.")


if __name__ == "__main__":
    main()
