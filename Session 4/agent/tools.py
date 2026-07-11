"""
tools.py — Tool registry for the agent.

Each tool has:
- name       : unique identifier
- description: what it does (LLM reads this to decide)
- parameters : JSON schema describing args (LLM reads this to format calls)
- handler(**kwargs) -> str : runs the tool, returns string result.

Adding a new tool = add entry to _TOOLS list. Loop automatically picks it up.

Phase 2 tool suite:
    read_file   - Read file contents (truncated for safety)
    write_file  - Create or overwrite a file
    edit_file   - Surgical exact-match replacement (Claude Code style)
    list_dir    - List directory contents
    glob        - File pattern matching
    grep        - Regex search over file contents
    bash        - Run shell command (no permission layer yet — Phase 4)
"""

from __future__ import annotations

import os
import re
import shutil
import subprocess
import sys
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Callable

from agent import safety


# ─────────────────────────────────────────────────────────
# Safety constants
# ─────────────────────────────────────────────────────────

# Max chars returned from a single read to protect context window.
_READ_CAP_CHARS = 4000

# Max chars accepted by write_file in one call.
_WRITE_CAP_CHARS = 50000

# Default + max timeout for bash commands (seconds).
_BASH_DEFAULT_TIMEOUT = 30
_BASH_MAX_TIMEOUT = 120

# Cap on grep output to keep context small.
_GREP_MAX_RESULTS = 50
_GREP_MAX_LINE_CHARS = 200

# Web tool constants.
_WEB_TIMEOUT_SECONDS = 20
_WEB_MAX_BYTES = 500_000          # 500KB cap per fetch / search HTML
_WEB_SEARCH_MAX_RESULTS = 8
_WEB_FETCH_MAX_CHARS = 30_000     # ~30K chars of markdown to feed LLM

# Common browser User-Agent (DDG blocks generic Python UAs).
_USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36"
)


# ─────────────────────────────────────────────────────────
# Tool implementations — file ops
# ─────────────────────────────────────────────────────────

def read_file(path: str) -> str:
    """Read a file and return its contents (truncated for safety)."""
    try:
        full = os.path.abspath(path)
        with open(full, "r", encoding="utf-8", errors="replace") as f:
            data = f.read()
        if len(data) > _READ_CAP_CHARS:
            data = data[:_READ_CAP_CHARS] + f"\n... [truncated, total {len(data)} chars]"
        return data
    except FileNotFoundError:
        return f"[error] File not found: {path}"
    except PermissionError:
        return f"[error] Permission denied: {path}"
    except Exception as e:
        return f"[error] {type(e).__name__}: {e}"


def write_file(path: str, content: str) -> str:
    """Create or overwrite a file with the given content.

    Creates parent directories if they don't exist. Overwrites without warning
    (LLM is expected to read_file first when modifying existing files).
    """
    try:
        if len(content) > _WRITE_CAP_CHARS:
            return f"[error] Content too large: {len(content)} chars > {_WRITE_CAP_CHARS}"

        full = Path(path).resolve()
        # Create parent dirs (mkdir -p semantics).
        full.parent.mkdir(parents=True, exist_ok=True)

        full.write_text(content, encoding="utf-8")
        return f"[ok] Wrote {len(content)} chars to {full}"
    except PermissionError:
        return f"[error] Permission denied: {path}"
    except Exception as e:
        return f"[error] {type(e).__name__}: {e}"


