"""
Slides 36-44 — the `agent talks 2` folder: three A2A agents that disagree,
driven by LangGraph, plus the recap and closing slides.
"""

from pptx.enum.text import PP_ALIGN

from theme import (
    ORANGE, ORANGE_HI, ORANGE_DK, TINT, TINT2, INK, GRAY, GRAY_LT, LINE,
    WHITE, RED, GREEN, M, CW, W, H, BODY_TOP,
    slide, bullets, para, heading, code, box, table,
    chip, chip_row, arrow, label, rule, vrule, twocol,
)

XL, XR, HALF = twocol()



def _s36_intro(prs):
    s = slide(prs, "Part 6 · Agent Talks 2", "Same protocol, agents that disagree")

    para(s, M, BODY_TOP + 0.04, 7.15, 0.60,
         "Files 01–11 showed agents that **cooperate**: one question, one delegation, "
         "one answer. This folder points the same protocol at agents that "
         "~~argue~~ — until they have to land somewhere.", size=13.2)

    table(s, M, 2.28, 7.15, [
        ["Agent", "Skill", "Its job"],
        ["**Debate Agent (PRO)**", "`argue_for`", "argue the claim is TRUE"],
        ["**Debate Agent (CON)**", "`argue_against`", "argue the claim is FALSE"],
        ["**Debate Referee**", "`judge_debate`", "only hired if 20 messages pass with no agreement"],
    ], widths=[2.2, 1.7, 3.25], row_h=0.46)

    box(s, M, 4.16, 7.15, 1.00, "The claim",
        ["*\"Toyota is better than every other car brand.\"*   Same claim, opposite "
         "orders. Every arrow between them is a real `message/send`."], size=12.5)

    heading(s, 8.05, BODY_TOP + 0.04, CW - 7.50, "Peer to peer, plus a tiebreaker")
    chip(s, 8.05, 1.90, 2.20, 0.80, "PRO", sub="8010", size=13, fill=TINT2)
    chip(s, 10.60, 1.90, 2.20, 0.80, "CON", sub="8011", size=13, fill=TINT2)
    arrow(s, 10.32, 2.02, 0.22, 0.16, direction="right")
    arrow(s, 10.32, 2.38, 0.22, 0.16, direction="left")
    vrule(s, 10.44, 2.74, 0.42, color=ORANGE_HI, thick=0.028)
    chip(s, 9.20, 3.16, 2.45, 0.66, "Referee", sub="8012", size=12)
    label(s, 8.05, 3.94, CW - 7.50, "hired only when they run out of time",
          size=10.5, color=GRAY)

    box(s, 8.05, 4.32, CW - 7.50, 1.34, "It always ends agreed",
        ["Within **20 messages**, always with both agents on the same verdict — "
         "either they talk each other into it, or the referee breaks the tie."],
        size=12, fill=TINT2)

    box(s, M, 5.72, CW, 1.10, "One terminal, real A2A",
        ["These agents are Python objects instead of FastAPI servers, so the whole "
         "debate runs in one window. The **card fields, the JSON-RPC envelope and the "
         "Task object are byte-for-byte the A2A you already know** — and turning them "
         "into real servers is the 10 lines on slide 42."], size=12.5)


