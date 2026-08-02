"""
Demo 1 — Honest RAG: Naive vs Loop
====================================

WHAT THIS PROVES:
  Mode A  → retrieve once, answer immediately  (often wrong + confident)
  Mode B  → retrieve → generate → EVALUATE → retry  (production pattern)

RUN:
  python demo1_honest_rag.py
  python demo1_honest_rag.py --mode naive
  python demo1_honest_rag.py --mode loop

COST: ~$0.01–0.02 per run (gpt-4o-mini)
"""

from __future__ import annotations


# ══════════════════════════════════════════════════════════════════════════════
# SECTION 1 — IMPORTS
# ══════════════════════════════════════════════════════════════════════════════

import argparse
import json
import re
import sys
import textwrap
from pathlib import Path

import chromadb
from openai import OpenAI

from config import (
    CHROMA_DIR,
    DATA_DIR,
    EMBEDDING_MODEL,
    MAX_LOOP_STEPS,
    MAX_OUTPUT_TOKENS,
    MODEL,
    TEMPERATURE,
)


# ══════════════════════════════════════════════════════════════════════════════
# SECTION 2 — CONFIG (change this question live if you want)
# ══════════════════════════════════════════════════════════════════════════════

QUESTION = (
    "How many remote days per week can "
    "a junior engineer work from home?"
)


# ══════════════════════════════════════════════════════════════════════════════
# SECTION 3 — DATA LOADING
# Load HR policy chunks. One chunk is intentionally ARCHIVED (the trap).
# ══════════════════════════════════════════════════════════════════════════════

def load_policy_chunks() -> list[dict]:
    """Read hr_policy.md and split into indexed chunks."""

    raw = (DATA_DIR / "hr_policy.md").read_text(encoding="utf-8")

    blocks = [
        b.strip()
        for b in raw.split("---")
        if b.strip() and "POLICY-" in b
    ]

    chunks = []

    for i, block in enumerate(blocks):

        policy_id = re.search(r"POLICY-[\w-]+", block)

        chunks.append({
            "id": policy_id.group(0) if policy_id else f"chunk-{i}",
            "text": block,
            "archived": "ARCHIVED" in block or "Superseded" in block,
        })

    return chunks


# ══════════════════════════════════════════════════════════════════════════════
# SECTION 4 — EMBEDDINGS + VECTOR STORE (ChromaDB)
# ══════════════════════════════════════════════════════════════════════════════

def embed_texts(client: OpenAI, texts: list[str]) -> list[list[float]]:
    """Turn text into vectors using OpenAI embeddings."""

    resp = client.embeddings.create(
        model=EMBEDDING_MODEL,
        input=texts,
    )

    return [item.embedding for item in resp.data]


def build_vector_store(
    client: OpenAI,
    chunks: list[dict],
) -> chromadb.Collection:
    """Index all policy chunks into Chroma for similarity search."""

    CHROMA_DIR.mkdir(exist_ok=True)

    db = chromadb.PersistentClient(path=str(CHROMA_DIR))

    # Fresh index each run (keeps demo predictable)
    try:
        db.delete_collection("hr_policy")
    except Exception:
        pass

    collection = db.create_collection("hr_policy")

    embeddings = embed_texts(client, [c["text"] for c in chunks])

    collection.add(
        ids=[c["id"] for c in chunks],
        documents=[c["text"] for c in chunks],
        embeddings=embeddings,
        metadatas=[{"archived": c["archived"]} for c in chunks],
    )

    return collection


# ══════════════════════════════════════════════════════════════════════════════
# SECTION 5 — RETRIEVE (RAG step 1)
# ══════════════════════════════════════════════════════════════════════════════

def retrieve(
    collection: chromadb.Collection,
    client: OpenAI,
    query: str,
    k: int = 2,
):
    """Find top-k policy chunks closest to the question."""

    q_emb = embed_texts(client, [query])[0]

    result = collection.query(
        query_embeddings=[q_emb],
        n_results=k,
    )

    docs = result["documents"][0]
    ids = result["ids"][0]
    metas = result["metadatas"][0]

    return list(zip(ids, docs, metas))


# ══════════════════════════════════════════════════════════════════════════════
# SECTION 6 — LLM CALL (shared helper)
# ══════════════════════════════════════════════════════════════════════════════

def llm(client: OpenAI, system: str, user: str) -> str:
    """Single chat completion — kept small for $5 budget."""

    resp = client.chat.completions.create(
        model=MODEL,
        temperature=TEMPERATURE,
        max_tokens=MAX_OUTPUT_TOKENS,
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
    )

    return resp.choices[0].message.content or ""


# ══════════════════════════════════════════════════════════════════════════════
# SECTION 7 — MODE A: NAIVE RAG  ❌  (no loop, no verify)
#
#   FLOW:  retrieve → answer → DONE
#
#   PROBLEM: may grab archived/wrong chunk and sound confident
# ══════════════════════════════════════════════════════════════════════════════

def demo_naive(
    client: OpenAI,
    collection: chromadb.Collection,
) -> None:

    print("\n" + "=" * 60)
    print("MODE A — NAIVE RAG")
    print("(retrieve once → answer → no verification)")
    print("=" * 60)

    # ── Step A1: Retrieve only ONE chunk ─────────────────────────────────────
    hits = retrieve(collection, client, QUESTION, k=1)

    chunk_id, chunk_text, meta = hits[0]

    print(f"\n[retrieve] Chunk used: {chunk_id}")
    print(f"[retrieve] Archived?  {meta['archived']}")
    print(textwrap.indent(chunk_text[:280] + "...", "  "))

    # ── Step A2: Generate answer immediately ─────────────────────────────────
    answer = llm(
        client,
        system="You are an HR assistant. Answer using ONLY the provided policy text.",
        user=f"Policy:\n{chunk_text}\n\nQuestion: {QUESTION}",
    )

    print(f"\n[answer]\n{textwrap.indent(answer.strip(), '  ')}")

    # ── Step A3: No evaluate step — that's the bug ───────────────────────────
    print(
        "\n⚠️  PROBLEM: Confident answer, zero evidence check. "
        "May cite wrong or ARCHIVED policy."
    )


