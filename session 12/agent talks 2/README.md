# Agent Talks 2 — two **A2A agents** debating each other

Session 12 files 01–11 teach A2A with agents that **cooperate**: an orchestrator hires a
weather agent, gets an answer, done. One question, one reply.

This folder uses the exact same protocol for agents that **disagree**, over and over, and
have to end up somewhere. Same claim — `"Toyota is better than every other car brand."` —
opposite orders:

| Agent | Skill | Job |
|---|---|---|
| **Debate Agent (PRO)** | `argue_for` | argue the claim is TRUE |
| **Debate Agent (CON)** | `argue_against` | argue the claim is FALSE |
| **Debate Referee** | `judge_debate` | only hired if 20 messages pass with no agreement |

Every arrow between them is a real A2A `message/send`. It ends within **20 messages**,
always with both agents on the **same** verdict.

> Everything runs in **one terminal**. The agents are Python objects instead of FastAPI
> servers, but the card fields, the JSON-RPC envelope and the Task object are byte-for-byte
> the A2A you already taught. Turning them back into real servers is 10 lines — see the
> bottom of this file.

---

## Setup

```bash
pip install -r requirements.txt
copy .env.example .env
```

Free Groq key, no card needed: <https://console.groq.com/keys>

---

## Files

Numbered files are the ones you **run**. Unnumbered files are the **library** they import.

| # | File | What it teaches |
|---|---|---|
| 1 | `01_agent_card.py` | Two **Agent Cards** side by side — same shape, different skill |
| 2 | `02_one_agent_replies.py` | **Discovery → `message/send` → Task**. Prints the whole Task object, then `tasks/get` |
| 3 | `03_two_agents_talk.py` | The **A2A communication flow** — one agent's answer relayed as the other's question |
| 4 | `04_debate_orchestrator.py` | ⭐ **LangGraph** drives the full 20-message debate. Referee, live transcript |
| – | `debate_agent.py` | The **agent base** — card, skills, `handle_rpc`, Task lifecycle, memory |
| – | `live_transcript.py` | Plumbing. Writes the `.md` / `.json` / `.html` while the debate runs |

```bash
python 01_agent_card.py
python 02_one_agent_replies.py
python 03_two_agents_talk.py
python 04_debate_orchestrator.py
python 04_debate_orchestrator.py "Python is better than JavaScript"
```

---

## Every A2A concept, and where it lives here

| Concept | Where |
|---|---|
| **Agent Card** | `DebateAgent.card` — name, url, version, modes, capabilities, skills |
| **Agent discovery** | `agent.get_agent_card()` — stands in for `GET /.well-known/agent-card.json` |
| **Agent skills** | `argue_for`, `argue_against`, `judge_debate` — each with `id`, `tags`, `examples` |
| **Agent base** | `class DebateAgent` — written once, both debaters are one function call |
| **Messages** | `{"role","parts":[{"kind":"text"}],"messageId","contextId","taskId","kind":"message"}` |
| **Tasks** | every turn is a Task: `id`, `contextId`, `status.state`, `history`, `artifacts` |
| **Task states** | `submitted` → `working` → `completed`, visible in file 2 |
| **Artifacts** | the finished argument, as `artifacts[0].parts[0].text` |
| **JSON-RPC** | `message/send`, `tasks/get`, and a real `-32601 Method not found` |
| **A2A flow** | discover → send → Task → read artifact → relay to the other agent → repeat |

---

## The two things to say out loud

### 1. `contextId` **is** the memory

```python
self.memory = {}                              # contextId -> [messages]
history = self.memory.setdefault(context_id, [])
```

Each agent files its own history under the debate's `contextId`. "Each agent has its own
memory" stops being a Python variable and becomes a **protocol** idea — which is why the
same code works whether the agents are in one process or on two continents.

At the end, file 4 prints the proof:

```
Debate Agent (PRO): 14 messages in its own memory, 7 tasks handled
Debate Agent (CON): 12 messages in its own memory, 6 tasks handled
```

Different numbers, because they heard different things. Neither dict is reachable from the
other agent.

### 2. The graph does **not** hold the memory

Look at `DebateState` in file 4 — there is no message history in it. Only whose turn it is
and what each side currently believes.

