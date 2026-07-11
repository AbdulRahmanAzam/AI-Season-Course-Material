"""
Ingestion — load ai-season.txt, chunk with every strategy, store in ChromaDB.

Run from repo root:
  python aiseason-tech/run_ingestion.py
  python aiseason-tech/run_ingestion.py --strategy recursive
  python aiseason-tech/run_ingestion.py --all
"""
import argparse
import os
import sys

# Allow imports from aiseason-tech/chatbot
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from chatbot.config import CHUNKING_STRATEGIES  # noqa: E402
from chatbot.pipeline import ingest  # noqa: E402


def main():
    parser = argparse.ArgumentParser(description="Ingest AI Season data into ChromaDB")
    parser.add_argument(
        "--strategy",
        default="recursive",
        choices=CHUNKING_STRATEGIES,
        help="Chunking strategy (default: recursive)",
    )
    parser.add_argument("--all", action="store_true", help="Ingest with every chunking strategy")
    parser.add_argument("--force", action="store_true", help="Rebuild even if store exists")
    parser.add_argument("--chunk-size", type=int, default=None)
    parser.add_argument("--chunk-overlap", type=int, default=None)
    args = parser.parse_args()

    print("=== AI Season Ingestion Pipeline ===\n")

    strategies = CHUNKING_STRATEGIES if args.all else [args.strategy]

    for strategy in strategies:
        print(f"\n{'=' * 60}")
        print(f"Strategy: {strategy}")
        print("=" * 60)
        try:
            ingest(
                chunking_strategy=strategy,
                chunk_size=args.chunk_size,
                chunk_overlap=args.chunk_overlap,
                force=args.force,
            )
        except Exception as exc:
            print(f"[SKIP] {strategy}: {exc}")

    print("\nIngestion complete. Run run_chat.py or run_ab_test.py next.")


if __name__ == "__main__":
    main()
