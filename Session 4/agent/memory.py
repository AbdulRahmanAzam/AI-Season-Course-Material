"""
memory.py — Conversation history (short-term memory).

Keeps an in-memory list of messages. LLM ko poora history bhejte hain
har turn pe (this is the simplest form of "context window").

Note:
- Yahan koi summarization / RAG / vector search nahi hai.
- Persistent memory (file/DB) bhi nahi — session band hobe pe chali jayegi.
- Ye deliberate hai: rules of MVP.
"""

from __future__ import annotations

from typing import TypedDict


class Message(TypedDict):
    """Single message in conversation. Matches OpenAI chat format."""
    role: str        # "system" | "user" | "assistant"
    content: str     # message text


def init_history(system_prompt: str) -> list[Message]:
    """Start a fresh conversation with a system prompt."""
    return [{"role": "system", "content": system_prompt}]


def add_user(history: list[Message], text: str) -> None:
    history.append({"role": "user", "content": text})


def add_assistant(history: list[Message], text: str) -> None:
    history.append({"role": "assistant", "content": text})


def last_user(history: list[Message]) -> str:
    """Helper: get last user message (debugging / tests)."""
    for m in reversed(history):
        if m.get("role") == "user":
            return m.get("content", "")
    return ""