def _s37_agent_base(prs):
    s = slide(prs, "Part 6 · `debate_agent.py`", "Write the agent once, get three agents")

    code(s, XL, BODY_TOP + 0.06, HALF, None, [
        '    def __init__(self, name, description, url, skill,',
        '                 side, opening_verdict, persona_intro):',
        '        self.card = {                  # THE AGENT CARD',
        '            "name": name,',
        '            "description": description,',
        '            "url": url,',
        '            "version": "1.0.0",',
        '            "defaultInputModes":  ["text"],',
        '            "defaultOutputModes": ["text"],',
        '            "capabilities": {"streaming": False,',
        '                             "pushNotifications": False},',
        '            "skills": [skill]}',
        '        # NOT on the card. The card is public;',
        '        # the persona is private.',
        '        self.persona_intro = persona_intro',
        '        self.memory = {}   # contextId -> [messages]',
    ], size=10.5, title="class DebateAgent  —  the agent base")

    code(s, XR, BODY_TOP + 0.06, HALF, None, [
        '    # PROMISE 1 — discovery',
        '    def get_agent_card(self):',
        '        return self.card',
        '',
        '    # PROMISE 2 — the A2A endpoint',
        '    def handle_rpc(self, rpc):',
        '        method = rpc.get("method")',
        '        if method == "message/send":',
        '            return self._message_send(rpc)',
        '        if method == "tasks/get":',
        '            ...                  # look it up by id',
    ], size=10.5, title="the same two promises as file 02")

    code(s, XR, 4.42, HALF, None, [
        'class RefereeAgent(DebateAgent):',
        '    """A new agent is a new CARD and a new PERSONA',
        '    — not a new server, not a new protocol, not a',
        '    new memory system."""',
        '    def persona(self, count):',
        '        return "You are a neutral referee ..."',
        '',
        '# inherits discovery, message/send, tasks/get, Tasks',
    ], size=10.5, title="a third agent, for free")

    box(s, XL, 5.54, HALF, 1.28, "Why this file exists at all",
        ["Session 12 wrote the same server code five times (files 02, 04, 05, 07, 08). "
         "Here it is written **once** — `make_pro()`, `make_con()` and `make_referee()` "
         "are one call each.",
         "~~An agent is a card plus a persona.~~"], size=12.5)


def _s38_task_in_code(prs):
    s = slide(prs, "Part 6 · Tasks ⭐", "The Task lifecycle, in the code that runs it")

    code(s, XL, BODY_TOP + 0.06, HALF, None, [
        'def _message_send(self, rpc):',
        '    incoming   = rpc["params"]["message"]',
        '    context_id = incoming.get("contextId")',
        '    text_in    = incoming["parts"][0]["text"]',
        '',
        '    # a TASK is born the moment we accept work',
        '    task = {',
        '        "id":        _id("task"),',
        '        "contextId": context_id,',
        '        "status": {"state": "submitted",',
        '                   "timestamp": _now()},',
        '        "history":   [incoming],',
        '        "artifacts": [],',
        '        "kind":      "task",',
        '    }',
        '    self.tasks[task["id"]] = task',
        '',
        '    # MY memory for THIS debate',
        '    history = self.memory.setdefault(context_id, [])',
        '    history.append(HumanMessage(text_in))',
        '',
        '    task["status"] = {"state": "working", ...}',
    ], size=10.5, title="agent talks 2 / debate_agent.py")

    code(s, XR, BODY_TOP + 0.06, HALF, None, [
        '    # think',
        '    prompt = [SystemMessage(self.persona(count))]',
        '    prompt += history',
        '    for chunk in self.llm.stream(prompt):',
        '        reply_text += chunk.content',
        '    history.append(AIMessage(reply_text))',
        '',
        '    # working -> completed, result as an ARTIFACT',
        '    task["artifacts"] = [{"artifactId": ...,',
        '        "name": "argument", "parts": [...]}]',
    ], size=10.5, title="…and the ending")

    heading(s, XR, 4.24, HALF, "What the class watches happen")
    chip(s, XR, 4.56, HALF / 3 - 0.14, 0.60, "submitted", size=11)
    arrow(s, XR + HALF / 3 - 0.10, 4.75, 0.16, 0.22)
    chip(s, XR + HALF / 3 + 0.07, 4.56, HALF / 3 - 0.14, 0.60, "working",
         size=11, fill=TINT2)
    arrow(s, XR + 2 * HALF / 3 - 0.03, 4.75, 0.16, 0.22)
    chip(s, XR + 2 * HALF / 3 + 0.14, 4.56, HALF / 3 - 0.14, 0.60, "completed",
         size=11, fill=INK, edge=None, color=WHITE)
    label(s, XR, 5.26, HALF, "printed live in the terminal as  "
                             "`[a2a] task-3f9a1c2b -> completed`", size=11,
          color=ORANGE_DK)

    box(s, XR, 5.62, HALF, 1.20, "This is the slide that makes Tasks real",
        ["File 02 prints the **whole Task object**, calls `tasks/get` on it, then "
         "sends `make/coffee` for a genuine `-32601`.",
         "*\"A2A did not hand back a string. It handed back a job.\"*"], size=12.5,
        fill=TINT2)


