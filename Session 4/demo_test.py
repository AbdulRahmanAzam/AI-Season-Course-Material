"""demo_test.py — Quick interactive demo: runs the agent REPL with sample inputs.

This module is not part of the agent itself; it exists for demonstration
and manual testing. It feeds a fixed list of sample inputs into the agent
loop and exits cleanly when the list is exhausted.
"""

from __future__ import annotations

import io
import sys
from collections.abc import Callable, Iterator
from typing import Final
from unittest.mock import patch

from dotenv import load_dotenv

from agent.loop import run

__all__: Final[list[str]] = ["SAMPLE_INPUTS", "main"]


SAMPLE_INPUTS: Final[list[str]] = [
    "list karo files aur batao kya kya hai",
    "read the file main.py and summarize in one line",
    "what tools do you have?",
    "agent folder mein kya hai?",
    "hi kya haal hai?",
    "quit",
]


def _force_utf8_stdio() -> None:
    """Reconfigure stdout/stderr to UTF-8 on Windows so box-drawing chars print."""
    if sys.platform != "win32":
        return
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")


def _make_fake_input(inputs: list[str]) -> Callable[[str], str]:
    """Build an `input()` replacement that yields `inputs` then always 'quit'."""
    iter_inputs: Iterator[str] = iter(inputs)

    def fake_input(prompt: str) -> str:
        del prompt  # unused; required by input() signature
        try:
            return next(iter_inputs)
        except StopIteration:
            return "quit"

    return fake_input


def main() -> None:
    """Run the agent REPL against the bundled SAMPLE_INPUTS."""
    _force_utf8_stdio()
    load_dotenv()

    fake_input = _make_fake_input(SAMPLE_INPUTS)
    with patch("builtins.input", fake_input):
        run(input_fn=fake_input)


if __name__ == "__main__":
    main()
