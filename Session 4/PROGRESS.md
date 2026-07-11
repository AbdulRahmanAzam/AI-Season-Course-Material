# DemoHarness — Progress Log & Handoff Document

**Last updated:** 2026-07-06
**Project:** Minimum-viable agent harness (Python)
**Repo:** https://github.com/MuhammadMustafa18/DemoHarness

---

## 🎯 Project Goal

Build a **2-hour minimum-viable agent harness** that:
- Connects an LLM to tools (file ops, bash, etc.)
- Implements ReAct pattern (Observe → Think → Act → Observe)
- Has pluggable LLM (mock → real)
- Has pluggable memory (in-memory list → future vector DB)
- Has pluggable tools (registry pattern)

---

## ✅ What's Built (4 Checkpoints Done)

### Checkpoint 0: Setup ✅
- Folder structure
- `.gitignore` (Python + IDE + OS)
- `.env.example` template
- GitHub repo initialized and connected

### Checkpoint 1: Mock LLM Chat REPL ✅
- `agent/mock_llm.py` (deleted in Checkpoint 4)
- `agent/llm.py` (router, now real_llm only)
- `agent/memory.py` (conversation history list)
- `agent/loop.py` (REPL)
- `main.py` (entry point with UTF-8 fix)

### Checkpoint 2: Tools + ReAct Loop ✅
- `agent/tools.py` (tool registry: read_file, list_dir)
- `agent/prompts.py` (system prompts)
- Tool calling via JSON actions
- Multi-turn ReAct with MAX_ITERATIONS cap

### Checkpoint 4: Real LLM Integration ✅
- `agent/real_llm.py` (Anthropic Claude via custom proxy)
- `requirements.txt` (anthropic, openai, rich, python-dotenv)
- `.env.example` updated for Anthropic format
- Mock LLM deleted (production mode)
- `demo_test.py` (automated testing with sample inputs)
- Temperature control (default 0.0 for deterministic behavior)

### Checkpoint 2-Expanded: Tool Suite ✅
- `agent/tools.py` extended: write_file, edit_file, glob, grep, bash
- `edit_file` — Claude Code-style surgical exact-match replace
- `bash` — cross-platform shell (Git Bash / cmd.exe / sh fallback chain)
- `test_tools.py` — 25+ assertions covering all 6 tools

### Checkpoint 4-Expanded: Observation Role Fix ✅
- Loop observation role: `assistant` → `user` with `[Tool Result for X]` prefix
- System prompt updated to clarify "tool results arrive as user-role messages"
- Result: multi-turn reasoning now works correctly

### Checkpoint 5: Bash Safety Layer ✅
- `agent/safety.py` — pattern-based classifier (ALLOW / WARN / BLOCK)
- BLOCK patterns: `rm -rf /`, `mkfs`, `dd to device`, fork bombs, `shutdown`
- WARN patterns: `rm`, `mv`, `cp`, `curl`, `git push`, `npm install`, etc.
- ALLOW patterns: `ls`, `cat`, `grep`, `find`, `pwd`, `git status`, etc.
- Unknown commands default to WARN (safe default)
- `bash()` tool now gates through safety layer
- Interactive permission prompt: `[y/n/a]` (allow / deny / always-this-command)
- Session-scoped `always_allow` set — "always" answers don't re-prompt for same command
- `test_safety.py` — 40 assertions covering classify() + bash() integration
- `loop.py` wires `prompt_fn` and `always_allow` set into bash handler

### Checkpoint 6: Web Tools ✅
- `web_search(query, max_results=8)` — DuckDuckGo HTML endpoint, no API key
- `web_fetch(url)` — Jina AI markdown converter, returns clean LLM-friendly text
- Both use stdlib `urllib` (no extra dependencies)
- Real network calls, no mocking
- `web_fetch` has retry-on-rate-limit logic (Jina free tier ~20s cooldown)
- `test_web.py` — smoke tests for both tools
- Verified end-to-end: agent searches web, structures answer with categories, offers follow-up fetch

---

## 📁 Current File Structure

```
DemoHarness/
├── .venv/                      # Python virtual environment
├── .env                        # API keys (GITIGNORED — sensitive)
├── .env.example                # Template (committed)
├── .gitignore                  # Comprehensive Python gitignore
├── README.md                   # Project overview
├── PROGRESS.md                 # This file (handoff doc)
├── Steps.md                    # Personal notes/learning log
├── requirements.txt            # anthropic, openai, rich, python-dotenv
├── resume.tex                  # LaTeX resume (Jake's template, fixed overlap)
├── main.py                     # Entry point with UTF-8 + load_dotenv
├── demo_test.py                # Automated test with mock inputs
└── agent/
    ├── __init__.py             # Empty package marker
    ├── llm.py                  # Router: real_llm.chat() (3 lines)
    ├── real_llm.py             # Anthropic Claude integration
    ├── loop.py                 # REPL + ReAct orchestration
    ├── memory.py               # In-memory message history
    ├── tools.py                # Tool registry (read_file, list_dir)
    └── prompts.py              # System prompt template
```

---

## 🔑 Key Files — What They Do