def _s39_contextid(prs):
    s = slide(prs, "Part 6 · Context ⭐", "`contextId` **is** the memory")

    code(s, XL, BODY_TOP + 0.06, HALF, None, [
        'self.memory = {}          # contextId -> [messages]',
        '',
        'history = self.memory.setdefault(context_id, [])',
        'history.append(HumanMessage(text_in))',
        '...',
        'history.append(AIMessage(reply_text))',
        '',
        '# CONTEXT_ID = "ctx-debate-1"   for the whole debate',
    ], size=10.5, title="two lines that change how you think")

    bullets(s, XL, 3.86, HALF, 2.4, [
        "Each agent files its own history under the debate's `contextId`.",
        "*\"Each agent has its own memory\"* stops being a Python variable and becomes a ~~protocol idea~~ — which is why the same code works whether the agents share a process or sit on two continents.",
        "Neither dict is reachable from the other agent. They only ever received **text that arrived in a** `message/send`.",
    ], size=12.8)

    heading(s, XR, BODY_TOP + 0.06, HALF, "One conversation, two private memories")
    chip(s, XR + HALF / 4, 1.78, HALF / 2, 0.54, "`contextId`\n`ctx-debate-1`",
         size=11, fill=ORANGE_HI, edge=None)
    rule(s, XR + 1.25, 2.52, HALF - 2.5, color=ORANGE_HI, thick=0.028)
    vrule(s, XR + HALF / 2, 2.32, 0.20, color=ORANGE_HI, thick=0.028)
    for cx in (XR + 1.25, XR + HALF - 1.25):
        vrule(s, cx, 2.52, 0.24, color=ORANGE_HI, thick=0.028)

    chip(s, XR + 0.10, 2.76, HALF / 2 - 0.30, 1.30, "PRO's memory",
         sub="14 messages\n7 tasks handled", size=12, fill=TINT2)
    chip(s, XR + HALF / 2 + 0.20, 2.76, HALF / 2 - 0.30, 1.30, "CON's memory",
         sub="12 messages\n6 tasks handled", size=12, fill=TINT2)
    label(s, XR, 4.18, HALF, "different numbers, because they heard different things",
          size=11, color=GRAY)

    box(s, XR, 4.58, HALF, 1.10, "The proof runs at the end of file 04",
        ["It prints both counts and then: *\"Neither agent could read the other's "
         "memory. They only ever received text.\"*"], size=12.5)

    box(s, M, 6.06, CW, 0.76, "Where each id belongs",
        ["`messageId` — one turn.    `taskId` — one job.    `contextId` — the whole "
         "conversation, and the key every agent files its own memory under."],
        size=12.5, fill=TINT2)


