"""
rules.py — Minimal ratchet system: mistakes → rules (manual).

Storage format: plain markdown file (default: DemoHarness.md).
Each rule is a section starting with `## [Rxxx] <title>`.

Commands (handled in loop.py):
  /log_mistake <description>  → append a new rule
  /recall <keyword>           → search and show matching rules
  /list                       → show all rules (compact)

Manual detection: this module does NOT auto-detect mistakes. The user
calls /log_mistake themselves when they notice a pattern worth
remembering. Lecture-friendly: forces user to think about what
went wrong before logging.

Detection → Extraction → Storage → Retrieval → Injection is the
full ratchet. This file implements only the manual subset
(Storage + simple Retrieval). Auto-detection/extraction is the
"next lecture" upgrade path.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path


# Default location — keeps .md file in project root, visible & git-trackable.
DEFAULT_RULES_FILE = "DemoHarness.md"

# Header block written when the file is first created.
_FILE_HEADER = """\
# DemoHarness Rules

> Auto-accumulated lessons from past agent mistakes. Each section is one rule.
> Use `/recall <keyword>` to search, `/list` to see everything.

---
"""


@dataclass
class Rule:
    """One parsed rule section from the .md file."""
    id: str              # "R001"
    title: str           # first-line summary (after the bracketed ID)
    body: str            # full section text after the metadata line
    category: str        # "tool_usage" | "verification" | etc.
    uses: int            # how many times it was recalled
    timestamp: str       # raw "Logged:" value

    def short(self) -> str:
        """One-line representation for /list."""
        return f"[{self.id}] {self.title}  ({self.category}, {self.uses} uses)"


# ────────────────────────────────────────────────────────────────────
# File I/O
# ────────────────────────────────────────────────────────────────────

def _ensure_file(path: str) -> None:
    """Create the file with a header if it doesn't exist."""
    p = Path(path)
    if not p.exists():
        p.write_text(_FILE_HEADER, encoding="utf-8")


def _read_file(path: str) -> str:
    """Read file contents (assumes file exists; create if missing)."""
    _ensure_file(path)
    return Path(path).read_text(encoding="utf-8")


def _append_block(path: str, block: str) -> None:
    """Append a rule block to the file."""
    _ensure_file(path)
    with open(path, "a", encoding="utf-8") as f:
        f.write(block)


# ────────────────────────────────────────────────────────────────────
# Parsing
# ────────────────────────────────────────────────────────────────────

# Matches a rule section header line, e.g.:
#   ## [R007] Some short title here
_SECTION_RE = re.compile(
    r"^## \[(?P<id>R\d+)\] (?P<title>.+?)$",
    re.MULTILINE,
)

# Matches the metadata line immediately after the header, e.g.:
#   **Logged:** 2026-07-08 14:30 | **Category:** tool_usage | **Uses:** 3 | **Helpful:** yes
_META_RE = re.compile(
    r"\*\*Logged:\*\*\s*(?P<ts>[^|]+?)\s*\|\s*"
    r"\*\*Category:\*\*\s*(?P<cat>[^|]+?)\s*\|\s*"
    r"\*\*Uses:\*\*\s*(?P<uses>\d+)\s*\|\s*"
    r"\*\*Helpful:\*\*\s*(?P<helpful>[^|]+?)(?:\n|$)",
)


def parse_rules(content: str) -> list[Rule]:
    """Parse the .md file into a list of Rule objects.

    Sections are delimited by `## [Rxxx] ...` headers. Anything before
    the first header (the file's preamble) is ignored.
    """
    headers = list(_SECTION_RE.finditer(content))
    rules: list[Rule] = []

    for i, m in enumerate(headers):
        # Body runs from end of this header line to the start of the next
        # one (or to end of file).
        body_start = m.end()
        body_end = headers[i + 1].start() if i + 1 < len(headers) else len(content)
        body = content[body_start:body_end].rstrip()

        # Pull metadata line out of the body (first non-blank line).
        meta_m = _META_RE.search(body)
        if meta_m:
            category = meta_m.group("cat").strip()
            uses = int(meta_m.group("uses"))
            timestamp = meta_m.group("ts").strip()
        else:
            category = "uncategorized"
            uses = 0
            timestamp = ""

        rules.append(Rule(
            id=m.group("id"),
            title=m.group("title").strip(),
            body=body,
            category=category,
            uses=uses,
            timestamp=timestamp,
        ))

    return rules


