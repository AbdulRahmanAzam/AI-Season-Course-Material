"""
Demo 2 — Fix Until Tests Pass (Agent Eval Loop)
================================================

WHAT THIS PROVES:
  observe (pytest fail) → act (LLM patch) → evaluate (pytest) → repeat

  Same pattern as: Uber AutoCover, Karpathy autoresearch, Cursor agent

RUN:
  python demo2_fix_until_pass.py

COST: ~$0.01–0.03 per run (1–3 gpt-4o-mini calls)
"""

from __future__ import annotations


# ══════════════════════════════════════════════════════════════════════════════
# SECTION 1 — IMPORTS
# ══════════════════════════════════════════════════════════════════════════════

import shutil
import subprocess
import sys
import textwrap
from pathlib import Path

from openai import OpenAI

from config import MAX_LOOP_STEPS, MAX_OUTPUT_TOKENS, MODEL, ROOT, TEMPERATURE


# ══════════════════════════════════════════════════════════════════════════════
# SECTION 2 — PATHS
# ══════════════════════════════════════════════════════════════════════════════

BROKEN_DIR = ROOT / "demo2_broken"      # source: intentionally buggy code
WORK_DIR = ROOT / "demo2_workspace"      # copy: agent edits this each run


# ══════════════════════════════════════════════════════════════════════════════
# SECTION 3 — SETUP: reset workspace
# ══════════════════════════════════════════════════════════════════════════════

def reset_workspace() -> Path:
    """Copy fresh broken code into workspace before each demo."""

    if WORK_DIR.exists():
        shutil.rmtree(WORK_DIR)

    shutil.copytree(BROKEN_DIR, WORK_DIR)

    return WORK_DIR


# ══════════════════════════════════════════════════════════════════════════════
# SECTION 4 — EVALUATE: run pytest (this IS the loop's judge)
# ══════════════════════════════════════════════════════════════════════════════

def run_tests(work_dir: Path) -> tuple[bool, str]:
    """
    Run pytest. Returns:
      (True,  output)  if all tests pass
      (False, output)  if any test fails
    """

    proc = subprocess.run(
        [sys.executable, "-m", "pytest", "-q"],
        cwd=work_dir,
        capture_output=True,
        text=True,
    )

    output = (proc.stdout + proc.stderr).strip()

    return proc.returncode == 0, output


# ══════════════════════════════════════════════════════════════════════════════
# SECTION 5 — HELPER: pull code from LLM response
# ══════════════════════════════════════════════════════════════════════════════

def extract_python_code(text: str) -> str:
    """Extract ```python ... ``` block from agent response."""

    if "```python" in text:
        start = text.index("```python") + len("```python")
        end = text.index("```", start)
        return text[start:end].strip()

    if "```" in text:
        start = text.index("```") + 3
        end = text.index("```", start)
        return text[start:end].strip()

    return text.strip()


# ══════════════════════════════════════════════════════════════════════════════
# SECTION 6 — ACT: ask LLM to fix the code
# ══════════════════════════════════════════════════════════════════════════════

def ask_fix(
    client: OpenAI,
    source: str,
    test_output: str,
    step: int,
) -> str:
    """Send broken code + test errors to LLM. Get patched file back."""

    prompt = textwrap.dedent(f"""
        You are a coding agent in a fix-until-pass loop (step {step}).

        Fix calculator.py so ALL pytest tests pass.
        Return ONLY the full corrected calculator.py in one ```python block.
        Do NOT change test files.

        ── Current calculator.py ──
        ```python
        {source}
        ```

        ── Latest pytest output ──
        ```
        {test_output[-2000:]}
        ```
    """).strip()

    resp = client.chat.completions.create(
        model=MODEL,
        temperature=TEMPERATURE,
        max_tokens=MAX_OUTPUT_TOKENS,
        messages=[
            {
                "role": "system",
                "content": "You fix Python bugs iteratively. Output only code.",
            },
            {
                "role": "user",
                "content": prompt,
            },
        ],
    )

    return resp.choices[0].message.content or ""


# ══════════════════════════════════════════════════════════════════════════════
# SECTION 7 — MAIN AGENT LOOP
#
#   FLOW:
#     observe  → read test failures
#     act      → LLM writes patch
#     evaluate → run pytest again
#     decide   → pass? stop : loop (max 3)
#
# ══════════════════════════════════════════════════════════════════════════════

def main() -> int:

    # ── Guard: API key ───────────────────────────────────────────────────────
    if not Path(".env").exists() and not __import__("os").environ.get("OPENAI_API_KEY"):
        print("Missing OPENAI_API_KEY. Copy .env.example → .env and add your key.")
        return 1

    client = OpenAI()

    work_dir = reset_workspace()
    calc_path = work_dir / "calculator.py"

    print("=" * 60)
    print("DEMO 2 — Fix-until-pass agent loop")
    print("=" * 60)
    print(f"Model:     {MODEL}")
    print(f"Max loops: {MAX_LOOP_STEPS}")
    print(f"Workspace: {work_dir}\n")

    # ── Step 0: OBSERVE initial state ─────────────────────────────────────────
    passed, output = run_tests(work_dir)

    print("[observe] Initial pytest run:")
    print(textwrap.indent(output or "(no output)", "  "))

    if passed:
        print("\nTests already pass — reset workspace or re-copy broken files.")
        return 0

    # ── THE LOOP ─────────────────────────────────────────────────────────────
    for step in range(1, MAX_LOOP_STEPS + 1):

        print(f"\n--- Agent loop step {step} / {MAX_LOOP_STEPS} ---")

        # ── Step 1: READ current broken code ─────────────────────────────────
        source = calc_path.read_text(encoding="utf-8")

        # ── Step 2: ACT — LLM proposes a fix ─────────────────────────────────
        fix_raw = ask_fix(client, source, output, step)
        fixed_code = extract_python_code(fix_raw)

        calc_path.write_text(fixed_code + "\n", encoding="utf-8")

        print("[act]      Wrote patched calculator.py")

        # ── Step 3: EVALUATE — run tests again ───────────────────────────────
        passed, output = run_tests(work_dir)

        print("[observe]  pytest output:")
        print(textwrap.indent(output or "(no output)", "  "))

        # ── Step 4: DECIDE — stop or continue ────────────────────────────────
        if passed:

            print(f"\n✅ SUCCESS — all tests passed at loop step {step}")

            print("\nFinal calculator.py:")
            print(textwrap.indent(calc_path.read_text(encoding="utf-8"), "  "))

            return 0

        print("[evaluate] Still failing → next loop iteration...")

    # ── Fallback: max loops hit → human-in-the-loop ──────────────────────────
    print(
        f"\n🛑 Stopped after {MAX_LOOP_STEPS} loops. "
        "Time for human-in-the-loop!"
    )

    return 1


if __name__ == "__main__":
    sys.exit(main())