def edit_file(path: str, old_string: str, new_string: str, replace_all: bool = False) -> str:
    """Surgical replacement — find exact `old_string` and replace with `new_string`.

    Rules:
        - Fails if old_string is not found.
        - Fails if old_string matches multiple places (unless replace_all=True).
        - Reads the file fresh each call so no stale state.

    Returns a short diff-style summary of what changed.
    """
    try:
        if not old_string:
            return "[error] old_string is empty — refusing to edit (would replace entire file)"

        full = Path(path).resolve()
        original = full.read_text(encoding="utf-8", errors="replace")

        occurrences = original.count(old_string)
        if occurrences == 0:
            return f"[error] old_string not found in {path}"
        if occurrences > 1 and not replace_all:
            return (
                f"[error] old_string matches {occurrences} places in {path}. "
                f"Add more surrounding context to make it unique, or pass replace_all=True."
            )

        new_content = original.replace(old_string, new_string, -1 if replace_all else 1)
        full.write_text(new_content, encoding="utf-8")

        # Build a tiny diff preview (first changed hunk).
        old_lines = old_string.splitlines() or [""]
        new_lines = new_string.splitlines() or [""]
        diff_preview = []
        for ln in old_lines[:3]:
            diff_preview.append(f"  - {ln}")
        for ln in new_lines[:3]:
            diff_preview.append(f"  + {ln}")
        if len(old_lines) > 3 or len(new_lines) > 3:
            diff_preview.append("  ...")

        scope = f"{occurrences} replacement{'s' if (replace_all and occurrences > 1) else ''}"
        return (
            f"[ok] {scope} in {path}\n"
            + "\n".join(diff_preview)
        )
    except FileNotFoundError:
        return f"[error] File not found: {path}"
    except PermissionError:
        return f"[error] Permission denied: {path}"
    except Exception as e:
        return f"[error] {type(e).__name__}: {e}"


# ─────────────────────────────────────────────────────────
# Tool implementations — directory + discovery
# ─────────────────────────────────────────────────────────

def list_dir(path: str = ".") -> str:
    """List contents of a directory."""
    try:
        full = os.path.abspath(path)
        entries = sorted(os.listdir(full))
        if not entries:
            return "(empty directory)"
        return "\n".join(entries)
    except Exception as e:
        return f"[error] {type(e).__name__}: {e}"


def glob(pattern: str, path: str = ".") -> str:
    """Find files matching a glob pattern.

    Pattern examples:
        "*.py"            — all .py in cwd
        "**/*.py"         — all .py recursively
        "agent/*.py"      — .py files in agent/
        "test_*.py"       — test files
    """
    try:
        root = Path(path).resolve()
        matches = sorted(root.glob(pattern))
        if not matches:
            return f"(no files match pattern: {pattern})"
        # Show paths relative to root for readability.
        rel = [str(m.relative_to(root)) if m.is_relative_to(root) else str(m) for m in matches]
        return "\n".join(rel)
    except Exception as e:
        return f"[error] {type(e).__name__}: {e}"


def grep(pattern: str, path: str = ".", include: str = "") -> str:
    """Search file contents for a regex pattern.

    Args:
        pattern: regex to search for
        path:    directory or file to search (default: cwd, recursive)
        include: optional file glob filter (e.g. "*.py")

    Returns:
        "file:line:matched_line" entries, capped at _GREP_MAX_RESULTS.
    """
    try:
        regex = re.compile(pattern)
    except re.error as e:
        return f"[error] Invalid regex: {e}"

    root = Path(path)
    if not root.exists():
        return f"[error] Path not found: {path}"

    results: list[str] = []
    files_searched = 0

    # Build list of files to scan.
    if root.is_file():
        files = [root]
    else:
        if include:
            files = list(root.rglob(include))
        else:
            # Default: all regular files, skip dotfiles + common junk.
            skip_dirs = {".git", ".venv", "__pycache__", "node_modules"}
            files = [
                p for p in root.rglob("*")
                if p.is_file()
                and not any(part in skip_dirs for part in p.parts)
            ]

    for fpath in files:
        if not fpath.is_file():
            continue
        files_searched += 1
        try:
            text = fpath.read_text(encoding="utf-8", errors="replace")
        except Exception:
            continue
        for lineno, line in enumerate(text.splitlines(), start=1):
            if regex.search(line):
                snippet = line.strip()
                if len(snippet) > _GREP_MAX_LINE_CHARS:
                    snippet = snippet[:_GREP_MAX_LINE_CHARS] + "..."
                results.append(f"{fpath}:{lineno}:{snippet}")
                if len(results) >= _GREP_MAX_RESULTS:
                    return (
                        "\n".join(results)
                        + f"\n... [truncated, {_GREP_MAX_RESULTS}+ matches; "
                          f"refine pattern to narrow]"
                    )

    if not results:
        return f"(no matches for pattern: {pattern!r} across {files_searched} files)"

    return "\n".join(results)


