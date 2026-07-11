"""
test_web.py — Smoke tests for web_search and web_fetch tools.

Note: These make REAL network calls. Run only when network is available.
Jina free tier has rate limits (~1 req per 10s); tests include delays.
"""
import sys
import time

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from agent.tools import web_search, web_fetch


PASS = "[PASS]"
FAIL = "[FAIL]"


def assert_contains(label, haystack, needle):
    ok = needle in haystack
    tag = PASS if ok else FAIL
    print(f"  {tag} {label}")
    if not ok:
        print(f"        looking for: {needle!r}")
        print(f"        in (first 300): {haystack[:300]!r}")
    return ok


def assert_not_error(label, result):
    ok = not result.startswith("[error]")
    tag = PASS if ok else FAIL
    print(f"  {tag} {label}")
    if not ok:
        print(f"        got error: {result!r}")
    return ok


def main():
    passed, total = 0, 0

    # ── web_search ───────────────────────────────────────
    print("\n[web_search]")
    r = web_search("python asyncio")
    total += 1; passed += assert_not_error("  basic search", r)
    total += 1; passed += assert_contains("  has numbered results", r, "[1]")
    total += 1; passed += assert_contains("  has URLs", r, "http")
    total += 1; passed += assert_contains("  has snippets", r, "\n    ")

    print("  (waiting 12s to respect DDG rate limits...)")
    time.sleep(12)

    # ── max_results ──────────────────────────────────────
    print("\n[web_search — max_results]")
    r = web_search("python tutorial", max_results=3)
    total += 1; passed += assert_contains("  respects max_results=3", r, "[3]")
    # Should NOT have [4] if max_results=3 works correctly.
    if "[4]" in r:
        total += 1; passed += 0  # mark fail
        print(f"  [FAIL]   found [4] despite max_results=3")
    else:
        total += 1; passed += 1
        print(f"  [PASS]   no [4] (max_results respected)")

    print("  (waiting 12s...)")
    time.sleep(12)

    # ── empty query ──────────────────────────────────────
    print("\n[web_search — empty query]")
    r = web_search("")
    total += 1; passed += assert_contains("  rejects empty", r, "[error]")

    print("  (waiting 12s...)")
    time.sleep(12)

    # ── web_fetch — example.com ──────────────────────────
    print("\n[web_fetch — example.com]")
    r = web_fetch("https://example.com")
    total += 1; passed += assert_not_error("  basic fetch", r)
    total += 1; passed += assert_contains("  contains 'Example Domain'", r, "Example Domain")

    print("  (waiting 12s...)")
    time.sleep(12)

    # ── web_fetch — auto-https ───────────────────────────
    print("\n[web_fetch — auto-https]")
    r = web_fetch("example.com")  # no scheme
    total += 1; passed += assert_not_error("  adds https://", r)

    print("  (waiting 12s...)")
    time.sleep(12)

    # ── web_fetch — empty url ────────────────────────────
    print("\n[web_fetch — empty url]")
    r = web_fetch("")
    total += 1; passed += assert_contains("  rejects empty", r, "[error]")

    # ── summary ───────────────────────────────────────────
    print(f"\n{'='*40}")
    print(f"  {passed}/{total} passed")
    print(f"{'='*40}")
    return 0 if passed == total else 1


if __name__ == "__main__":
    sys.exit(main())