```
LangGraph = the conductor   (whose turn, are we done, who breaks a tie)
A2A       = the wire        (every arrow is a message/send)
```

---

## How it always ends in agreement

The system prompt is rebuilt **every turn**, and its last line changes as time runs out:

| Messages so far | Injected instruction |
|---|---|
| 0–9 | Argue hard. Do not concede. |
| 10–14 | Name the strongest point your opponent made and say what is true about it. |
| 15–20 | Time is nearly up. You **must** reach a shared verdict. |

Plus one rule that keeps it interesting: **never repeat an argument you already used**.
Without it the two agents recycle the same three points for twenty messages. With it they
work through reliability, safety, dealer network, hybrids, resale, market share — and then
honestly run out and concede.

Every reply ends with `VERDICT: YES` or `VERDICT: NO`. When both match, `whose_turn()`
returns `END`. If 20 messages pass with no match, the **referee** is discovered and hired,
and both adopt its answer.

---

## Watching it live

While file 4 runs:

1. **Terminal** — replies stream word by word, each followed by `[a2a] task-xxxx -> completed`.
2. **`transcripts/debate_<topic>.html`** — **double-click it while the debate is running.**
   It reloads every 2 seconds and scrolls to the newest message. PRO left in orange, CON
   right, referee in black across the middle.
3. **`transcripts/debate_<topic>.md`** — `Ctrl+Shift+V` in VS Code for the same thing.

`transcripts/debate_<topic>.json` is the whole debate as data.

---

## Turning these into real servers

Nothing about the agents changes. You only add the two HTTP promises back:

```python
from fastapi import FastAPI, Request
import uvicorn
from debate_agent import make_pro

agent = make_pro("Toyota is better than every other car brand.")
app = FastAPI()

@app.get("/.well-known/agent-card.json")
def card():
    return agent.get_agent_card()

@app.post("/")
async def rpc(request: Request):
    return agent.handle_rpc(await request.json())

uvicorn.run(app, host="127.0.0.1", port=8010)
```

Then the orchestrator's `send_message` swaps one line:

```python
agent.handle_rpc(rpc)                       # today
requests.post(card["url"], json=rpc).json() # as a real server
```

That is the whole difference. The `url` fields in the cards (`:8010`, `:8011`, `:8012`)
are already set for it.

---

## Tips and gotchas

- **`ModuleNotFoundError: langchain_groq`** — run `pip install -r requirements.txt`.
- **Model.** `openai/gpt-oss-120b`. Groq deprecated `llama-3.3-70b-versatile` in June 2026,
  so do not copy that id in from session 6.
- **VS Code underlines the imports but it runs fine** — Pylance is pointing at a different
  Python. `Ctrl+Shift+P` → *Python: Select Interpreter*.
- **429 rate limit.** Free tier. There is a `time.sleep(1)` between turns; raise it if the
  whole room runs the demo at once.
- **Debate ends after 2 messages.** Your claim was not arguable. Pick one with two real sides.
- **`.env` and `transcripts/` are gitignored.**

---

## Student exercises

1. **Make them real servers.** Copy the snippet above into `pro_server.py` and
   `con_server.py`, swap the one line in `send_message`, run 3 terminals. Nothing else changes.
2. **Add a fourth agent** — a `fact_checker` with skill `check_claim` that the orchestrator
   calls after every PRO turn. Subclass `DebateAgent` like `RefereeAgent` does.
3. **Route by skill, not by name.** Right now the orchestrator knows which agent is PRO.
   Make it pick by scanning `card["skills"][0]["tags"]` for `"for"` / `"against"`, the way
   session 12 file 06 does.
4. **Implement `message/stream`.** The cards say `"streaming": false`. Make `handle_rpc`
   a generator yielding `status-update` and `artifact-update` events, and flip the card.
5. **Persist the tasks.** `self.tasks` dies with the process. Write it to JSON so
   `tasks/get` still works on the next run.

---

## Learn more

- A2A specification — <https://a2a-protocol.org/latest/specification/>
- LangGraph graph API — <https://docs.langchain.com/oss/python/langgraph/graph-api>
- Groq models and deprecations — <https://console.groq.com/docs/models>
