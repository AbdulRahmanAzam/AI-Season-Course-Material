"""
test_safety.py — Tests for the bash permission / safety layer.

Covers:
    - classify() returns correct tier for various commands
    - BLOCK patterns always win over ALLOW matches
    - bash() refuses BLOCK commands without invoking subprocess
    - bash() runs ALLOW commands without prompting
    - bash() prompts for WARN commands; respects y/n/a responses
    - bash() remembers "always" decisions across calls
"""
import os
import sys
import tempfile
from pathlib import Path

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from agent import safety
from agent.tools import bash


PASS = "[PASS]"
FAIL = "[FAIL]"


def assert_eq(label, got, expected):
    ok = got == expected
    tag = PASS if ok else FAIL
    print(f"  {tag} {label}")
    if not ok:
        print(f"        got:      {got!r}")
        print(f"        expected: {expected!r}")
    return ok


def assert_contains(label, haystack, needle):
    ok = needle in haystack
    tag = PASS if ok else FAIL
    print(f"  {tag} {label}")
    if not ok:
        print(f"        looking for: {needle!r}")
        print(f"        in:          {haystack[:200]!r}")
    return ok


def main():
    passed, total = 0, 0

    # ── classify() — pure function tests ─────────────────
    print("\n[classify() — ALLOW tier]")
    for cmd in ["ls -la", "cat main.py", "pwd", "git status", "grep -r foo ."]:
        cls = safety.classify(cmd)
        total += 1; passed += assert_eq(f"  {cmd!r}", cls.tier, "allow")

    print("\n[classify() — WARN tier]")
    for cmd in ["rm foo.txt", "mv a b", "curl https://x.com", "pip install x", "git commit -m hi"]:
        cls = safety.classify(cmd)
        total += 1; passed += assert_eq(f"  {cmd!r}", cls.tier, "warn")

    print("\n[classify() — BLOCK tier (destructive)]")
    for cmd in ["rm -rf /", "rm -rf /home", "mkfs.ext4 /dev/sda", "shutdown now", ":(){ :|:& };:"]:
        cls = safety.classify(cmd)
        total += 1; passed += assert_eq(f"  {cmd!r}", cls.tier, "block")

    print("\n[classify() — BLOCK overrides ALLOW]")
    # Even if "rm" looks like an allow somehow, BLOCK wins.
    cls = safety.classify("ls / && rm -rf /")
    total += 1; passed += assert_eq("  chained rm -rf /", cls.tier, "block")

    print("\n[classify() — unknown command defaults to WARN]")
    cls = safety.classify("custom-tool --flag")
    total += 1; passed += assert_eq("  unknown command", cls.tier, "warn")

    # ── parse_permission_response ─────────────────────────
    print("\n[parse_permission_response]")
    total += 1; passed += assert_eq("  'y' → allow", safety.parse_permission_response("y"), "allow")
    total += 1; passed += assert_eq("  'yes' → allow", safety.parse_permission_response("yes"), "allow")
    total += 1; passed += assert_eq("  'a' → always", safety.parse_permission_response("a"), "always")
    total += 1; passed += assert_eq("  'n' → deny", safety.parse_permission_response("n"), "deny")
    total += 1; passed += assert_eq("  '' → deny", safety.parse_permission_response(""), "deny")
    total += 1; passed += assert_eq("  'gibberish' → deny", safety.parse_permission_response("gibberish"), "deny")

    # ── bash() integration ───────────────────────────────
    print("\n[bash() — BLOCK refuses without prompt]")
    prompts_called = []
    def fake_prompt(p): prompts_called.append(p); return "y"
    r = bash("rm -rf /", prompt_fn=fake_prompt, always_allow=set())
    total += 1; passed += assert_contains("  returns block msg", r, "BLOCKED by safety policy")
    total += 1; passed += assert_eq("  no prompt shown", prompts_called, [])

    print("\n[bash() — ALLOW runs without prompt]")
    prompts_called.clear()
    r = bash("echo hello", prompt_fn=fake_prompt, always_allow=set())
    total += 1; passed += assert_contains("  ran echo", r, "hello")
    total += 1; passed += assert_eq("  no prompt shown", prompts_called, [])

    print("\n[bash() — WARN prompts user; respects 'n']")
    prompts_called.clear()
    def deny_prompt(p): prompts_called.append(p); return "n"
    r = bash("touch newfile.txt", prompt_fn=deny_prompt, always_allow=set())
    total += 1; passed += assert_contains("  shows prompt", prompts_called[0] if prompts_called else "", "Permission needed")
    total += 1; passed += assert_contains("  denied message", r, "User denied")
    total += 1; passed += assert_eq("  touch did NOT create file", (Path("newfile.txt").exists()), False)

    print("\n[bash() — WARN prompts user; respects 'y']")
    prompts_called.clear()
    def yes_prompt(p): prompts_called.append(p); return "y"
    r = bash("touch allowed.txt", prompt_fn=yes_prompt, always_allow=set())
    total += 1; passed += assert_contains("  shows prompt", prompts_called[0] if prompts_called else "", "Permission needed")
    total += 1; passed += assert_contains("  ran successfully", r, "[exit 0]")
    if Path("allowed.txt").exists():
        Path("allowed.txt").unlink()
        total += 1; passed += assert_eq("  file cleaned", True, True)

    print("\n[bash() — WARN remembers 'always' for SAME command]")
    # Create real file so rm succeeds (exit 0).
    Path("repeat_target.txt").write_text("hi")
    Path("repeat_target2.txt").write_text("hi")

    prompts_called.clear()
    always_set = set()
    def always_prompt(p): prompts_called.append(p); return "a"

    # First call: prompts, runs, adds to always_set
    r1 = bash("rm repeat_target.txt", prompt_fn=always_prompt, always_allow=always_set)
    total += 1; passed += assert_eq("  first call prompted", len(prompts_called), 1)
    total += 1; passed += assert_contains("  first call succeeded", r1, "[exit 0]")
    total += 1; passed += assert_eq("  added to always_set", "rm repeat_target.txt" in always_set, True)

    # Second call with SAME command: should NOT prompt
    Path("repeat_target.txt").write_text("hi")  # re-create
    r2 = bash("rm repeat_target.txt", prompt_fn=always_prompt, always_allow=always_set)
    total += 1; passed += assert_eq("  same cmd did NOT prompt", len(prompts_called), 1)
    total += 1; passed += assert_contains("  same cmd succeeded", r2, "[exit 0]")

    # Different WARN command should still prompt
    r3 = bash("rm repeat_target2.txt", prompt_fn=always_prompt, always_allow=always_set)
    total += 1; passed += assert_eq("  different cmd DID prompt", len(prompts_called), 2)

    # cleanup
    if Path("repeat_target2.txt").exists():
        Path("repeat_target2.txt").unlink()

    print("\n[bash() — no prompt_fn defaults to DENY for WARN]")
    r = bash("touch denied.txt", prompt_fn=None, always_allow=set())
    total += 1; passed += assert_contains("  requires approval msg", r, "requires user approval")

    # ── summary ───────────────────────────────────────────
    print(f"\n{'='*40}")
    print(f"  {passed}/{total} passed")
    print(f"{'='*40}")
    return 0 if passed == total else 1


if __name__ == "__main__":
    sys.exit(main())