def next_rule_id(rules: list[Rule]) -> str:
    """Generate next sequential ID like 'R005' given existing rules."""
    if not rules:
        return "R001"
    nums = [
        int(r.id[1:])
        for r in rules
        if r.id.startswith("R") and r.id[1:].isdigit()
    ]
    return f"R{max(nums) + 1:03d}" if nums else "R001"


# ────────────────────────────────────────────────────────────────────
# Category guessing (super-light heuristic)
# ────────────────────────────────────────────────────────────────────

_CATEGORY_KEYWORDS = {
    "tool_usage": ("read_file", "write_file", "edit_file", "bash", "truncate",
                   "glob", "grep", "file", "tool"),
    "verification": ("verify", "test", "pytest", "claim", "passed", "fail"),
    "vague_tasks": ("vague", "ask", "clarify", "default", "refactor"),
    "prompt_injection": ("injection", "untrusted", "mojibake", "encoding"),
    "permission": ("permission", "allow", "deny", "warn"),
}


def guess_category(description: str) -> str:
    """Naive keyword-based category guess. Falls back to 'general'."""
    desc_lower = description.lower()
    scores: dict[str, int] = {}
    for cat, keywords in _CATEGORY_KEYWORDS.items():
        scores[cat] = sum(1 for kw in keywords if kw in desc_lower)
    best = max(scores.items(), key=lambda kv: kv[1])
    if best[1] == 0:
        return "general"
    return best[0]


# ────────────────────────────────────────────────────────────────────
# Public API used by loop.py commands
# ────────────────────────────────────────────────────────────────────

def log_rule(text: str, why: str = "", category: str = "general",
             path: str = DEFAULT_RULES_FILE) -> Rule:
    """Append a fully-specified rule (used by auto-extraction).

    Used by /log_mistake (auto path) and agent-side mistake extraction.
    """
    rules_list = parse_rules(_read_file(path))
    new_id = next_rule_id(rules_list)
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    safe_category = category or "general"

    title = text if len(text) <= 60 else text[:57] + "..."
    block = (
        f"\n## [{new_id}] {title}\n"
        f"**Logged:** {timestamp} | **Category:** {safe_category} | **Uses:** 0 | **Helpful:** pending\n\n"
        f"{text}\n\n"
    )
    if why:
        why_lines = "\n".join(f"> {line}" for line in why.splitlines())
        block += f"{why_lines}\n\n"
    block += f"---\n"
    _append_block(path, block)

    updated = parse_rules(_read_file(path))
    return updated[-1]


def log_mistake(description: str, path: str = DEFAULT_RULES_FILE) -> Rule:
    """Backward-compat manual entry path.

    Equivalent to log_rule(text=description, why="manual entry",
    category=guess_category(description)). Used by /log_mistake <text>
    when the user provides free-form text.
    """
    return log_rule(
        text=description,
        why="manual entry via /log_mistake",
        category=guess_category(description),
        path=path,
    )


def list_rules(path: str = DEFAULT_RULES_FILE) -> list[Rule]:
    """Return all rules in the file."""
    return parse_rules(_read_file(path))


def recall(query: str, path: str = DEFAULT_RULES_FILE) -> list[Rule]:
    """Find rules whose title or body contains the query (case-insensitive).

    Also bumps the `Uses` count for each match by rewriting the metadata
    line — this gives us data on which rules actually get referenced.
    """
    rules = parse_rules(_read_file(path))
    q = query.lower().strip()
    if not q:
        return []

    matches = [r for r in rules if q in r.title.lower() or q in r.body.lower()]

    # Bump uses count for matched rules (write back to file).
    if matches:
        _bump_uses([m.id for m in matches], path)

    # Return the (now incremented) versions.
    updated = parse_rules(_read_file(path))
    return [r for r in updated if r.id in {m.id for m in matches}]


def _bump_uses(rule_ids: list[str], path: str) -> None:
    """Increment the Uses count for given rule IDs in the file."""
    content = _read_file(path)
    for rid in rule_ids:
        # Match the metadata line for THIS specific rule id and
        # increment the Uses number. We anchor with the id at line start.
        pattern = re.compile(
            rf"(^## \[{re.escape(rid)}\] .+?\n\*\*Logged:\*\* [^|]+\|\s*\*\*Category:\*\*"
            rf" [^|]+\|\s*\*\*Uses:\*\*\s*)(\d+)",
            re.MULTILINE,
        )
        content, n = pattern.subn(
            lambda m: m.group(1) + str(int(m.group(2)) + 1),
            content,
            count=1,
        )
        if n == 0:
            # Fallback: rule has no metadata line — skip silently.
            continue
    Path(path).write_text(content, encoding="utf-8")