def _s40_files_1_3(prs):
    s = slide(prs, "Part 6 · Files 01–03", "Cards, one Task, then two agents talking")

    heading(s, XL, BODY_TOP + 0.02, HALF, "01 · two cards, side by side")
    code(s, XL, 1.74, HALF, None, [
        'for agent in (pro, con):',
        '    card  = agent.get_agent_card()',
        '    skill = card["skills"][0]',
        '    print(f"  WHO   -> {card[\'name\']}")',
        '    print(f"  WHERE -> {card[\'url\']}")',
        '    print(f"  WHAT  -> {skill[\'name\']}  {skill[\'tags\']}")',
    ], size=10, fill=WHITE)

    heading(s, XL, 3.50, HALF, "02 · the reply is a Task, not a string")
    code(s, XL, 3.82, HALF, None, [
        'print(f"task id     : {task[\'id\']}")',
        'print(f"contextId   : {task[\'contextId\']}")',
        'print(f"final state : {task[\'status\'][\'state\']}")',
        'print(f"artifacts   : {task[\'artifacts\'][0][\'name\']}")',
        '',
        '# and then, by id:',
        'rpc = {"jsonrpc": "2.0", "id": 2, "method": "tasks/get",',
        '       "params": {"id": task["id"]}}',
    ], size=10, fill=WHITE)

    heading(s, XR, BODY_TOP + 0.02, HALF, "03 · the A2A communication flow, by hand")
    code(s, XR, 1.74, HALF, None, [
        'text = f\'The topic is: "{TOPIC}". Open the argument.\'',
        '',
        'for count in range(ROUNDS):',
        '    speaker = agents[count % 2]   # PRO, CON, PRO, CON',
        '    label   = "PRO" if count % 2 == 0 else "CON"',
        '',
        '    task  = send_message(speaker, text,',
        '                         context_id, count)',
        '    reply = task_text(task)',
        '    print(f"      task {task[\'id\']} -> "',
        '          f"{task[\'status\'][\'state\']}")',
        '',
        '    # THE WHOLE TRICK',
        '    text = f"{label} said: {reply}"',
    ], size=10, fill=WHITE)

    box(s, XR, 4.94, HALF, 0.94, "One line is the entire idea",
        ["`text = f\"{label} said: {reply}\"` — **one agent's answer becomes the "
         "other agent's question.**"], size=12.5, fill=TINT2)

    box(s, M, 5.98, CW, 0.84, "The one-line difference from a real server",
        ["`agent.handle_rpc(rpc)` today   ·   "
         "`requests.post(card[\"url\"], json=rpc).json()` as a real server. "
         "**Same envelope either way** — that is the whole point of the folder."],
        size=12.5)


def _s41_langgraph(prs):
    s = slide(prs, "Part 6 · File 04 ⭐", "LangGraph conducts. A2A carries.")

    code(s, XL, BODY_TOP + 0.06, HALF, None, [
        'class DebateState(TypedDict):',
        '    topic: str',
        '    last_text: str      # what the next agent hears',
        '    transcript: Annotated[list, operator.add]',
        '    pro_verdict: str    # "YES" / "NO" / ""',
        '    con_verdict: str',
        '    count: int          # messages spoken so far',
        '',
        '# LOOK AT WHAT IS NOT HERE: no message history.',
    ], size=10.5, title="1 · the state")

    code(s, XL, 4.06, HALF, None, [
        'def whose_turn(state):',
        '    if state["pro_verdict"] and \\',
        '       state["pro_verdict"] == state["con_verdict"]:',
        '        return END              # agreed -> stop early',
        '    if state["count"] >= MAX_MESSAGES:',
        '        return "referee"        # out of time',
        '    return ("con_turn" if state["count"] % 2 == 1',
        '            else "pro_turn")',
        '',
        'builder.add_conditional_edges("pro_turn", whose_turn,',
        '    ["con_turn", "referee", END])',
    ], size=10.5, title="2 · the conditional edge — the only reason a node repeats")

    heading(s, XR, BODY_TOP + 0.06, HALF, "3 · the graph")
    chip(s, XR + HALF / 2 - 0.65, 1.74, 1.30, 0.44, "START", size=11, fill=WHITE)
    arrow(s, XR + HALF / 2 - 0.09, 2.20, 0.18, 0.22, direction="down")
    chip(s, XR + 0.35, 2.48, HALF / 2 - 0.55, 0.58, "pro_turn", size=11.5, fill=TINT2)
    chip(s, XR + HALF / 2 + 0.20, 2.48, HALF / 2 - 0.55, 0.58, "con_turn",
         size=11.5, fill=TINT2)
    arrow(s, XR + HALF / 2 - 0.20, 2.56, 0.40, 0.16, direction="right")
    arrow(s, XR + HALF / 2 - 0.20, 2.86, 0.40, 0.16, direction="left")
    label(s, XR, 3.12, HALF, "every arrow above is a JSON-RPC `message/send`",
          size=10.5, color=ORANGE_DK)
    arrow(s, XR + HALF / 2 - 0.09, 3.42, 0.18, 0.22, direction="down")
    chip(s, XR + HALF / 4, 3.70, HALF / 2, 0.52, "referee", size=11.5)
    arrow(s, XR + HALF / 2 - 0.09, 4.26, 0.18, 0.22, direction="down")
    chip(s, XR + HALF / 2 - 0.65, 4.54, 1.30, 0.44, "END", size=11, fill=WHITE)

    box(s, XR, 5.10, HALF, 0.86, "The line to write on the board",
        ["**LangGraph = the conductor** (whose turn, are we done, who breaks a tie).   "
         "**A2A = the wire.**"], size=12.5, fill=TINT2)

    code(s, XR, 6.04, HALF, None, [
        'def relay(state, label):',
        '    task = send_message(agent, state["last_text"],',
        '                        CONTEXT_ID, state["count"])',
    ], size=10, fill=WHITE)


