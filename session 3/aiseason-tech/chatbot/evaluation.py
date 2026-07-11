"""
A/B evaluation — compare answers WITH vs WITHOUT retrieved chunks.

Also scores answers against expected keywords from the knowledge base.
"""
from .llm import use_mock_llm
from .pipeline import ask


# Ground-truth test cases derived from ai-season.txt
TEST_CASES = [
    {
        "question": "What is AI Season?",
        "expected_keywords": ["bootcamp", "ai agents", "agentic"],
    },
    {
        "question": "Who teaches AI Season?",
        "expected_keywords": ["abdul rahman azam", "founder", "instructor"],
    },
    {
        "question": "What is the early-bird price of AI Season?",
        "expected_keywords": ["2,250", "2250", "pkr"],
    },
    {
        "question": "When does the first cohort start?",
        "expected_keywords": ["july", "2026", "1st"],
    },
    {
        "question": "How long is the AI Season program?",
        "expected_keywords": ["6 weeks", "18"],
    },
    {
        "question": "Does AI Season teach RAG?",
        "expected_keywords": ["rag", "retrieval"],
    },
    {
        "question": "Is AI Season taught in Urdu?",
        "expected_keywords": ["urdu", "english"],
    },
    {
        "question": "What is the capital of France?",
        "expected_keywords": ["don't have", "do not have", "not enough", "don't know", "do not know"],
        "out_of_scope": True,
    },
]


def score_answer(answer, expected_keywords):
    """
    Simple keyword overlap score (0.0 - 1.0).
    Returns fraction of expected keywords found in the answer.
    """
    answer_lower = answer.lower()
    if not expected_keywords:
        return 0.0

    hits = sum(1 for kw in expected_keywords if kw.lower() in answer_lower)
    return hits / len(expected_keywords)


def run_single_ab_test(
    test_case,
    chunking_strategy="recursive",
    top_k=3,
    retrieval_method="similarity",
):
    """Run one question in both modes and return comparison."""
    question = test_case["question"]
    keywords = test_case.get("expected_keywords", [])

    with_rag = ask(
        question,
        chunking_strategy=chunking_strategy,
        top_k=top_k,
        retrieval_method=retrieval_method,
        use_retrieved_context=True,
    )
    without_rag = ask(
        question,
        chunking_strategy=chunking_strategy,
        top_k=top_k,
        retrieval_method=retrieval_method,
        use_retrieved_context=False,
    )

    return {
        "question": question,
        "expected_keywords": keywords,
        "out_of_scope": test_case.get("out_of_scope", False),
        "with_context": {
            "answer": with_rag["answer"],
            "score": score_answer(with_rag["answer"], keywords),
            "num_chunks": len(with_rag["retrieved_docs"]),
        },
        "without_context": {
            "answer": without_rag["answer"],
            "score": score_answer(without_rag["answer"], keywords),
        },
    }


def run_full_evaluation(
    chunking_strategy="recursive",
    top_k=3,
    retrieval_method="similarity",
    test_cases=None,
):
    """Run all test cases and print a summary report."""
    cases = test_cases or TEST_CASES
    results = []

    print("=== A/B Evaluation: WITH context vs WITHOUT context ===\n")
    print(f"Chunking: {chunking_strategy} | top_k={top_k} | retrieval={retrieval_method}")
    print(f"LLM mode: {'mock' if use_mock_llm() else 'groq'}\n")

    for i, case in enumerate(cases, 1):
        result = run_single_ab_test(
            case,
            chunking_strategy=chunking_strategy,
            top_k=top_k,
            retrieval_method=retrieval_method,
        )
        results.append(result)

        print(f"--- Test {i}: {result['question']} ---")
        print(f"  WITH context    (score={result['with_context']['score']:.2f}, "
              f"chunks={result['with_context']['num_chunks']}):")
        print(f"    {result['with_context']['answer'][:300]}")
        print(f"  WITHOUT context (score={result['without_context']['score']:.2f}):")
        print(f"    {result['without_context']['answer'][:300]}")
        print()

    avg_with = sum(r["with_context"]["score"] for r in results) / len(results)
    avg_without = sum(r["without_context"]["score"] for r in results) / len(results)

    print("=" * 60)
    print("SUMMARY")
    print(f"  Average keyword score WITH context:    {avg_with:.2f}")
    print(f"  Average keyword score WITHOUT context: {avg_without:.2f}")
    print(f"  RAG improvement:                       {avg_with - avg_without:+.2f}")
    print("=" * 60)

    return results


def compare_chunking_strategies(
    strategies,
    top_k=3,
    retrieval_method="similarity",
    test_cases=None,
):
    """Compare multiple chunking strategies using the A/B test."""
    cases = test_cases or TEST_CASES
    summary = {}

    print("=== Chunking Strategy Comparison ===\n")

    for strategy in strategies:
        results = run_full_evaluation(
            chunking_strategy=strategy,
            top_k=top_k,
            retrieval_method=retrieval_method,
            test_cases=cases,
        )
        avg_with = sum(r["with_context"]["score"] for r in results) / len(results)
        avg_without = sum(r["without_context"]["score"] for r in results) / len(results)
        summary[strategy] = {"with_context": avg_with, "without_context": avg_without}

    print("\n=== CHUNKING COMPARISON TABLE ===")
    print(f"{'Strategy':<30} {'With Ctx':>10} {'Without':>10} {'Delta':>10}")
    print("-" * 62)
    for strategy, scores in summary.items():
        delta = scores["with_context"] - scores["without_context"]
        print(
            f"{strategy:<30} {scores['with_context']:>10.2f} "
            f"{scores['without_context']:>10.2f} {delta:>+10.2f}"
        )

    return summary