| File | Lines | Purpose |
|------|-------|---------|
| `main.py` | ~22 | Entry. Forces UTF-8 on Windows, `load_dotenv()`, calls `loop.run()` |
| `agent/llm.py` | ~22 | Single source of truth for LLM. Just imports & forwards to `real_llm` |
| `agent/real_llm.py` | ~165 | Anthropic SDK + custom base_url. JSON parsing with fallback. |
| `agent/loop.py` | ~125 | REPL + ReAct: Read user → add to memory → LLM think → tool call or final → repeat |
| `agent/memory.py` | ~30 | Just a list of `Message` TypedDicts. Helpers: init, add_user, add_assistant |
| `agent/tools.py` | ~115 | `_TOOLS` list with name/description/parameters/handler. Public API: get_schemas, get_handler, list_names |
| `agent/prompts.py` | ~30 | System prompt string with `{tool_list}` placeholder |

---

## 🔄 ReAct Loop Flow (per user turn)

```
User input
  ↓
1. mem.add_user(history, text)
  ↓
2. FOR i in range(MAX_ITERATIONS=8):
  ↓
3. llm.chat(history) → returns JSON string
  ↓
4. parse JSON → action = {action: tool_call|final, ...}
  ↓
5a. If tool_call:
      handler = tool_registry.get_handler(tool_name)
      observation = handler(**args)
      history.append({role: assistant, content: "[observation for X] ..."})
      print tool call + preview
      goto 2
  ↓
5b. If final:
      print("Agent: " + answer)
      mem.add_assistant(history, answer)
      break loop
```

---

## 🎨 Tool Registry Pattern

**Add a new tool = edit `agent/tools.py`:**

```python
def my_tool(arg1: str, arg2: int = 5) -> str:
    """Do something."""
    return f"Got {arg1}, {arg2}"

_TOOLS.append({
    "name": "my_tool",
    "description": "What this tool does (LLM reads this)",
    "parameters": {
        "type": "object",
        "properties": {
            "arg1": {"type": "string", "description": "..."},
            "arg2": {"type": "integer", "description": "..."},
        },
        "required": ["arg1"],   # arg2 is optional
    },
    "handler": my_tool,
})
```

**Loop, LLM, memory — kuch change nahi karna.** Pluggable.

---

## 🔌 LLM Configuration (.env)

```ini
ANTHROPIC_BASE_URL=https://api.minimax.io/anthropic   # Custom proxy
ANTHROPIC_AUTH_TOKEN=sk-cp-w-...                       # API key (sensitive!)
MODEL_NAME=Opus 4.7                                     # Or claude-3-5-sonnet-latest
TEMPERATURE=0.0                                         # CRITICAL: 0 for deterministic
MAX_TOKENS=2048
```

**Important env vars:**
- `ANTHROPIC_AUTH_TOKEN` OR `ANTHROPIC_API_KEY` (auth)
- `ANTHROPIC_BASE_URL` (optional, for proxies like minimax)
- `MODEL_NAME` (default: claude-3-5-sonnet-latest)
- `TEMPERATURE` (default in code: 0.0 — DO NOT set to >0.5, causes hallucination)
- `MAX_TOKENS` (default: 2048)

---

## 🐛 Known Issues & Fixes

### Issue 1: Windows CP1252 Unicode Error
**Symptom:** `UnicodeEncodeError: 'charmap' codec can't encode characters`
**Fix:** Force UTF-8 at top of `main.py`:
```python
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")
```

### Issue 2: `.env` Not Auto-Loaded
**Symptom:** `RuntimeError: No API key found`
**Fix:** Explicit `load_dotenv()` BEFORE importing agent modules in `main.py`

### Issue 3: LLM Hallucination (FastAPI Bug)
**Symptom:** Claude returns content not present in real file
**Root Cause:** Temperature too high (default 1.0 = very random)
**Fix:** Set `TEMPERATURE=0.0` (deterministic, tool-calling reliable)
**Implementation:** `real_llm.py` reads `os.environ.get("TEMPERATURE", "0.0")`

### Issue 4: Mock LLM Infinite Loop
**Symptom:** Tool called repeatedly without final answer
**Fix (mock only):** Observation check runs first — "if any tool observation exists → final answer"
**Why still there:** Real LLM doesn't need this heuristic; mock does. Will naturally disappear.

---

## 🧪 Testing Status

### What's been verified ✅
- Real Claude handles chat-only queries
- Real Claude calls `list_dir` tool correctly
- Real Claude calls `read_file` tool correctly
- Multi-turn memory works
- Multi-step ReAct works (one query → multiple tool calls)
- Urdu/English mix handled

### Known quirks (LLM-side, not code-side)
- Same input can produce slightly different outputs (controlled by temperature)
- Multi-turn conversations occasionally confuse LLM (industry-wide issue)
- Tool selection sometimes defaults to clarify instead of act (valid behavior)

### How to test
```bash
cd D:/Fresh_Start/Harness/DemoHarness
.venv/Scripts/activate
python main.py
```

Or automated:
```bash
python demo_test.py
```

---

## 🚀 What's NOT Built Yet (Future Checkpoints)

