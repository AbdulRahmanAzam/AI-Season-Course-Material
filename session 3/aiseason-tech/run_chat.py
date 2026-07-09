"""
Interactive chat — ask questions with RAG over AI Season data.

Run from repo root:
  python aiseason-tech/run_chat.py
  python aiseason-tech/run_chat.py --no-context
  python aiseason-tech/run_chat.py --strategy line --top-k 5
"""
import argparse
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from chatbot.config import CHUNKING_STRATEGIES, DEFAULT_TOP_K  # noqa: E402
from chatbot.llm import use_mock_llm  # noqa: E402
from chatbot.pipeline import ask, ingest  # noqa: E402
from chatbot.vector_store import vector_store_exists  # noqa: E402


def main():
    parser = argparse.ArgumentParser(description="AI Season RAG chatbot")
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
        "--no-context",
        action="store_true",
        help="Send question to LLM WITHOUT retrieved chunks (baseline)",
    )
    parser.add_argument("--question", default=None, help="Single question (non-interactive)")
    args = parser.parse_args()

    print("=== AI Season Chatbot ===\n")
    print(f"LLM: {'mock' if use_mock_llm() else 'groq'}")
    print(f"Chunking: {args.strategy} | top_k={args.top_k} | retrieval={args.retrieval}")
    print(f"Mode: {'WITHOUT context' if args.no_context else 'WITH retrieved context (RAG)'}\n")

    if not vector_store_exists(args.strategy):
        print(f"No index for '{args.strategy}'. Building now...\n")
        ingest(chunking_strategy=args.strategy)

    def run_question(q):
        result = ask(
            q,
            chunking_strategy=args.strategy,
            top_k=args.top_k,
            retrieval_method=args.retrieval,
            use_retrieved_context=not args.no_context,
        )

        print(f"Question: {result['question']}\n")

        if not args.no_context:
            print("--- Retrieved chunks ---")
            for i, doc in enumerate(result["retrieved_docs"], 1):
                print(f"[{i}] {doc.page_content[:200]}...")
            print()

        print("--- Answer ---")
        print(result["answer"])
        print("-" * 60)

    if args.question:
        run_question(args.question)
        return

    print("Type a question (or 'quit' to exit).\n")
    while True:
        try:
            question = input("You: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nBye.")
            break

        if not question:
            continue
        if question.lower() in {"quit", "exit", "q"}:
            print("Bye.")
            break

        run_question(question)
        print()


if __name__ == "__main__":
    main()
