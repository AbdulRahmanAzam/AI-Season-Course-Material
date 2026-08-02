"""
calculator.py — INTENTIONALLY BROKEN for Demo 2
================================================

BUGS (point these out on screen):
  add()      → subtracts instead of adding
  subtract() → adds instead of subtracting

WORKING:
  multiply(), divide()
"""

# ══════════════════════════════════════════════════════════════════════════════


def add(a: float, b: float) -> float:
    """Should return a + b"""

    # Fix: change subtraction to addition
    return a + b


# ══════════════════════════════════════════════════════════════════════════════


def subtract(a: float, b: float) -> float:
    """Should return a - b"""

    # Fix: change addition to subtraction
    return a - b


# ══════════════════════════════════════════════════════════════════════════════


def multiply(a: float, b: float) -> float:
    """Works correctly"""

    return a * b


# ══════════════════════════════════════════════════════════════════════════════


def divide(a: float, b: float) -> float:
    """Works correctly — raises on divide-by-zero"""

    if b == 0:
        raise ValueError("Cannot divide by zero")

    return a / b