# ─────────────────────────────────────────────────────────
# Tool implementations — execution
# ─────────────────────────────────────────────────────────

def bash(
    command: str,
    timeout: int = _BASH_DEFAULT_TIMEOUT,
    prompt_fn: Callable[[str], str] | None = None,
    always_allow: set[str] | None = None,
) -> str:
    """Run a shell command, gated by the safety classifier.

    Args:
        command: shell command string
        timeout: max seconds to wait (clamped to _BASH_MAX_TIMEOUT)
        prompt_fn: callable(prompt_text) -> response_str, used to ask
            permission for WARN-tier commands. If None, WARN commands
            default to deny (safe default).
        always_allow: mutable set of exact-command strings the user has
            pre-approved for this session. Passed by loop.py so "always"
            answers don't re-prompt.

    Returns:
        Combined output with exit code, or block/deny/timeout message.

    Safety flow:
        1. classify(command) → allow / warn / block
        2. block  → refuse, return error
        3. warn   → ask user via prompt_fn (or default deny)
        4. allow  → run directly

    Cross-platform: discovers shell via SHELL env, `bash` on PATH, or
        falls back to `cmd.exe` on Windows. Tries each candidate in order —
        the first one that produces actual output (not a CreateProcessCommon
        shim error) wins. Excludes `wsl.exe` from candidates because it has
        its own CLI semantics, and is only useful when called from Windows
        to launch a WSL shell — not as a generic `bash -c` replacement.
    """
    # ── Safety gate ────────────────────────────────────────
    cls = safety.classify(command)

    if cls.tier == "block":
        return safety.format_block_response(command, cls)

    if cls.tier == "warn":
        # Pre-approved?
        if always_allow is not None and command in always_allow:
            pass  # proceed
        else:
            if prompt_fn is None:
                # No prompt available — default deny (safe default).
                return (
                    f"[error] WARN command requires user approval but no "
                    f"prompt_fn was provided. Command: {command[:80]}"
                )
            prompt = safety.format_prompt(command, cls)
            response = prompt_fn(prompt)
            verdict = safety.parse_permission_response(response)
            if verdict == "deny":
                return "[error] User denied permission for command."
            if verdict == "always":
                if always_allow is not None:
                    always_allow.add(command)
            # verdict == "allow" or "always" → proceed

    # ── Execute ────────────────────────────────────────────
    return _execute_bash(command, timeout)


