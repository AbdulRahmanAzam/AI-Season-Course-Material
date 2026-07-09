"""
safety.py — Pattern-based command classification for bash tool.

Three tiers:
    ALLOW  — Read-only / safe commands. Run silently.
    WARN   — Mutating commands. Ask user for permission first.
    BLOCK  — Destructive commands. Refuse always.

Patterns are pure data (list of regex strings) so they're easy to extend.
A command is classified by:
    1. If it matches any BLOCK pattern → BLOCK.
    2. Else if it matches any WARN pattern → WARN.
    3. Else if it matches only ALLOW patterns (or none of WARN/BLOCK) → ALLOW.

Note: classifier prefers BLOCK over WARN over ALLOW — i.e. specific dangerous
patterns always win over general allowlist matches.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Iterable


# ─────────────────────────────────────────────────────────
# Pattern lists — extend these as needed.
# ─────────────────────────────────────────────────────────

# Read-only commands — safe to run without asking.
# Anchored at start of command. Use \b for word boundaries where useful.
_ALLOW_PATTERNS: list[str] = [
    r"^\s*ls\b",
    r"^\s*cat\b",
    r"^\s*less\b",
    r"^\s*more\b",
    r"^\s*head\b",
    r"^\s*tail\b",
    r"^\s*pwd\b",
    r"^\s*echo\b",
    r"^\s*printf\b",
    r"^\s*grep\b",
    r"^\s*find\b",
    r"^\s*tree\b",
    r"^\s*wc\b",
    r"^\s*file\b",
    r"^\s*stat\b",
    r"^\s*which\b",
    r"^\s*whoami\b",
    r"^\s*date\b",
    r"^\s*df\b",          # disk free (read-only)
    r"^\s*du\b",          # disk usage (read-only on dirs)
    r"^\s*ps\b",
    r"^\s*env\b",
    r"^\s*uname\b",
    r"^\s*git\s+(status|log|diff|show|branch|remote|config)\b",
    r"^\s*python\s+(-c|-m|\S+\.py)\b",   # running scripts
    r"^\s*pytest\b",
    r"^\s*pip\s+(list|show|freeze)\b",
]

# Mutating commands — ask user first.
_WARN_PATTERNS: list[str] = [
    r"\brm\b",                  # any rm
    r"\bmv\b",
    r"\bcp\b",
    r"\bmkdir\b",
    r"\btouch\b",
    r"\bchmod\b",
    r"\bchown\b",
    r"\bchgrp\b",
    r"\bcurl\b",
    r"\bwget\b",
    r"\bapt(-get)?\s+install\b",
    r"\bpip\s+install\b",
    r"\bnpm\s+(install|i)\b",
    r"\byarn\s+(install|add)\b",
    r"\bgit\s+(commit|push|pull|fetch|merge|rebase|reset|checkout|stash|add)\b",
    r"\bpython\s+-m\s+pip\b",
    r"\bnode\s+\S*\.js\b",
    r"\b&\s*&\s*",              # background chaining (often used in exploits)
    r"\|\s*sh\b",                # piping to shell
    r"\|\s*bash\b",
    r"\bsudo\b",
]

# Destructive patterns — always refused.
_BLOCK_PATTERNS: list[str] = [
    # rm -rf / or rm -fr / (with or without trailing space)
    r"rm\s+(-[a-zA-Z]*[rf][a-zA-Z]*\s+)+/\s*$",
    r"rm\s+(-[a-zA-Z]*[rf][a-zA-Z]*\s+)+/\w",          # rm -rf /home, /etc, /var, etc.
    r"\bmkfs(\.\w+)?\b",         # mkfs, mkfs.ext4, etc.
    r"\bdd\s+.*of=/dev/",         # dd writing to device
    r"\b(shutdown|reboot|halt|poweroff)\b",
    r":\(\)\s*\{",                # fork bomb
    r">\s*/dev/sd[a-z]",          # redirect to disk device
    r"\bchmod\s+(-R\s+)?777\s+/\s*$",
    r"\bchmod\s+(-R\s+)?777\s+/\w",  # chmod 777 /something
    r"\bsudo\s+rm\b",
]


# ─────────────────────────────────────────────────────────
# Classification result
# ─────────────────────────────────────────────────────────

@dataclass(frozen=True)
class Classification:
    tier: str           # "allow" | "warn" | "block"
    matched: str       # the pattern that matched (for diagnostics)
    reason: str        # human-readable explanation


def _matches_any(patterns: Iterable[str], command: str) -> str | None:
    """Return first matching pattern, or None."""
    for pat in patterns:
        if re.search(pat, command):
            return pat
    return None


def classify(command: str) -> Classification:
    """Classify a shell command into allow / warn / block.

    Order of precedence: BLOCK > WARN > ALLOW.
    A command that matches both a BLOCK and an ALLOW pattern is BLOCKED
    (specific dangerous patterns always win).
    """
    block_match = _matches_any(_BLOCK_PATTERNS, command)
    if block_match:
        return Classification(
            tier="block",
            matched=block_match,
            reason="destructive pattern detected",
        )

    warn_match = _matches_any(_WARN_PATTERNS, command)
    if warn_match:
        return Classification(
            tier="warn",
            matched=warn_match,
            reason="mutating command requires user approval",
        )

    allow_match = _matches_any(_ALLOW_PATTERNS, command)
    if allow_match:
        return Classification(
            tier="allow",
            matched=allow_match,
            reason="safe read-only command",
        )

    # Unknown command — default to WARN (ask user). Better safe than sorry.
    return Classification(
        tier="warn",
        matched="",
        reason="command not in allowlist; defaulting to ask",
    )


# ─────────────────────────────────────────────────────────
# Permission prompt flow
# ─────────────────────────────────────────────────────────

def format_prompt(command: str, classification: Classification) -> str:
    """Build the user-facing permission prompt."""
    cmd_preview = command if len(command) <= 80 else command[:77] + "..."
    return (
        f"\n  ⚠ Permission needed [{classification.tier.upper()}]\n"
        f"  Reason: {classification.reason}\n"
        f"  Pattern: {classification.matched or '(unknown)'}\n"
        f"  Command: {cmd_preview}\n"
        f"  Allow? [y/n/a]: "
    )


def parse_permission_response(response: str) -> str:
    """Parse user's reply. Returns one of: 'allow', 'deny', 'always'.

    'a' means "always allow this exact command for the rest of the session".
    """
    r = response.strip().lower()
    if r in ("y", "yes"):
        return "allow"
    if r in ("a", "always"):
        return "always"
    # default to deny (safer)
    return "deny"


def format_block_response(command: str, classification: Classification) -> str:
    """Build user-facing message when a command is blocked."""
    cmd_preview = command if len(command) <= 80 else command[:77] + "..."
    return (
        f"[error] Command BLOCKED by safety policy.\n"
        f"  Reason: {classification.reason}\n"
        f"  Pattern: {classification.matched}\n"
        f"  Command: {cmd_preview}"
    )


# ─────────────────────────────────────────────────────────
# Public exports for testing
# ─────────────────────────────────────────────────────────

def get_pattern_lists() -> dict[str, list[str]]:
    """Return the pattern lists (for inspection / extension)."""
    return {
        "allow": list(_ALLOW_PATTERNS),
        "warn": list(_WARN_PATTERNS),
        "block": list(_BLOCK_PATTERNS),
    }