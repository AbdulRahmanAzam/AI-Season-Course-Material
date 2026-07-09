"""
mistakes.py — Auto-detect mistakes from history + extract rules.

Detection sources:
  1. Verifier FAIL diagnostics (most reliable — coach verifier
     structured output already in history).
  2. Tool errors: [Tool Result] blocks containing [error] prefix
     or stack-trace keywords.
  3. User correction heuristics: short user messages containing
     push-back words ("no", "wrong", "actually", "instead", etc.).

Extraction:
  A single LLM call converts the detected mistakes into 1-3
  generalizable rule candidates (imperative, ≤200 chars, with
  "why" + category).

This is the "smart" half of the ratchet. Manual entry via
/log_mistake <text> still works as a fallback.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass

from agent import llm


@dataclass
class Mistake:
    """One detected mistake event from history."""
    source: str          # "verifier_fail" | "tool_error" | "user_correction"
    snippet: str         # short excerpt (≤400 chars)
    why: str             # brief explanation for extraction prompt


# ────────────────────────────────────────────────────────────────────
# Detection patterns
# ────────────────────────────────────────────────────────────────────

# Tool-result error markers. Subprocess / read_file / etc. signal errors
# with [error] prefix or traceback lines.
_ERROR_PREFIX_RE = re.compile(
    r"\[error\]|\bTraceback \(most recent call last\)|\bUnicodeDecodeError"
    r"|\bFileNotFoundError\b|\bPermissionError\b|\bTimeoutExpired\b",
)

# User push-back heuristics. Conservative — only short messages count,
# to avoid false positives on long instructions.
_USER_CORRECTION_RE = re.compile(
    r"^\s*(no|wrong|actually|instead|not what|i meant|incorrect|nah|nope"
    r"|that'?s not|not right)\b",
    re.IGNORECASE,
)


def detect_mistakes(history: list[dict], max_recent: int = 12) -> list[Mistake]:
    """Scan the last `max_recent` messages for mistake signals.

    Returns a de-duplicated list (oldest first within the slice).
    """
    mistakes: list[Mistake] = []
    recent = history[-max_recent:]

    for msg in recent:
        role = msg.get("role")
        content = msg.get("content", "")
        if role not in ("user", "assistant"):
            continue

        # ── Verifier coach-feedback block ─────────────────────────
        if role == "user" and "Verifier feedback" in content:
            m = re.search(r"Diagnosis:\s*(.+?)(?:\n|$)", content, re.DOTALL)
            if m:
                diag = m.group(1).strip()[:400]
                mistakes.append(Mistake(
                    source="verifier_fail",
                    snippet=diag,
                    why=f"Verifier rejected work: {diag[:120]}",
                ))

        # ── Tool errors in [Tool Result for X] blocks ──────────────
        if role == "user" and content.startswith("[Tool Result"):
            if _ERROR_PREFIX_RE.search(content):
                first_line = content.splitlines()[0][:120]
                mistakes.append(Mistake(
                    source="tool_error",
                    snippet=content[:400],
                    why=f"Tool returned an error: {first_line}",
                ))

        # ── User push-back (only short corrections) ────────────────
        if role == "user":
            stripped = content.strip()
            if (
                len(stripped) <= 200
                and len(stripped) >= 3
                and _USER_CORRECTION_RE.match(stripped)
                and "Verifier feedback" not in stripped      # not our own feedback
                and "[Tool Result" not in stripped           # not a tool result echoed back
            ):
                mistakes.append(Mistake(
                    source="user_correction",
                    snippet=stripped[:200],
                    why=f"User pushed back: {stripped[:80]!r}",
                ))

    # Dedupe by snippet — same mistake captured twice -> keep one.
    seen: set[str] = set()
    deduped: list[Mistake] = []
    for m in mistakes:
        if m.snippet in seen:
            continue
        seen.add(m.snippet)
        deduped.append(m)
    return deduped


# ────────────────────────────────────────────────────────────────────
# Extraction — LLM call converts mistakes → rule candidates
# ────────────────────────────────────────────────────────────────────

_EXTRACTION_PROMPT = """\
You are a rule-extractor for an AI agent harness. Given a list of
mistakes the agent made recently, produce 1-3 GENERALIZABLE rules
that would prevent the same mistake in future sessions.

Each rule must:
- Be specific and actionable (not vague like "be more careful")
- Use imperative voice ("Use X", "Avoid Y", "When Z, do W")
- Be tied to a CAUSE the agent can avoid next time
- Be a single sentence, ≤200 characters

INPUT (mistakes from recent history):
{mistakes_json}

OUTPUT — strict JSON, no prose, no markdown fences, no commentary:
{{
  "rules": [
    {{
      "text": "<imperative, single sentence, ≤200 chars>",
      "why": "<one-line trigger description>",
      "category": "<one of: tool_usage, verification, vague_tasks, prompt_injection, permission, general>"
    }}
  ]
}}

If the mistakes don't generalize (e.g. one-off typos), return
{{"rules": []}}.
Return ONLY the JSON object.
"""


def extract_rules(mistakes: list[Mistake]) -> list[dict]:
    """Meta-LLM call: detected mistakes → rule candidates.

    Each returned dict has keys: text (str), why (str), category (str).
    Returns [] if no clear rule emerges.
    """
    if not mistakes:
        return []

    payload = [
        {"source": m.source, "why": m.why, "snippet": m.snippet}
        for m in mistakes
    ]
    mistakes_json = json.dumps(payload, indent=2)

    prompt = _EXTRACTION_PROMPT.format(mistakes_json=mistakes_json)
    raw = llm.chat(
        messages=[{"role": "user", "content": prompt}],
        plan_mode=True,    # JSON-only, no tools
    )
    try:
        parsed = json.loads(raw)
    except json.JSONDecodeError:
        return []

    candidates = parsed.get("rules") or []
    if not isinstance(candidates, list):
        return []

    valid: list[dict] = []
    for c in candidates:
        if not isinstance(c, dict):
            continue
        text = str(c.get("text", "")).strip()
        if not text or len(text) > 300:
            continue
        valid.append({
            "text": text,
            "why": str(c.get("why", "")).strip(),
            "category": str(c.get("category", "general")).strip() or "general",
        })
    return valid
