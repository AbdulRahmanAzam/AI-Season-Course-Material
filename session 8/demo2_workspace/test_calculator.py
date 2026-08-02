"""
test_calculator.py — the EVALUATOR for Demo 2
===============================================

These tests ARE the loop's judge.
Agent must fix calculator.py until all assertions pass.
"""

from calculator import add, subtract, multiply, divide


# ══════════════════════════════════════════════════════════════════════════════
# TEST 1 — catches add() bug
# ══════════════════════════════════════════════════════════════════════════════

def test_add():
    assert add(2, 3) == 5


# ══════════════════════════════════════════════════════════════════════════════
# TEST 2 — catches subtract() bug
# ══════════════════════════════════════════════════════════════════════════════

def test_subtract():
    assert subtract(10, 4) == 6


# ══════════════════════════════════════════════════════════════════════════════
# TEST 3 — already passing (agent should NOT break this)
# ══════════════════════════════════════════════════════════════════════════════

def test_multiply():
    assert multiply(3, 4) == 12


# ══════════════════════════════════════════════════════════════════════════════
# TEST 4 — already passing
# ══════════════════════════════════════════════════════════════════════════════

def test_divide():
    assert divide(10, 2) == 5


# ══════════════════════════════════════════════════════════════════════════════
# TEST 5 — edge case (already passing)
# ══════════════════════════════════════════════════════════════════════════════

def test_divide_by_zero():
    try:
        divide(5, 0)
        assert False, "Expected ValueError"

    except ValueError:
        pass