def _s42_watching(prs):
    s = slide(prs, "Part 6 · Running it", "How it always ends, and what to watch")

    heading(s, XL, BODY_TOP + 0.02, HALF, "The persona is rebuilt every single turn")
    table(s, XL, 1.74, HALF, [
        ["Messages so far", "The line injected into the system prompt"],
        ["0 – 9", "Argue hard. Do not concede."],
        ["10 – 14", "Name the strongest point your opponent made and say what is true about it."],
        ["15 – 20", "Time is nearly up. You **must** reach a shared verdict."],
    ], widths=[1.6, 4.3], row_h=0.52)

    box(s, XL, 3.72, HALF, 1.15, "Plus one rule that keeps it interesting",
        ["**Never repeat an argument you already used.** Without it they recycle three "
         "points for twenty messages. With it they work through reliability, safety, "
         "dealers, hybrids, resale — then honestly run out and concede."], size=12)

    box(s, XL, 5.00, HALF, 1.05, "A real run",
        ["13 messages. PRO conceded. Final answer **VERDICT: NO** — *\"they talked "
         "each other into it.\"*  The referee was never needed."], size=12.5,
        fill=TINT2)

    heading(s, XR, BODY_TOP + 0.02, HALF, "Turning them into real servers")
    code(s, XR, 1.74, HALF, None, [
        'from fastapi import FastAPI, Request',
        'from debate_agent import make_pro',
        '',
        'agent = make_pro("Toyota is better than ...")',
        'app = FastAPI()',
        '',
        '@app.get("/.well-known/agent-card.json")',
        'def card():',
        '    return agent.get_agent_card()',
    ], size=10.5, title="pro_server.py — nothing about the agent changes")

    code(s, XR, 4.28, HALF, None, [
        '@app.post("/")',
        'async def rpc(request: Request):',
        '    return agent.handle_rpc(await request.json())',
        '',
        'uvicorn.run(app, host="127.0.0.1", port=8010)',
    ], size=10.5, fill=WHITE)

    box(s, XR, 5.66, HALF, 1.16, "Three ways to watch it live",
        ["**Terminal** — each reply streams, then `[a2a] task-… -> completed`.",
         "**The `.html`** — open it *while it runs*; it reloads every 2 seconds.",
         "**`.md` and `.json`** — the debate as a document, and as data."],
        size=11.5)


