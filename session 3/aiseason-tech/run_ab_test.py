"""
A/B test — evaluate answers WITH vs WITHOUT retrieved chunks.

Run from repo root:
  python aiseason-tech/run_ab_test.py
  python aiseason-tech/run_ab_test.py --strategy line
  python aiseason-tech/run_ab_test.py --compare-all
"""
import argparse
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from chatbot.config import CHUNKING_STRATEGIES, DEFAULT_TOP_K  # noqa: E402
from chatbot.evaluation import compare_chunking_strategies, run_full_evaluation  # noqa: E402
from chatbot.pipeline import ingest  # noqa: E402
from chatbot.vector_store import vector_store_exists  # noqa: E402


def ensure_index(strategy):
    if not vector_store_exists(strategy):
        print(f"Building index for '{strategy}'...\n")
        ingest(chunking_strategy=strategy)


def main():
    parser = argparse.ArgumentParser(description="A/B test: with vs without RAG context")
    parser.add_argument(
        "--strategy",
        default="recursive",
        choices=CHUNKING_STRATEGIES,
    )
    parser.add_argument("--top-k", type=int, default=DEFAULT_TOP_K)
    parser.add_argument(
        "--retrieval",
        default="similarity",
        choices=["similarity", "similarity_score_threshold", "mmr"],
    )
    parser.add_argument(
        "--compare-all",
        action="store_true",
        help="Run evaluation for every chunking strategy",
    )
    args = parser.parse_args()

    if args.compare_all:
        for strategy in CHUNKING_STRATEGIES:
            try:
                ensure_index(strategy)
            except Exception as exc:
                print(f"[SKIP] Could not index {strategy}: {exc}")
        compare_chunking_strategies(
            [s for s in CHUNKING_STRATEGIES if vector_store_exists(s)],
            top_k=args.top_k,
            retrieval_method=args.retrieval,
        )
        return

    ensure_index(args.strategy)
    run_full_evaluation(
        chunking_strategy=args.strategy,
        top_k=args.top_k,
        retrieval_method=args.retrieval,
    )


if __name__ == "__main__":
    main()
