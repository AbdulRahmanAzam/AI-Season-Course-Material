# Session 9 — Agent-to-Agent (A2A) Communication

How do AI agents built by **different teams, frameworks, and companies** talk to
each other and hand off work? That is what Google's **A2A (Agent2Agent) protocol**
standardizes. This session teaches it from zero: first we build A2A **by hand**
(so you see it is just JSON over HTTP), then we use the **official `a2a-sdk`**.

## The one line to remember

| Protocol | Connects | Think of it as |
|----------|----------|----------------|
| **MCP**  | an agent → its **tools / data / APIs** | giving one worker a toolbox |
| **A2A**  | an agent → **another agent** | letting workers phone and hire each other |

They are complementary. In **Session 6** `get_weather` and `convert_currency` were
**tools** one agent owned (MCP-style). Here we turn each into its **own independent
agent** that others discover and delegate to (A2A-style).

## Setup

```bash
# from this folder:
python -m venv .venv
.venv\Scripts\activate            # Windows
pip install -r requirements.txt
```

The LLM files (07–09) use **Groq** (`openai/gpt-oss-120b`). They are **optional**:

```bash
copy .env.example .env            # then paste your free key from console.groq.com/keys
```

**No key? Everything still runs** — files 07–09 automatically fall back to **MOCK
mode** (canned answers), so the whole lesson works offline.

## The files (run them in order)

| # | File | What it teaches |
|---|------|-----------------|
| 01 | `01_what_is_an_agent_card.py` | The **Agent Card** — an agent's résumé (no server) |
| 02 | `02_greeting_agent.py` | An A2A **server** built by hand (card + `message/send`) |
| 03 | `03_greeting_client.py` | An A2A **client**: discover → send → read |
| 04 | `04_weather_agent.py` | A **specialist** agent (weather, mock data) |
| 05 | `05_currency_agent.py` | A **specialist** agent (currency, mock data) |
| 06 | `06_orchestrator.py` | ⭐ An **orchestrator** that discovers both and **delegates** |
| 07 | `07_llm_weather_agent.py` | Same weather agent, now with a **Groq LLM** brain |
| 08 | `08_llm_currency_agent.py` | Same currency agent, now with a **Groq LLM** brain |
| 09 | `09_llm_orchestrator.py` | Orchestrator that uses an **LLM to route** |
| 10 | `10_sdk_agent.py` | The same agent with the **official `a2a-sdk`** |
| 11 | `11_sdk_client.py` | The **SDK client** |

## How to run each part

Each **agent is a server** — it keeps running in its own terminal. The
**client / orchestrator** runs in a separate terminal and talks to them.

**Part 1 — one agent, by hand**
```bash
# Terminal 1
python 02_greeting_agent.py
# Terminal 2
python 03_greeting_client.py
```
Also open `http://localhost:8001/.well-known/agent-card.json` in a browser to see
the raw card.

**Part 2 — two agents collaborating** ⭐
```bash
# Terminal 1
python 04_weather_agent.py       # port 8002
# Terminal 2
python 05_currency_agent.py      # port 8003
# Terminal 3
python 06_orchestrator.py
```
The orchestrator discovers both and routes each question to the right one.

**Part 3 — give the agents a real brain (Groq)**

Swap the hand-made agents for the LLM ones — **same ports**, so the orchestrator
doesn't change at all (that's the point of A2A: agents are black boxes):
```bash
# Terminal 1
python 07_llm_weather_agent.py   # port 8002
# Terminal 2
python 08_llm_currency_agent.py  # port 8003
# Terminal 3
python 06_orchestrator.py        # or: python 09_llm_orchestrator.py
```

**Part 4 — the official SDK**
```bash
# Terminal 1
python 10_sdk_agent.py           # port 9999
# Terminal 2
python 11_sdk_client.py
```

## Ports used

`8001` greeting · `8002` weather · `8003` currency · `9999` SDK agent.
Windows: if a port is stuck, close the terminal running that agent (Ctrl+C).

## Learn more

- Spec & tutorials: <https://a2a-protocol.org>
- Python SDK: `pip install a2a-sdk` (this lesson was built and tested on **1.1.1**)
