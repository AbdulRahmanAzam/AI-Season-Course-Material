"""
test_tools.py — Sanity tests for the Phase 2 tool suite.

Run: python test_tools.py
"""
import os
import sys
import tempfile
from pathlib import Path

# Force UTF-8 on Windows.
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from agent.tools import (
    read_file, write_file, edit_file, list_dir, glob, grep, bash
)


PASS = "[PASS]"
FAIL = "[FAIL]"


def assert_eq(label: str, got, expected):
    ok = got == expected
    tag = PASS if ok else FAIL
    print(f"  {tag} {label}")
    if not ok:
        print(f"        got:      {got!r}")
        print(f"        expected: {expected!r}")
    return ok


def assert_contains(label: str, haystack: str, needle: str):
    ok = needle in haystack
    tag = PASS if ok else FAIL
    print(f"  {tag} {label}")
    if not ok:
        print(f"        looking for: {needle!r}")
        print(f"        in:          {haystack[:200]!r}")
    return ok


def main():
    passed = 0
    total = 0

    # Use an isolated temp dir so we don't pollute the real repo.
    with tempfile.TemporaryDirectory() as tmp:
        tmpdir = Path(tmp)
        os.chdir(tmpdir)
        sub = tmpdir / "sub"
        sub.mkdir()

        # ── write_file ─────────────────────────────────────
        print("\n[write_file]")
        r = write_file("hello.txt", "line1\nline2\nline3\n")
        total += 1; passed += assert_contains("creates file", r, "[ok] Wrote")
        total += 1; passed += assert_eq("file exists", (tmpdir / "hello.txt").read_text(), "line1\nline2\nline3\n")

        # nested dir creation
        r = write_file(str(sub / "nested.txt"), "nested")
        total += 1; passed += assert_contains("creates nested", r, "[ok] Wrote")
        total += 1; passed += assert_eq("nested content", (sub / "nested.txt").read_text(), "nested")

        # content too large
        big = "x" * 60000
        r = write_file("big.txt", big)
        total += 1; passed += assert_contains("rejects oversized", r, "[error] Content too large")

        # ── read_file ───────────────────────────────────────
        print("\n[read_file]")
        r = read_file("hello.txt")
        total += 1; passed += assert_eq("reads back", r, "line1\nline2\nline3\n")

        r = read_file("nonexistent.txt")
        total += 1; passed += assert_contains("missing file error", r, "[error] File not found")

        # ── edit_file ───────────────────────────────────────
        print("\n[edit_file]")
        r = edit_file("hello.txt", "line2\n", "LINE2\n")
        total += 1; passed += assert_contains("edit success", r, "[ok] 1 replacement")
        total += 1; passed += assert_eq("content changed", (tmpdir / "hello.txt").read_text(), "line1\nLINE2\nline3\n")

        # not found
        r = edit_file("hello.txt", "no_such_text", "x")
        total += 1; passed += assert_contains("edit not-found error", r, "[error] old_string not found")

        # multi-match (replace_all=False default)
        write_file("multi.txt", "x\nx\nx\n")
        r = edit_file("multi.txt", "x", "y")
        total += 1; passed += assert_contains("multi-match without flag fails", r, "matches 3 places")

        # multi-match with replace_all=True
        r = edit_file("multi.txt", "x", "y", replace_all=True)
        total += 1; passed += assert_contains("replace_all works", r, "[ok] 3 replacements")
        total += 1; passed += assert_eq("all replaced", (tmpdir / "multi.txt").read_text(), "y\ny\ny\n")

        # empty old_string refused
        r = edit_file("multi.txt", "", "z")
        total += 1; passed += assert_contains("empty old_string refused", r, "[error] old_string is empty")

        # ── list_dir ────────────────────────────────────────
        print("\n[list_dir]")
        r = list_dir(".")
        total += 1; passed += assert_contains("lists hello.txt", r, "hello.txt")
        total += 1; passed += assert_contains("lists multi.txt", r, "multi.txt")

        r = list_dir(str(sub))
        total += 1; passed += assert_contains("lists nested dir", r, "nested.txt")

        # ── glob ────────────────────────────────────────────
        print("\n[glob]")
        write_file("a.py", "x")
        write_file("b.py", "x")
        write_file("c.md", "x")
        write_file(str(sub / "d.py"), "x")

        r = glob("*.py")
        total += 1; passed += assert_contains("finds top-level .py", r, "a.py")
        total += 1; passed += assert_contains("finds b.py", r, "b.py")
        total += 1; passed += assert_contains("excludes .md", r if "c.md" not in r else "[FAIL] excluded", "")

        r = glob("**/*.py")
        total += 1; passed += assert_contains("recursive finds nested", r, "d.py")

        # ── grep ────────────────────────────────────────────
        print("\n[grep]")
        write_file("src.py", "def foo():\n    pass\ndef bar():\n    pass\n")
        r = grep(r"def \w+", ".")
        total += 1; passed += assert_contains("finds foo", r, "def foo")
        total += 1; passed += assert_contains("finds bar", r, "def bar")
        total += 1; passed += assert_contains("line numbers", r, ":1:")

        r = grep(r"def \w+", "src.py", include="*.py")
        total += 1; passed += assert_contains("include filter works", r, "def foo")

        r = grep(r"^\bNOPE\b$", ".")
        total += 1; passed += assert_contains("no match message", r, "(no matches")

        # invalid regex
        r = grep("[invalid", ".")
        total += 1; passed += assert_contains("invalid regex error", r, "[error] Invalid regex")

        # ── bash ────────────────────────────────────────────
        # Note: bash() is now safety-gated. We use a "y" prompt for WARN commands.
        print("\n[bash]")
        def yes_prompt(p): return "y"

        r = bash("echo hello", prompt_fn=yes_prompt)
        total += 1; passed += assert_contains("echo works", r, "hello")
        total += 1; passed += assert_contains("exit code shown", r, "[exit 0]")

        r = bash("false", prompt_fn=yes_prompt)
        total += 1; passed += assert_contains("non-zero exit captured", r, "[exit 1]")

        r = bash("ls > /tmp/_test_bash_out.txt && cat /tmp/_test_bash_out.txt", prompt_fn=yes_prompt)
        total += 1; passed += assert_contains("writes/reads file via shell", r, "_test_bash_out.txt")

        r = bash("sleep 5", prompt_fn=yes_prompt, timeout=1)
        total += 1; passed += assert_contains("timeout enforced", r, "[error] Command timed out")

    # ── summary ──────────────────────────────────────────
    print(f"\n{'='*40}")
    print(f"  {passed}/{total} passed")
    print(f"{'='*40}")
    return 0 if passed == total else 1


if __name__ == "__main__":
    sys.exit(main())