### Checkpoint 7: Native Tool API
- Drop JSON-in-text hack; use Anthropic native `tool_use` blocks
- `tool_use_id` tracking, typed `tool_result` content blocks
- Reliable multi-turn with native tool_use

### Checkpoint 8: Rich Terminal UI
- Colored output (cyan/yellow/green)
- Tool call panels with rich library
- Spinner during LLM thinking
- Streaming responses

### Checkpoint 9: Plan Mode
- Agent proposes plan first, user approves, then exec
- Sub-agents for parallel work
- TodoList tracking mid-task

### Checkpoint 10: Better Memory
- Persistent storage (SQLite)
- Conversation history save/load
- Sliding window (limit context size)
- Vector memory for long-term recall

### Checkpoint 11: Multi-Provider LLM
- OpenAI adapter, local (Ollama) adapter
- Provider abstraction layer

### Checkpoint 12: Polish
- Better error handling, async support
- Multi-agent (sub-agents for parallel work)

---

## 📚 Concepts Learned So Far

| Concept | Where | Why Important |
|---------|-------|---------------|
| **REPL** | `loop.py` | Foundation of all interactive agents |
| **Memory as a list** | `memory.py` | Simplest context model, works for short conversations |
| **Tool registry pattern** | `tools.py` | Open/Closed Principle — add tools without changing core |
| **ReAct pattern** | `loop.py` | Industry-standard agent loop (Reason + Act) |
| **Pluggable LLM** | `llm.py` | Same interface, swap implementations |
| **JSON actions** | `real_llm.py` | LLM returns structured data, not prose |
| **Temperature control** | `real_llm.py` | Lower = deterministic, higher = creative/risky |
| **Dependency Injection** | `loop.py` (input_fn, output_fn) | Testable code, swappable I/O |
| **UTF-8 on Windows** | `main.py` | Box-drawing chars need explicit encoding |
| **dotenv pattern** | `main.py` | Secrets outside code, version control safe |

---

## 🎓 Key Lessons

### Lesson 1: Mock → Real transition is where most harnesses fail
- Mock ki hacks (like Rule 0 observation check) real LLM mein disappear
- Interface stability is what makes migration painless

### Lesson 2: Temperature is critical for tool calling
- `1.0` (default) = hallucination risk
- `0.0` = reliable tool selection
- Set `TEMPERATURE=0.0` in `.env` for production agent

### Lesson 3: Pluggability is not optional
- llm.py / tools.py / memory.py all separate concerns
- New tool = 1 entry in tools.py
- New LLM = 1 new file, llm.py update
- No "big rewrite" ever needed

### Lesson 4: Real LLMs are non-deterministic
- Same input → different output (sometimes)
- Even with temp=0, multi-turn behavior varies
- Build defensive: validate outputs, don't trust blindly

---

## 🔧 Recovery Commands

If session breaks, run these to verify state:

```bash
# Check structure
ls -la D:/Fresh_Start/Harness/DemoHarness/

# Verify venv
cd D:/Fresh_Start/Harness/DemoHarness
source .venv/Scripts/activate
python --version
python -c "import anthropic; print(anthropic.__version__)"

# Check git status
git status
git log --oneline

# Test env loading
python -c "from dotenv import load_dotenv; load_dotenv(); import os; print(os.environ.get('ANTHROPIC_AUTH_TOKEN', 'NOT SET')[:10] + '...')"

# Quick test
python demo_test.py
```

---

## 📞 Resume From Here

When picking up tomorrow:
1. Read this file
2. Read `README.md`
3. Read `agent/real_llm.py` (most complex file)
4. Run `python demo_test.py` to verify state
5. Pick next checkpoint (5: Rich UI recommended)

**Time estimate for Checkpoint 5 (Rich UI):** ~25 min

---

## ⚠️ Security Notes

### ⚠️ API KEY WAS LEAKED IN CHAT HISTORY ⚠️
- Key visible in conversation transcripts
- **Action required:** rotate key in minimax dashboard
- Generate new key, update `.env`
- Old key should be revoked

### Best practices to follow
- NEVER paste API keys in chat/commits
- Use `.env` for all secrets
- `.env` is in `.gitignore` (verified)
- `.env.example` is the commitable template

---

## 📊 Stats

| Metric | Value |
|--------|-------|
| Total commits | 5 (as of Checkpoint 4) |
| Lines of code | ~600 (Python) + 280 (resume LaTeX) |
| Files | 12 (8 Python + 2 env + 2 docs) |
| Dependencies | 4 (anthropic, openai, rich, python-dotenv) |
| Tools registered | 2 (read_file, list_dir) |
| Time invested today | ~3.5 hours |

---

## 🤝 Working Style Notes

- User is learning — explain concepts, don't just dump code
- Use Urdu/Hindi mix where natural (user comfortable)
- Commit at each checkpoint with descriptive message
- Test before claiming done
- "Replay mode" preferred — user wants to see each step
- Reasonable to push back on design choices (user does)
- Pragmatic over perfect (e.g., keep-as-is + doc over premature refactor)

---

**End of handoff. Next session: continue from Checkpoint 5.**