# ══════════════════════════════════════════════════════════════════════════════
# SECTION 8 — HELPER: parse evaluator JSON
# ══════════════════════════════════════════════════════════════════════════════

def parse_json_block(text: str) -> dict:
    """Extract JSON verdict from evaluator LLM output."""

    match = re.search(r"\{.*\}", text, re.DOTALL)

    if not match:
        return {"supported": False, "reason": "Could not parse evaluator output"}

    try:
        return json.loads(match.group(0))
    except json.JSONDecodeError:
        return {"supported": False, "reason": "Invalid JSON from evaluator"}


# ══════════════════════════════════════════════════════════════════════════════
# SECTION 9 — MODE B: LOOP RAG  ✅  (production pattern)
#
#   FLOW:  retrieve → generate → EVALUATE → retry OR stop
#
#   THIS IS LOOP ENGINEERING — the evaluate step is the product
# ══════════════════════════════════════════════════════════════════════════════

def demo_loop(
    client: OpenAI,
    collection: chromadb.Collection,
) -> None:

    print("\n" + "=" * 60)
    print("MODE B — LOOP RAG")
    print("(retrieve → generate → evaluate → retry)")
    print("=" * 60)

    query = QUESTION
    final_answer = ""

    # ── THE LOOP ─────────────────────────────────────────────────────────────
    for step in range(1, MAX_LOOP_STEPS + 1):

        print(f"\n--- Loop step {step} / {MAX_LOOP_STEPS} ---")

        # ── Step B1: RETRIEVE ────────────────────────────────────────────────
        hits = retrieve(collection, client, query, k=3)

        # Prefer current (non-archived) policies when displaying
        hits = sorted(hits, key=lambda h: h[2].get("archived", False))

        context = "\n\n".join(f"[{cid}]\n{doc}" for cid, doc, _ in hits)

        print(f"[retrieve] Query:   {query!r}")
        print(f"[retrieve] Chunks:  {[h[0] for h in hits]}")

        # ── Step B2: GENERATE draft answer ───────────────────────────────────
        draft = llm(
            client,
            system=(
                "You are an HR assistant. Answer ONLY from the policy excerpts. "
                "Cite policy IDs like [POLICY-2024-001]. "
                "If evidence is insufficient, say so."
            ),
            user=f"Policies:\n{context}\n\nQuestion: {QUESTION}",
        )

        print(f"[generate]\n{textwrap.indent(draft.strip(), '  ')}")

        # ── Step B3: EVALUATE — does the answer have real evidence? ──────────
        eval_raw = llm(
            client,
            system=(
                "You are a strict RAG evaluator. Return ONLY JSON:\n"
                '{"supported": true/false, "reason": "...", "retry_query": "..."}\n'
                "supported=false if answer uses archived policy, contradicts excerpts, "
                "or lacks citation to a current policy."
            ),
            user=(
                f"Question: {QUESTION}\n\n"
                f"Policies:\n{context}\n\n"
                f"Draft answer:\n{draft}"
            ),
        )

        verdict = parse_json_block(eval_raw)

        print(f"[evaluate] {verdict}")

        # ── Step B4: DECIDE — stop, retry, or fallback ───────────────────────
        if verdict.get("supported"):

            final_answer = draft

            print(f"\n✅ Loop STOPPED — evidence verified at step {step}")
            break

        # Rewrite query for next retrieval attempt
        query = verdict.get("retry_query") or (
            QUESTION + " current official policy not archived"
        )

        if step == MAX_LOOP_STEPS:

            final_answer = (
                "I don't have enough verified policy evidence to answer confidently. "
                "Please check with HR directly."
            )

            print("\n🛑 Max loops reached — safe fallback (refuse to guess)")

    print(f"\n[final answer]\n{textwrap.indent(final_answer.strip(), '  ')}")


# ══════════════════════════════════════════════════════════════════════════════
# SECTION 10 — MAIN
# ══════════════════════════════════════════════════════════════════════════════

def main() -> int:

    parser = argparse.ArgumentParser(description="Honest RAG demo")

    parser.add_argument(
        "--mode",
        choices=["both", "naive", "loop"],
        default="both",
        help="Which demo to run",
    )

    args = parser.parse_args()

    # ── Guard: API key must exist ────────────────────────────────────────────
    if not Path(".env").exists() and not __import__("os").environ.get("OPENAI_API_KEY"):
        print("Missing OPENAI_API_KEY. Copy .env.example → .env and add your key.")
        return 1

    client = OpenAI()

    # ── Setup: load data + build vector index ─────────────────────────────────
    chunks = load_policy_chunks()

    print(f"Loaded {len(chunks)} policy chunks")
    print(f"Model:      {MODEL}")
    print(f"Embeddings: {EMBEDDING_MODEL}")
    print(f"Question:   {QUESTION}")

    collection = build_vector_store(client, chunks)

    # ── Run selected mode(s) ─────────────────────────────────────────────────
    if args.mode in ("both", "naive"):
        demo_naive(client, collection)

    if args.mode in ("both", "loop"):
        demo_loop(client, collection)

    print("\n" + "-" * 60)
    print("Teaching point: Production RAG adds an EVALUATE step in the loop.")
    print("-" * 60)

    return 0


if __name__ == "__main__":
    sys.exit(main())