def _execute_bash(command: str, timeout: int) -> str:
    """Inner: actually run the command via subprocess. No safety checks here."""
    timeout = max(1, min(int(timeout), _BASH_MAX_TIMEOUT))

    # Build a list of candidate shells to try, in priority order.
    candidates: list[list[str]] = []

    explicit = os.environ.get("SHELL")
    if explicit:
        candidates.append([explicit])

    if sys.platform == "win32":
        for name in ("bash.exe", "bash"):
            found = shutil.which(name)
            if found:
                candidates.append([found])
        git_bash = Path("C:/Program Files/Git/usr/bin/bash.exe")
        if git_bash.exists():
            candidates.append([str(git_bash)])
        comspec = os.environ.get("COMSPEC", "cmd.exe")
        candidates.append([comspec])
    else:
        for name in ("bash", "sh"):
            found = shutil.which(name)
            if found:
                candidates.append([found])

    shim_error_signatures = (
        "CreateProcessCommon",
        "execvpe",
        "wsl.exe --help",
        "Invalid command line argument",
        "No such file or directory",
    )

    last_error: str = ""
    for shell in candidates:
        is_cmd = shell[0].lower().endswith("cmd.exe")
        flag = "/c" if is_cmd else "-c"
        argv = shell + [flag, command]

        try:
            proc = subprocess.run(
                argv,
                capture_output=True,
                text=True,
                # Windows defaults to cp1252, which crashes on UTF-8 bytes
                # (e.g. em-dash = 0x90). Force UTF-8 with replace-fallback
                # so subprocess reader thread never dies on non-ASCII output.
                encoding="utf-8",
                errors="replace",
                timeout=timeout,
                cwd=os.getcwd(),
            )
            out = (proc.stdout or "") + (proc.stderr or "")
            if any(sig in out for sig in shim_error_signatures) and proc.returncode != 0:
                last_error = out.strip()[:200]
                continue

            if out:
                out = out.rstrip() + f"\n[exit {proc.returncode}]"
            else:
                out = f"(no output)\n[exit {proc.returncode}]"
            if len(out) > _READ_CAP_CHARS:
                out = out[:_READ_CAP_CHARS] + f"\n... [truncated, total {len(out)} chars]"
            return out
        except subprocess.TimeoutExpired:
            return f"[error] Command timed out after {timeout}s"
        except FileNotFoundError:
            last_error = f"shell not found: {shell[0]}"
            continue
        except Exception as e:
            last_error = f"{type(e).__name__}: {e}"
            continue

    return f"[error] No shell could execute the command. Last error: {last_error or 'unknown'}"


# ─────────────────────────────────────────────────────────
# Tool implementations — web access
# ─────────────────────────────────────────────────────────

def web_search(query: str, max_results: int = _WEB_SEARCH_MAX_RESULTS) -> str:
    """Search the web using DuckDuckGo's HTML endpoint.

    Returns up to `max_results` entries in the form:
        [N] Title
            URL
            Snippet text...

    Notes:
        - Uses POST to https://html.duckduckgo.com/html/ (no API key needed).
        - No signup, no rate limit exposed — but be courteous.
        - Quality depends on DDG's HTML structure; if they change it, parsing
          may break. (Defensive: returns whatever it can extract.)
    """
    if not query.strip():
        return "[error] query is empty"

    max_results = max(1, min(int(max_results), 15))  # hard cap at 15

    try:
        data = urllib.parse.urlencode({"q": query}).encode("utf-8")
        req = urllib.request.Request(
            "https://html.duckduckgo.com/html/",
            data=data,
            headers={
                "User-Agent": _USER_AGENT,
                "Accept": "text/html",
                "Accept-Language": "en-US,en;q=0.9",
            },
        )
        with urllib.request.urlopen(req, timeout=_WEB_TIMEOUT_SECONDS) as resp:
            raw = resp.read(_WEB_MAX_BYTES)
            html = raw.decode("utf-8", errors="replace")

    except urllib.error.URLError as e:
        return f"[error] Network error: {e.reason}"
    except TimeoutError:
        return f"[error] Search timed out after {_WEB_TIMEOUT_SECONDS}s"
    except Exception as e:
        return f"[error] {type(e).__name__}: {e}"

    # Parse: each result has <a class="result__a" href="URL">TITLE</a>
    # and <a class="result__snippet">SNIPPET</a>.
    # The href is sometimes a DDG redirect (//duckduckgo.com/l/?uddg=...) —
    # urllib.parse.unquote extracts the real URL after the uddg= param.
    title_pat = re.compile(
        r'class="result__a"[^>]*href="([^"]+)"[^>]*>(.*?)</a>',
        re.DOTALL,
    )
    snippet_pat = re.compile(
        r'class="result__snippet"[^>]*>(.*?)</a>',
        re.DOTALL,
    )

    titles = title_pat.findall(html)
    snippets = snippet_pat.findall(html)

    if not titles:
        return f"(no results for query: {query!r})"

    out: list[str] = []
    for i, (raw_url, title_html) in enumerate(titles[:max_results]):
        # Strip HTML tags from title.
        title = re.sub(r"<[^>]+>", "", title_html).strip()
        # Resolve DDG redirect URLs.
        if "uddg=" in raw_url:
            m = re.search(r"uddg=([^&]+)", raw_url)
            if m:
                raw_url = urllib.parse.unquote(m.group(1))
        snippet_html = snippets[i] if i < len(snippets) else ""
        snippet = re.sub(r"<[^>]+>", "", snippet_html).strip()
        snippet = re.sub(r"\s+", " ", snippet)
        out.append(f"[{i+1}] {title}\n    {raw_url}\n    {snippet}")

    return "\n\n".join(out)


