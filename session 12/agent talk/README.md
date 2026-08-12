# Agent Talk — two agents arguing with each other

The rest of session 12 shows one agent **handing work to** another agent.
This folder shows two agents **disagreeing with** each other.

Both get the same claim — `"Toyota is better than every other car brand."` — and
opposite orders:

| Agent | Job |
|---|---|
| **PRO** | argue the claim is TRUE |
| **CON** | argue the claim is FALSE |

They take turns. Each one reads what the other just said before it replies, and each
one keeps its **own private memory** — there is no shared brain. The debate stops the
moment they land on the same answer, and never runs past **20 messages**.

---

## Setup

```bash
pip install -r requirements.txt

# copy .env.example to .env and paste your key in
copy .env.example .env
```

Free Groq key, no card needed: <https://console.groq.com/keys>

---

## Files

| # | File | What it teaches |
|---|---|---|
| 1 | `01_simple_debate.py` | The debate built **by hand** — a `while` loop and an `if/else`. No framework. |
| 2 | `02_debate_graph.py` | ⭐ The same debate, run by a **LangGraph** `StateGraph`. Adds a referee and writes the live transcript. |
| – | `live_transcript.py` | Plumbing, not a lesson. Writes the `.md` / `.json` / `.html` files while the debate runs. |

Run them in order — file 1 exists so that file 2 has something to be better than.

```bash
python 01_simple_debate.py
python 02_debate_graph.py
```

Any claim works:

```bash
python 02_debate_graph.py "Python is better than JavaScript"
```

---

## Watching it live

Three things happen at once while file 2 runs:

1. **Terminal** — each reply streams in word by word as the model writes it.
2. **`transcripts/debate_<topic>.html`** — a chat page. **Double-click it while the
   debate is still running.** It reloads itself every 2 seconds and scrolls to the
   newest message, so the class watches the bubbles appear. PRO on the left in orange,
   CON on the right, referee in black across the middle.
3. **`transcripts/debate_<topic>.md`** — open it in VS Code and press `Ctrl+Shift+V`.
   The preview grows line by line too.

`transcripts/debate_<topic>.json` is the same conversation as data — open it after the
run to show students the shape the agents actually produced.

---

## The one idea to say out loud

> **One agent's output becomes the other agent's input — with the label changed.**

```python
mine:   [AIMessage(text)]                 # my words go in MY memory as "assistant"
theirs: [HumanMessage(f"{who}: {text}")]  # the SAME words go in THEIR memory as "user"
```

PRO's own lines look like *"things I said"* to PRO, and like *"things someone said to
me"* to CON. Swap the names and you get the other side. That is the whole mechanic of
two agents talking — everything else in file 2 is scheduling.

---

## What LangGraph actually adds (file 2)

Three ideas, nothing more:

| Idea | In the code |
|---|---|
| **State** | `DebateState` — one dictionary holding **two separate memories**, both verdicts, and the message count |
| **Node** | a plain function: state in, updates out. `pro_agent`, `con_agent`, `referee` |
| **Conditional edge** | `whose_turn()` returns the **name of the next node**. Pointing it back at an earlier node is what makes a **loop** |

```
START ---> pro_agent ---.
                         >--- whose_turn? ---> pro_agent | con_agent | referee | END
           con_agent ---'
           referee ---> END
```

`mid test task/09_graph.py` is a straight line — start to finish, no going back. This is
the first graph in the course that **cycles**, and conditional edges are the only reason
it can.

---

## How they are forced to agree

The system prompt is rebuilt **every single turn**, and the last line of it changes as
the clock runs down:

| Messages so far | Instruction injected |
|---|---|
| 0–11 | Argue hard. Do not concede. |
| 12–15 | Name the strongest point your opponent made and say what is true about it. |
| 16–20 | Time is nearly up. You **must** reach a shared verdict. If their case is stronger, change your VERDICT to match theirs. |

Every reply ends with `VERDICT: YES` or `VERDICT: NO`. When both agents' verdicts match,
`whose_turn()` returns `END` and the debate stops early.

If 20 messages go by and they still disagree, the **referee** node makes one neutral call,
reads the whole transcript, and writes its answer into *both* verdicts. So the run always
ends with the two of them on the same side — never an anticlimax in class.

---

## Tips and gotchas

- **`ModuleNotFoundError: langchain_groq`** — run `pip install -r requirements.txt`.
- **VS Code underlines the imports in yellow but the script runs fine.** That is Pylance
  pointing at a different Python than the one you installed into. `Ctrl+Shift+P` →
  *Python: Select Interpreter*. It is a squiggle, not an error.
- **Model.** `openai/gpt-oss-120b`. Groq deprecated `llama-3.3-70b-versatile` in June 2026,
  so do not copy that id in from session 6.
- **`reasoning_effort="low"`.** GPT-OSS is a reasoning model. `"low"` means think briefly,
  answer fast — right for a live debate. Raise it to `"high"` for sharper arguments and a
  much slower class.
- **429 rate limit.** Free tier. There is a `time.sleep(1)` between turns already; raise it
  if the whole room runs the demo at once.
- **Debate ends after 2 messages.** Your topic was probably not arguable — the models agree
  instantly on facts. Pick something with two real sides.
- **Nothing appears in the browser.** Open the `.html` **after** the script prints its path,
  not before — it does not exist until message 1.
- **`transcripts/` and `.env` are gitignored.** Each run overwrites the file for that topic.

---

## Student exercises

1. Swap the personas so **CON** opens the debate. What changes in the graph? (One edge.)
2. Add a third stance — a **NEUTRAL** agent that speaks every third turn.
3. Make `MAX_MESSAGES` 4 and watch the referee fire every time.
4. Print `len(pro_memory)` and `len(con_memory)` after each turn and explain why they differ.
5. Remove the `PHASE` lines from `persona()`. Do they ever agree on their own?

---

## Learn more

- LangGraph graph API — <https://docs.langchain.com/oss/python/langgraph/graph-api>
- ChatGroq — <https://docs.langchain.com/oss/python/integrations/chat/groq>
- Groq models and deprecations — <https://console.groq.com/docs/models>