def _s43_recap(prs):
    s = slide(prs, "Recap", "Everything, on one slide")

    box(s, M, BODY_TOP + 0.02, CW, 0.78, "The loop, in one breath",
        ["~~publish a card  →  discover it  →  `message/send`  →  read the reply.~~   "
         "Everything else is built on top of it."], size=13.5)

    table(s, XL, 2.42, HALF, [
        ["Object", "One line"],
        ["Agent Card", "the public résumé at `/.well-known/agent-card.json`"],
        ["Agent Skill", "one capability, with the `tags` others route on"],
        ["Message", "one turn — a `role` and a list of `parts`"],
        ["Part", "`text` · `file` · `data`"],
        ["Task", "a job with an `id` and a lifecycle"],
        ["Artifact", "what the agent produced, inside the Task"],
        ["`contextId`", "the conversation, and each agent's memory key"],
    ], widths=[1.7, 4.2], row_h=0.40)

    table(s, XR, 2.42, HALF, [
        ["Method", "When you need it"],
        ["`message/send`", "always — this *is* the protocol"],
        ["`message/stream`", "live partial answers over SSE"],
        ["`tasks/get`", "check on a job you started earlier"],
        ["`tasks/cancel`", "stop a long job"],
        ["`tasks/pushNotificationConfig/set`", "get a webhook when it finishes"],
        ["`agent/getAuthenticatedExtendedCard`", "the fuller card, after logging in"],
        ["`-32601`", "the error every unknown method gets"],
    ], widths=[3.0, 2.9], row_h=0.40)

    box(s, M, 5.60, CW, 1.22, "The three questions students always ask",
        ["*\"Is A2A the same as MCP?\"*  No. **MCP = agent → tool. A2A = agent → agent.** Complementary.",
         "*\"Does the client need to know how the other agent works inside?\"*  No — it reads the card and sends messages. That opacity is the design.",
         "*\"Do both agents need the same framework or LLM?\"*  No. That is the entire point."],
        size=12)


def _s44_close(prs):
    s = slide(prs, "Your turn", "Nine things to go and build")

    heading(s, XL, BODY_TOP + 0.02, HALF, "On the eleven files")
    bullets(s, XL, 1.72, HALF, 2.5, [
        "**Add a third agent.** Copy `04_weather_agent.py` into a `math_agent` on port 8004 with skill `add`, and add it to `KNOWN_AGENTS`. Zero changes to the other agents.",
        "**Add a second skill** to the weather agent (`get_forecast`) and show it on the card.",
        "**Make a reply stream.** Set `\"streaming\": true` and return chunks via `message/stream`.",
        "**Go cross-machine.** Point your orchestrator at a classmate's agent URL.",
    ], size=12.2)

    heading(s, XR, BODY_TOP + 0.02, HALF, "On `agent talks 2`")
    bullets(s, XR, 1.72, HALF, 2.9, [
        "**Make them real servers** with the 10-line snippet, and swap the one line in `send_message`.",
        "**Add a fourth agent** — a `fact_checker` with skill `check_claim`, subclassing `DebateAgent` the way `RefereeAgent` does.",
        "**Route by skill, not by name** — scan `card[\"skills\"][0][\"tags\"]` for `for` / `against`, the way file 06 does.",
        "**Implement `message/stream`** — make `handle_rpc` a generator yielding status and artifact updates.",
        "**Persist the tasks** so `tasks/get` still works after a restart.",
    ], size=12.2)

    rule(s, M, 5.06, CW, color=LINE)

    box(s, XL, 5.24, HALF, 1.05, "Where to read more",
        ["Spec and tutorials — `a2a-protocol.org`      ·      "
         "Python SDK — `pip install a2a-sdk==1.1.1`"], size=12)

    label(s, XR, 5.42, HALF, "AI Season", size=17, color=ORANGE)
    label(s, XR, 5.80, HALF, "Abdul Rahman Azam", size=14, color=INK)
    label(s, XR, 6.10, HALF, "Session 12  ·  Agent-to-Agent (A2A) Communication",
          size=11.5, color=GRAY)


def build(prs):
    _s36_intro(prs)
    _s37_agent_base(prs)
    _s38_task_in_code(prs)
    _s39_contextid(prs)
    _s40_files_1_3(prs)
    _s41_langgraph(prs)
    _s42_watching(prs)
    _s43_recap(prs)
    _s44_close(prs)
