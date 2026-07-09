"""
llm.py — Unified LLM interface (production version).

Routes to real_llm.chat() only. Mock has been removed (Checkpoint 4).

Single point of change = single source of truth for "what LLM does the agent use".
"""

from __future__ import annotations

from agent import real_llm


def chat(messages: list[dict], system: str = "", plan_mode: bool = False,
         verifier_mode: bool = False) -> str:
    """Send conversation history to LLM, get one action (JSON string).

    Args:
        messages: full conversation history.
        system: system prompt.
        plan_mode: when True, LLM returns a "plan" action instead of tool_call.
        verifier_mode: when True, LLM returns a verifier verdict (no tools).

    Returns:
        JSON string — tool_call, final, plan, or verifier verdict action.
    """
    return real_llm.chat(
        messages, system=system, plan_mode=plan_mode, verifier_mode=verifier_mode
    )