def _should_bypass_jina(url: str) -> bool:
    """Check if URL should be fetched directly (bypass Jina).

    Some sites block Jina's User-Agent or have anti-bot measures that
    Jina's scraper can't bypass. For these, we fetch directly with a
    browser-like User-Agent.
    """
    direct_domains = (
        "raw.githubusercontent.com",   # GitHub raw files (Jina can't render)
        "gist.githubusercontent.com",
        "api.github.com",
        "githubusercontent.com",
    )
    return any(d in url for d in direct_domains)


def _fetch_direct(url: str) -> str:
    """Fetch URL directly with browser headers. Used as fallback for sites
    that block Jina. Performs basic HTML stripping for LLM consumption."""
    try:
        req = urllib.request.Request(
            url,
            headers={
                "User-Agent": _USER_AGENT,
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                "Accept-Language": "en-US,en;q=0.9",
            },
        )
        with urllib.request.urlopen(req, timeout=_WEB_TIMEOUT_SECONDS) as resp:
            raw = resp.read(_WEB_MAX_BYTES)
            text = raw.decode("utf-8", errors="replace")
    except urllib.error.HTTPError as e:
        try:
            body = e.read().decode("utf-8", errors="replace")[:200]
        except Exception:
            body = ""
        return f"[error] HTTP {e.code}: {e.reason} {body}".strip()
    except urllib.error.URLError as e:
        return f"[error] Network error: {e.reason}"
    except TimeoutError:
        return f"[error] Fetch timed out after {_WEB_TIMEOUT_SECONDS}s"
    except Exception as e:
        return f"[error] {type(e).__name__}: {e}"

    # Raw text/markdown endpoints — return as-is, no HTML stripping.
    if any(url.endswith(ext) for ext in (".md", ".txt", ".json", ".csv", ".py")):
        if len(text) > _WEB_FETCH_MAX_CHARS:
            text = text[:_WEB_FETCH_MAX_CHARS] + f"\n\n... [truncated, total {len(text)} chars]"
        return text

    # For HTML pages, strip script/style blocks and tags so LLM gets text.
    text = re.sub(r"<script[^>]*>.*?</script>", " ", text, flags=re.DOTALL | re.IGNORECASE)
    text = re.sub(r"<style[^>]*>.*?</style>", " ", text, flags=re.DOTALL | re.IGNORECASE)
    text = re.sub(r"<[^>]+>", " ", text)
    text = re.sub(r"\s+", " ", text).strip()

    if len(text) > _WEB_FETCH_MAX_CHARS:
        text = text[:_WEB_FETCH_MAX_CHARS] + f"\n\n... [truncated, total {len(text)} chars]"
    return text


