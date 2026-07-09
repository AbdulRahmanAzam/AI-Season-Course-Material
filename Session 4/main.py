"""main.py — Entry point for Demo Harness.

Usage:
    python main.py
"""

# Force UTF-8 stdout/stderr on Windows (cp1252 can't print box-drawing chars).
import sys
import io
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

# Load .env FIRST so agent modules see API keys when imported.
from dotenv import load_dotenv
load_dotenv()

from agent.loop import run  # noqa: E402  (must come after stdout reconfigure)


if __name__ == "__main__":
    run()
