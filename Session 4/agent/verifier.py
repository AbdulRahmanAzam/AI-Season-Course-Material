"""
verifier.py — Coach-style verifier for completed agent work.

The verifier is a SEPARATE LLM call that judges whether the agent
actually achieved the user's goal. It runs at logical endpoints:
  - After a plan completes (all steps executed).
  - After a single task gives its final answer.

The verifier acts as a COACH, not just a gatekeeper: when it returns
FAIL, it provides:
  - diagnosis    → what's wrong, tied to the goal
  - missing      → concrete list of what's absent
  - suggested_actions → concrete next steps for the agent

This richer feedback gets injected into history so the next attempt
has an actionable playbook, not just "try again".

Output schema (matches _VERIFIER_PROMPT):
  {
    "verdict": "pass" | "fail",
    "diagnosis": "<paragraph>",
    "missing": ["<item>", ...],
    "suggested_actions": ["<step>", ...]
  }
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import Callable

from agent import llm


@dataclass
class Verdict:
    """Structured verifier output.

    A "coach" verdict: not just pass/fail, but actionable guidance.
    """
    passed: bool
    diagnosis: str = ""
    missing: list[str] = field(default_factory=list)
    suggested_actions: list[str] = field(default_factory=list)
    raw: str = ""

    # Convenience: one-line summary for logs/UX.
    @property
    def reason(self) -> str:
        if self.passed:
            return self.diagnosis or "passed"
        return self.diagnosis or (self.missing[0] if self.missing else "failed")

    def __bool__(self) -> bool:
        return self.passed

    def to_feedback_message(self) -> str:
        """Format the verdict as a rich user-role message for the agent.

        On PASS, returns a brief confirmation (rarely used since callers
        usually short-circuit on pass).
        On FAIL, returns a structured "coach" message with diagnosis,
        missing items, and concrete next steps.
        """
        if self.passed:
            return "[Verifier] Goal achieved. No further action needed."

        lines = ["[Verifier feedback — coach mode]"]

        if self.diagnosis:
            lines.append("")
            lines.append(f"Diagnosis: {self.diagnosis}")

        if self.missing:
            lines.append("")
            lines.append("Missing (concrete gaps):")
            for i, m in enumerate(self.missing, 1):
                lines.append(f"  {i}. {m}")

        if self.suggested_actions:
            lines.append("")
            lines.append("Suggested next actions (do these in order):")
            for i, a in enumerate(self.suggested_actions, 1):
                lines.append(f"  {i}. {a}")

        lines.append("")
        lines.append(
            "Address each missing item by following the suggested actions. "
            "Use tools (read_file, write_file, edit_file, bash) — do NOT just "
            "describe. When the work is genuinely complete, return final "
            "with a one-line summary of what was done."
        )

        return "\n".join(lines)


def _parse_verdict(raw_action_json: str) -> Verdict:
    """Parse the verifier's JSON output into a Verdict.

    Primary schema (new — coach mode):
      {
        "verdict": "pass" | "fail",
        "diagnosis": "...",
        "missing": [...],
        "suggested_actions": [...]
      }

    Backward-compat: if the verifier returns the legacy
      {"action": "plan", "steps": ["VERDICT: FAIL — reason"]}
    format, we extract the reason into diagnosis so the system still works.
    """
    try:
        action = json.loads(raw_action_json)
    except json.JSONDecodeError:
        return Verdict(
            passed=False,
            diagnosis="verifier returned non-JSON",
            raw=raw_action_json,
        )

    # ── Primary schema ────────────────────────────────────────
    verdict_str = str(action.get("verdict", "")).lower().strip()
    if verdict_str in ("pass", "fail"):
        return Verdict(
            passed=(verdict_str == "pass"),
            diagnosis=str(action.get("diagnosis", "")).strip(),
            missing=list(action.get("missing") or []),
            suggested_actions=list(action.get("suggested_actions") or []),
            raw=raw_action_json,
        )

    # ── Backward compat: old "VERDICT: PASS|FAIL — reason" format ──
    steps = action.get("steps") or []
    if steps:
        head = str(steps[0]).strip()
        if head.upper().startswith("VERDICT: PASS"):
            return Verdict(
                passed=True,
                diagnosis="passed (legacy format)",
                raw=raw_action_json,
            )
        if head.upper().startswith("VERDICT: FAIL"):
            reason = head[len("VERDICT: FAIL"):].lstrip(" —:-").strip()
            return Verdict(
                passed=False,
                diagnosis=reason or "(no reason given)",
                missing=[reason] if reason else [],
                raw=raw_action_json,
            )

    # ── Unknown shape ──────────────────────────────────────────
    return Verdict(
        passed=False,
        diagnosis=f"verifier returned unrecognized verdict shape: {raw_action_json[:200]}",
        raw=raw_action_json,
    )


def _format_evidence(history: list[dict], limit_chars: int = 6000) -> str:
    """Render the conversation history as a compact evidence string.

    We skip the system message and keep recent turns so the verifier
    sees both the goal and the work done. The limit prevents blowing
    past the context window on long plans.
    """
    lines = []
    total = 0
    for m in history:
        role = m.get("role", "?")
        content = m.get("content", "")
        if role == "system":
            continue
        line = f"[{role}] {content}"
        if total + len(line) > limit_chars:
            lines.append("... (truncated for length)")
            break
        lines.append(line)
        total += len(line)
    return "\n\n".join(lines)


def verify(
    goal: str,
    history: list[dict],
    emit: Callable[[str], None] | None = None,
) -> Verdict:
    """Single LLM call judging whether `goal` was achieved by the work
    captured in `history`. Returns a rich coach Verdict.

    Args:
        goal: the original user request (or, in plan mode, the goal the
              approved plan was meant to achieve).
        history: full conversation history including tool calls, tool
                 results, and any final answer the agent produced.
        emit: optional output sink (used to print verifier activity).

    Returns:
        Verdict(passed, diagnosis, missing, suggested_actions, raw).
    """
    evidence = _format_evidence(history)

    user_prompt = (
        f"GOAL (what the user asked for):\n{goal}\n\n"
        f"EVIDENCE (chronological transcript of the agent's work):\n"
        f"{evidence}\n\n"
        f"Now judge: did the work above genuinely achieve the goal?\n"
        f"Return ONLY the verdict JSON with diagnosis, missing, and "
        f"suggested_actions (even if PASS — diagnosis should explain why)."
    )

    if emit:
        emit("\n  ── Verifying ──")

    raw = llm.chat(
        messages=[{"role": "user", "content": user_prompt}],
        system="",
        verifier_mode=True,
    )

    verdict = _parse_verdict(raw)

    if emit:
        if verdict.passed:
            diagnosis_preview = (
                f" — {verdict.diagnosis}" if verdict.diagnosis else ""
            )
            emit(f"  ✓ Verifier: PASS{diagnosis_preview}\n")
        else:
            emit(f"  ✗ Verifier: FAIL — {verdict.diagnosis}\n")
            if verdict.missing:
                emit(f"    Missing: {len(verdict.missing)} item(s)\n")
            if verdict.suggested_actions:
                emit(f"    Suggestions: {len(verdict.suggested_actions)} step(s)\n")

    return verdict