def web_fetch(url: str) -> str:
    """Fetch a URL and return its content as readable text (LLM-friendly).

    Implementation strategy:
        1. Some sites (GitHub raw, etc.) — fetch directly with browser headers.
        2. Other sites — route through Jina AI for clean markdown extraction.

    Both paths are free and require no API key.

    Limits:
        - ~30K chars returned (cap to protect context window)
        - JS-heavy SPAs may render poorly
        - Jina free tier has ~20s rate limit (handled with retry + direct fallback)
    """
    if not url.strip():
        return "[error] url is empty"

    # Normalize URL.
    if not url.startswith(("http://", "https://")):
        url = "https://" + url

    # Direct fetch for sites that Jina can't render / blocks.
    if _should_bypass_jina(url):
        return _fetch_direct(url)

    # General path: try Jina, fall back to direct on failure.
    jina_url = f"https://r.jina.ai/{url}"

    import time
    text: str = ""
    last_err: str = ""
    for attempt in range(2):  # 1 retry — Jina's cooldown is ~20s
        req = urllib.request.Request(
            jina_url,
            headers={
                "User-Agent": _USER_AGENT,
                "Accept": "text/plain",
                "X-Return-Format": "markdown",
                "X-Timeout": str(_WEB_TIMEOUT_SECONDS),
            },
        )
        try:
            with urllib.request.urlopen(req, timeout=_WEB_TIMEOUT_SECONDS) as resp:
                raw = resp.read(_WEB_MAX_BYTES)
                text = raw.decode("utf-8", errors="replace")
                break
        except urllib.error.HTTPError as e:
            if e.code in (403, 429, 503) and attempt == 0:
                last_err = f"HTTP {e.code}"
                time.sleep(20)
                continue
            # Final HTTP error — fall through to direct fetch fallback.
            return _fetch_direct(url)
        except urllib.error.URLError:
            return _fetch_direct(url)
        except TimeoutError:
            return f"[error] Fetch timed out after {_WEB_TIMEOUT_SECONDS}s"
        except Exception as e:
            return f"[error] {type(e).__name__}: {e}"
    else:
        return f"[error] Jina rate-limited after 2 attempts: {last_err}"

    # Jina prepends "Title: ... Markdown Content:" — strip it.
    if "Markdown Content:" in text:
        text = text.split("Markdown Content:", 1)[1].lstrip()

    if len(text) > _WEB_FETCH_MAX_CHARS:
        text = text[:_WEB_FETCH_MAX_CHARS] + f"\n\n... [truncated, total {len(text)} chars]"
    return text


# ─────────────────────────────────────────────────────────
# Tool registry — each entry has schema + handler.
# ─────────────────────────────────────────────────────────

