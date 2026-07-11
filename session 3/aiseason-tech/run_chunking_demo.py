"""
Chunking demo — preview all non-LLM chunking strategies on ai-season.txt.

Run from repo root:
  python aiseason-tech/run_chunking_demo.py
  python aiseason-tech/run_chunking_demo.py --strategy line
"""
import argparse
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from chatbot.chunking import get_text_splitter, preview_chunks, split_documents  # noqa: E402
from chatbot.config import CHUNKING_STRATEGIES, DEFAULT_CHUNK_OVERLAP, DEFAULT_CHUNK_SIZE  # noqa: E402
from chatbot.file_loader import load_text_file, preview_documents  # noqa: E402


def demo_strategy(strategy, documents, chunk_size, chunk_overlap, max_preview=2):
    print(f"\n{'=' * 60}")
    print(f"=== {strategy.upper()} ===")
    print("=" * 60)

    try:
        chunks = split_documents(
            documents,
            strategy=strategy,
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
        )
        preview_chunks(chunks, max_chunks=max_preview)
        return len(chunks)
    except Exception as exc:
        print(f"[SKIP] {strategy}: {exc}")
        return None


def main():
    parser = argparse.ArgumentParser(description="Preview chunking strategies")
    parser.add_argument("--strategy", default=None, choices=CHUNKING_STRATEGIES)
    parser.add_argument("--chunk-size", type=int, default=DEFAULT_CHUNK_SIZE)
    parser.add_argument("--chunk-overlap", type=int, default=DEFAULT_CHUNK_OVERLAP)
    args = parser.parse_args()

    print("=== AI Season Chunking Demo ===\n")

    documents = load_text_file()
    preview_documents(documents)

    strategies = [args.strategy] if args.strategy else CHUNKING_STRATEGIES
    counts = {}

    for strategy in strategies:
        count = demo_strategy(
            strategy,
            documents,
            args.chunk_size,
            args.chunk_overlap,
        )
        if count is not None:
            counts[strategy] = count

    if len(counts) > 1:
        print(f"\n{'=' * 60}")
        print("CHUNK COUNT SUMMARY")
        print("=" * 60)
        for strategy, count in sorted(counts.items(), key=lambda x: x[1]):
            print(f"  {strategy:<30} {count:>6} chunks")

    print("\nTeaching point: chunking strategy affects retrieval quality.")


if __name__ == "__main__":
    main()
