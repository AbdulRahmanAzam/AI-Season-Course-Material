# DemoHarness

A 2-hour buildable **minimum viable agent harness** — built checkpoint by checkpoint.

## What it is

An agent harness is the loop that connects an LLM (brain) to tools (hands), with memory,
so it can *actually do things* rather than just generate text.

## Checkpoints (build order)

| # | What | Status |
|---|------|--------|
| 0 | Skeleton + `.gitignore` + `.env.example` + GitHub | ✅ done |
| 1 | Plain chat REPL with **mock LLM** (no API key needed) | ✅ current |
| 2 | Tool calling: `read_file` tool + ReAct-style loop | ⏳ next |
| 3 | `bash` tool with safety prompt | ⏳ |
| 4 | `rich` terminal UI polish | ⏳ |
| 5 | Swap mock → real LLM (OpenAI) | ⏳ |

## Run

```bash
python -m venv .venv
source .venv/Scripts/activate     # Git Bash on Windows
pip install -r requirements.txt   # (openai, rich, python-dotenv — when needed)
python main.py
```

## Architecture (as of Checkpoint 1)

```
┌────────────┐    ┌────────────┐    ┌────────────┐
│  main.py   │ ─▶ │ agent/     │ ─▶ │ mock_llm   │
│ (entry pt) │    │   loop.py  │    │            │
└────────────┘    │   llm.py   │    └────────────┘
                  │   memory.py│
                  └────────────┘
```

## Files

- `agent/loop.py` — REPL (Read-Eval-Print Loop). The agent loop.
- `agent/llm.py` — single LLM interface (today: mock; later: OpenAI).
- `agent/mock_llm.py` — fake LLM for learning the loop without API cost.
- `agent/memory.py` — conversation history (in-memory list of messages).
- `main.py` — starts `loop.run()`.

## Key concepts learned

- **ReAct pattern** (Observe → Think → Act → Observe) — implemented in Checkpoint 2.
- **Tool registry** — implemented in Checkpoint 2.
- **Memory = list of messages** — the simplest model that works.
- **Pluggable LLM** — same interface, swap implementation. (Real LLM in Checkpoint 5.)