_TOOLS: list[dict] = [
    {
        "name": "read_file",
        "description": (
            "Read the contents of a file. Returns the text (truncated if large). "
            "Use this when you need to see what's in a file."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "Path to the file (relative or absolute).",
                }
            },
            "required": ["path"],
        },
        "handler": read_file,
    },
    {
        "name": "write_file",
        "description": (
            "Create or overwrite a file with the given content. "
            "Creates parent directories if needed. "
            "Use this when creating new files or doing full rewrites."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "Path to the file to write.",
                },
                "content": {
                    "type": "string",
                    "description": "Full file content to write.",
                },
            },
            "required": ["path", "content"],
        },
        "handler": write_file,
    },
    {
        "name": "edit_file",
        "description": (
            "Surgical replacement: find an exact `old_string` in the file and "
            "replace it with `new_string`. Fails if old_string is not found or "
            "matches multiple places (unless replace_all=True). "
            "Use this for targeted edits without rewriting the whole file."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "Path to the file to edit.",
                },
                "old_string": {
                    "type": "string",
                    "description": "Exact text to find. Must match exactly once unless replace_all=True.",
                },
                "new_string": {
                    "type": "string",
                    "description": "Replacement text.",
                },
                "replace_all": {
                    "type": "boolean",
                    "description": "If true, replace every occurrence. Default false.",
                    "default": False,
                },
            },
            "required": ["path", "old_string", "new_string"],
        },
        "handler": edit_file,
    },
    {
        "name": "list_dir",
        "description": (
            "List files and folders in a directory. "
            "Use this to discover what files exist."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "Directory path. Defaults to current dir.",
                    "default": ".",
                }
            },
            "required": [],
        },
        "handler": list_dir,
    },
    {
        "name": "glob",
        "description": (
            "Find files matching a glob pattern. Examples: '*.py', '**/*.md', "
            "'agent/*.py'. Returns paths relative to the search root."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "pattern": {
                    "type": "string",
                    "description": "Glob pattern (e.g. '*.py', '**/*.json').",
                },
                "path": {
                    "type": "string",
                    "description": "Root directory to search from. Default '.'.",
                    "default": ".",
                },
            },
            "required": ["pattern"],
        },
        "handler": glob,
    },
    {
        "name": "grep",
        "description": (
            "Search file contents for a regex pattern. Returns "
            "'file:line:matched_line' entries. Use `include` to filter by "
            "file glob (e.g. '*.py'). Skips .git, .venv, __pycache__, node_modules."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "pattern": {
                    "type": "string",
                    "description": "Regex pattern to search for.",
                },
                "path": {
                    "type": "string",
                    "description": "File or directory to search. Default '.' (recursive).",
                    "default": ".",
                },
                "include": {
                    "type": "string",
                    "description": "Optional file glob filter (e.g. '*.py').",
                    "default": "",
                },
            },
            "required": ["pattern"],
        },
        "handler": grep,
    },
    {
        "name": "bash",
        "description": (
            "Run a shell command and return stdout+stderr. "
            "Timeout enforced (default 30s, max 120s). "
            "Use this for: running tests, git operations, installing dependencies, "
            "anything file/shell related that other tools can't do. "
            "Cross-platform: uses bash on Unix/Git-Bash, cmd.exe on Windows. "
            "NOTE: No permission layer yet — be careful with destructive commands."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "command": {
                    "type": "string",
                    "description": "Shell command to execute.",
                },
                "timeout": {
                    "type": "integer",
                    "description": "Timeout in seconds. Default 30, max 120.",
                    "default": 30,
                },
            },
            "required": ["command"],
        },
        "handler": bash,
    },
    {
        "name": "web_search",
        "description": (
            "Search the web using DuckDuckGo. Returns up to N results "
            "(title, URL, snippet). Use this when you need to find "
            "current information, look up documentation, or find resources. "
            "No API key needed. Network call — may be slow or rate-limited."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Search query string.",
                },
                "max_results": {
                    "type": "integer",
                    "description": "Max results to return (default 8, max 15).",
                    "default": 8,
                },
            },
            "required": ["query"],
        },
        "handler": web_search,
    },
    {
        "name": "web_fetch",
        "description": (
            "Fetch a URL and return its content as clean markdown (LLM-friendly). "
            "Routes through Jina AI which extracts readable text from the page. "
            "Use this AFTER web_search to read the actual content of a result, "
            "or directly when you know which URL you want. "
            "Returns up to ~30K chars. No API key needed."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "url": {
                    "type": "string",
                    "description": "Full URL (http:// or https://). https:// is added if missing.",
                },
            },
            "required": ["url"],
        },
        "handler": web_fetch,
    },
]


# ─────────────────────────────────────────────────────────
# Public API — the only thing the loop should import.
# ─────────────────────────────────────────────────────────

def get_schemas() -> list[dict]:
    """Return tool schemas for LLM (without handlers)."""
    return [
        {"name": t["name"], "description": t["description"], "parameters": t["parameters"]}
        for t in _TOOLS
    ]


def get_handler(name: str) -> Callable[..., str] | None:
    """Return the handler for a tool name, or None if not found."""
    for t in _TOOLS:
        if t["name"] == name:
            return t["handler"]
    return None


def list_names() -> list[str]:
    return [t["name"] for t in _TOOLS]