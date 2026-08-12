"""
Slides 1-23 — why A2A exists, how it compares to MCP and plain APIs, the
multi-agent picture, and every object in the protocol (Card, Skills, Discovery,
Messages, Tasks, Artifacts) ending with the communication flow.
"""

from pptx.enum.text import PP_ALIGN

from theme import (
    ORANGE, ORANGE_HI, ORANGE_DK, TINT, TINT2, INK, GRAY, GRAY_LT, LINE,
    WHITE, RED, GREEN, M, CW, W, BODY_TOP,
    slide, title_slide, bullets, para, heading, code, box, table,
    chip, chip_row, arrow, label, rule, vrule, grid, twocol,
)

XL, XR, HALF = twocol()


# =====================================================================
#  PART 1 — WHY  (1-7)
# =====================================================================

def _s01_title(prs):
    title_slide(
        prs,
        "Agent-to-Agent (A2A) Communication",
        "How agents built by different teams, frameworks and companies "
        "discover each other and hand off work",
        "Abdul Rahman Azam",
        "AI Season",
        meta=["Session 12",
              "11 files + a live debate demo",
              "Python · FastAPI · Groq · a2a-sdk"],
    )


def _s02_agenda(prs):
    s = slide(prs, "Roadmap", "What we are building today")

    chip_row(s, M, 1.62, CW, 1.02,
             [("WHY", "the silo problem"),
              ("VOCABULARY", "card · task · artifact"),
              ("BY HAND", "40 lines, no SDK"),
              ("REAL BRAINS", "Groq LLM agents"),
              ("THE SDK", "a2a-sdk 1.1")],
             gap=0.30, size=12.5)

    table(s, M, 3.00, CW, [
        ["Part", "What you will be able to do after it", "Files", "Min"],
        ["0 · Why A2A exists", "Explain why agents cannot just call each other's APIs", "—", "5"],
        ["1 · The vocabulary", "Read any Agent Card and name every field", "01", "10"],
        ["2 · Build one by hand", "Write a working A2A agent + client with no SDK", "02, 03", "20"],
        ["3 · Two agents collaborating", "Discover specialists and delegate to the right one", "04, 05, 06", "20"],
        ["4 · Give them real brains", "Swap the brain without touching the client", "07, 08, 09", "10"],
        ["5 · Meet the real SDK", "Map every SDK piece back to what you built", "10, 11", "8"],
        ["6 · Agents that disagree", "Run a 3-agent debate over the same protocol", "agent talks 2", "12"],
    ], widths=[2.5, 6.2, 2.1, 0.8], row_h=0.36)

    box(s, M, 6.05, CW, 0.78, "The one line to remember",
        "~~MCP = agent to tool.   A2A = agent to agent.~~   Real systems use both together.",
        size=13.5)


def _s03_why_talk(prs):
    s = slide(prs, "Part 1 · Why", "Why do agents need to talk to each other?")

    bullets(s, XL, BODY_TOP + 0.06, HALF, 4.6, [
        "You already know how to give **one** agent tools. But the thing your agent needs help from is often ~~another whole agent~~ — built by a different company, running on a different framework, that you cannot see inside.",
        "A **travel** AI, a **weather** AI and a **currency** AI are each smart on their own. None of them can help the others.",
        (1, "different teams, different codebases"),
        (1, "different LLMs, different frameworks"),
        (1, "no shared memory, no shared variables"),
        "One real user question crosses all three. Somebody has to make them cooperate.",
        "Before A2A you wrote **custom glue code for every pair**. That does not scale.",
    ], size=13.2)

    heading(s, XR, BODY_TOP + 0.02, HALF, "Three agents, three silos")
    chip_row(s, XR, 1.90, HALF, 0.92,
             [("Travel AI", "plans trips"),
              ("Weather AI", "forecasts"),
              ("Currency AI", "converts")],
             gap=0.42, arrows=False, size=12)

    # the crossed-out links between them
    for gx in (XR + (HALF - 0.84) / 3 + 0.10, XR + 2 * ((HALF - 0.84) / 3 + 0.42) - 0.32):
        label(s, gx, 2.24, 0.42, "✕", size=20, color=RED)

    box(s, XR, 3.15, HALF, 1.58, "The user asks one question",
        ["*\"I fly to Tokyo tomorrow — what is the weather there, and what is "
         "100 USD in yen?\"*",
         "No single agent can answer it. And none of them knows the others exist."],
        size=12.5, fill=TINT2)

    box(s, XR, 4.90, HALF, 1.92, "What is missing",
        ["A shared way to answer two questions:",
         "**1.  Who are you and what can you do?**",
         "**2.  How do I send you work and get the result back?**",
         "That is exactly what A2A standardises — like HTTP did for web servers."],
        size=12.5)


def _s04_nxm(prs):
    s = slide(prs, "Part 1 · Why", "Before A2A: custom glue for every single pair")

    heading(s, XL, BODY_TOP + 0.02, HALF, "Without a protocol  —  N × M")
    label(s, XL, 1.78, HALF, "every cell is glue code somebody has to write and maintain",
          size=10.5, color=GRAY, align=PP_ALIGN.LEFT)

    names = ["Travel", "Weather", "Currency", "Booking"]
    fills, texts = [], []
    for r in range(4):
        frow, trow = [], []
        for c in range(4):
            if r == c:
                frow.append(WHITE)
                trow.append("—")
            else:
                frow.append(TINT2)
                trow.append("glue")
        fills.append(frow)
        texts.append(trow)
    grid(s, XL + 1.55, 2.35, 0.66, [[0] * 4] * 4, fills=fills, texts=texts,
         size=9, head_cols=names, head_rows=names)

    label(s, XL, 5.15, HALF, "4 agents  =  **12** one-way integrations        "
                             "10 agents  =  **90**", size=12.5, color=INK,
          align=PP_ALIGN.LEFT)

    heading(s, XR, BODY_TOP + 0.02, HALF, "With A2A  —  N")
    label(s, XR, 1.78, HALF, "each agent learns one protocol, once, and is done",
          size=10.5, color=GRAY, align=PP_ALIGN.LEFT)

    n, gap = 4, 0.24
    cw = (HALF - gap * (n - 1)) / n
    for i, name in enumerate(names):
        cx = XR + i * (cw + gap)
        chip(s, cx, 2.55, cw, 0.72, name, size=11.5)
        arrow(s, cx + cw / 2 - 0.09, 3.32, 0.18, 0.44, direction="down")

    bar = chip(s, XR, 3.86, HALF, 0.80, "A2A — one shared protocol",
               fill=ORANGE_HI, edge=None, size=14)
    del bar

    label(s, XR, 4.82, HALF, "4 agents  =  **4** integrations        "
                             "10 agents  =  **10**", size=12.5, color=INK,
          align=PP_ALIGN.LEFT)

    box(s, XR, 5.35, HALF, 1.20, "Why not just call their REST API?",
        ["Because an agent is not an endpoint. It **reasons**, it takes minutes, "
         "it asks you follow-up questions, and its owner will not show you its "
         "prompt. A2A is built for that; a REST call is not."],
        size=12)


def _s05_what_is_a2a(prs):
    s = slide(prs, "Part 1 · Why", "So what exactly is A2A?")

    para(s, M, BODY_TOP + 0.04, CW, 0.72,
         "A2A (**Agent2Agent**) is an ~~open standard for communication between AI agents~~. "
         "An agent publishes a small JSON résumé at a fixed web address; any other agent "
         "reads it and sends it work over plain HTTP. Nothing else is required.", size=14)

    table(s, M, 2.32, CW, [
        ["Design principle", "What the spec says", "What it means for you"],
        ["Simple", "Reuse existing, well-understood standards", "HTTP, JSON-RPC 2.0, Server-Sent Events — no new wire format to learn"],
        ["Enterprise ready", "Auth, authorization, security, privacy, tracing", "Agent Cards carry security schemes; cards can be signed"],
        ["Async first", "Designed for (potentially very) long-running tasks", "A job can run for hours; you poll it or get a webhook"],
        ["Modality agnostic", "Support exchange of diverse content types", "Text, files and structured data are all just \"parts\""],
        ["Opaque execution", "Collaborate without sharing internal thoughts", "You never see the other agent's prompt, model, tools or memory"],
    ], widths=[2.1, 4.2, 5.9], row_h=0.50)

    box(s, M, 5.72, HALF, 1.10, "Who runs it",
        ["A **Linux Foundation** project, not a single vendor's. v1.0 shipped in 2026, "
         "150+ organisations, SDKs in Python, JavaScript, Java, Go and .NET."], size=12)
    box(s, XR, 5.72, HALF, 1.10, "The transport",
        ["`HTTP(S)` is required. An agent must speak at least one of "
         "**JSON-RPC 2.0**, **gRPC**, or **HTTP+JSON/REST**. This course uses JSON-RPC."],
        size=12)


def _s06_vs(prs):
    s = slide(prs, "Part 1 · Why", "A2A vs MCP vs a plain API")

    xw = (CW - 0.6) / 3
    for i, (top, mid, bot, tint) in enumerate([
        ("Your app", "REST API", "a server", WHITE),
        ("An agent", "MCP", "a tool", TINT),
        ("An agent", "A2A", "another agent", TINT2),
    ]):
        x = M + i * (xw + 0.3)
        chip(s, x, 1.52, xw, 0.46, top, size=11)
        arrow(s, x + xw / 2 - 0.08, 2.02, 0.16, 0.26, direction="down")
        chip(s, x, 2.32, xw, 0.46, mid, fill=ORANGE_HI if i == 2 else tint,
             edge=ORANGE, size=11.5)
        arrow(s, x + xw / 2 - 0.08, 2.82, 0.16, 0.26, direction="down")
        chip(s, x, 3.12, xw, 0.46, bot, size=11)

    table(s, M, 3.86, CW, [
        ["", "Plain API", "MCP", "A2A"],
        ["Connects", "an app to a server", "an agent to its tools and data", "an agent to another agent"],
        ["The other side is", "code you call", "a function you own", "a peer that reasons for itself"],
        ["How you find it", "you read the docs", "the server lists its tools", "you fetch its Agent Card"],
        ["Unit of work", "a request", "a tool call", "a Message, or a Task with a lifecycle"],
        ["Who decides how", "you do", "you do", "**the other agent does**"],
        ["Think of it as", "a vending machine", "giving a worker a toolbox", "workers phoning and hiring each other"],
    ], widths=[1.7, 2.7, 3.5, 4.3], row_h=0.37)

    label(s, M, 6.58, CW, "They are ~~complementary~~ — a real system uses MCP inside "
                          "each agent and A2A between them.", size=12.5, color=INK,
          align=PP_ALIGN.LEFT)


def _s07_when(prs):
    s = slide(prs, "Part 1 · Why", "The same capability, packaged two ways")

    heading(s, XL, BODY_TOP + 0.02, HALF, "Session 6  —  `get_weather` was a TOOL")
    chip(s, XL + 0.55, 1.86, HALF - 1.1, 2.05, "", fill=TINT, edge=ORANGE)
    label(s, XL + 0.55, 1.98, HALF - 1.1, "One agent", size=12, color=ORANGE)
    chip(s, XL + 1.05, 2.34, HALF - 2.1, 0.52, "the LLM", size=11)
    arrow(s, XL + HALF / 2 - 0.09, 2.92, 0.18, 0.28, direction="down")
    chip(s, XL + 1.05, 3.24, HALF - 2.1, 0.52, "`get_weather()`", size=11, fill=TINT2)
    label(s, XL, 4.02, HALF, "one process · one codebase · you wrote both halves",
          size=11, color=GRAY)

    heading(s, XR, BODY_TOP + 0.02, HALF, "Session 12  —  it is its OWN AGENT")
    chip(s, XR + 0.10, 1.86, HALF / 2 - 0.35, 1.00, "Orchestrator",
         sub="reads cards, delegates", size=11.5)
    chip(s, XR + HALF / 2 + 0.25, 1.86, HALF / 2 - 0.35, 1.00, "Weather Agent",
         sub="port 8002, own card", size=11.5, fill=TINT2)
    arrow(s, XR + HALF / 2 - 0.20, 2.16, 0.42, 0.18, direction="right")
    label(s, XR, 3.00, HALF, "`message/send`  over HTTP", size=11, color=ORANGE_DK)
    label(s, XR, 3.32, HALF, "two processes · two codebases · could be two companies",
          size=11, color=GRAY)
    label(s, XR, 4.02, HALF, "the orchestrator has ~~no idea~~ what is inside",
          size=11.5, color=INK)

    box(s, M, 4.55, CW, 0.92, "Say this out loud",
        ["*\"That jump — from a **tool you own** to a **separate agent you talk to** — "
         "is agent-to-agent. Everything else in this session is detail.\"*"], size=13)

    table(s, M, 5.68, CW, [
        ["Use a plain API when…", "Use MCP when…", "Use A2A when…"],
        ["the other side is deterministic code and you just want the data back",
         "your own agent needs a tool, a file or a database it can call directly",
         "the other side is an autonomous agent that reasons, is owned by someone else, or takes a long time"],
    ], widths=[3.6, 3.9, 4.7], row_h=0.72)


# =====================================================================
#  PART 2 — ARCHITECTURE + VOCABULARY  (8-10)
# =====================================================================

def _s08_architecture(prs):
    s = slide(prs, "Part 2 · Architecture", "Multi-Agent Architecture — the three actors")

    label(s, M, BODY_TOP + 0.02, CW, "A client is not a special program — "
                                     "**an agent acting as a client is still an agent**.",
          size=12.8, color=INK, align=PP_ALIGN.LEFT)

    chip(s, 0.75, 1.85, 2.05, 0.85, "User", sub="asks for something", size=13)
    arrow(s, 2.95, 2.16, 0.55, 0.22)
    chip(s, 3.65, 1.85, 3.05, 0.85, "A2A Client", sub="the agent that starts it",
         size=13, fill=TINT)
    arrow(s, 6.85, 2.16, 1.45, 0.22)
    chip(s, 8.45, 1.85, 3.85, 1.55, "A2A Server\n(Remote Agent)", size=13,
         fill=TINT2)
    label(s, 6.75, 1.82, 1.65, "HTTP(S)\nJSON-RPC 2.0", size=10, color=ORANGE_DK)

    # what the client cannot see
    inner = chip(s, 8.45, 3.62, 3.85, 1.55, "", fill=WHITE, edge=GRAY_LT)
    del inner
    label(s, 8.45, 3.72, 3.85, "everything below is INVISIBLE to the client",
          size=9.5, color=GRAY_LT)
    for i, t in enumerate(["its LLM", "its tools", "its memory"]):
        chip(s, 8.62 + i * 1.19, 4.05, 1.08, 0.44, t, size=9.5, fill=TINT,
             edge=LINE, bold=False)
    label(s, 8.45, 4.60, 3.85, "~~opaque execution~~", size=11.5, color=ORANGE)
    vrule(s, 10.37, 3.40, 0.22, color=GRAY_LT)

    table(s, M, 5.42, CW, [
        ["Actor", "Official definition", "In our code"],
        ["A2A Client", "The application or agent that initiates requests on behalf of a user",
         "`06_orchestrator.py`, `03_greeting_client.py`"],
        ["A2A Server (Remote Agent)", "An agent that exposes an A2A-compliant HTTP endpoint and does the work",
         "`04_weather_agent.py`, `05_currency_agent.py`"],
    ], widths=[2.6, 5.6, 4.0], row_h=0.48)


def _s09_topologies(prs):
    s = slide(prs, "Part 2 · Architecture", "Three shapes a multi-agent system takes")

    xw = (CW - 0.7) / 3

    # 1 — orchestrator / worker
    x = M
    heading(s, x, BODY_TOP + 0.06, xw, "1 · Orchestrator – worker")
    chip(s, x + xw / 2 - 1.05, 1.92, 2.10, 0.60, "Orchestrator", size=11.5, fill=TINT2)
    rule(s, x + 0.45, 2.82, xw - 0.9, color=ORANGE_HI, thick=0.028)
    vrule(s, x + xw / 2, 2.52, 0.30, color=ORANGE_HI, thick=0.028)
    for i in range(3):
        cx = x + 0.45 + i * ((xw - 0.9) / 2)
        vrule(s, cx, 2.82, 0.26, color=ORANGE_HI, thick=0.028)
    for i, t in enumerate(["Weather", "Currency", "Maths"]):
        chip(s, x + 0.05 + i * ((xw - 0.1) / 3), 3.08, (xw - 0.1) / 3 - 0.14, 0.54,
             t, size=10)
    label(s, x, 3.78, xw, "one hires many · **file 06**", size=11, color=INK)
    label(s, x, 4.08, xw, "the shape 90% of systems use", size=10.5, color=GRAY)

    # 2 — peer to peer
    x = M + xw + 0.35
    heading(s, x, BODY_TOP + 0.06, xw, "2 · Peer to peer")
    chip(s, x + 0.10, 2.20, xw / 2 - 0.35, 0.70, "PRO", size=11.5, fill=TINT2)
    chip(s, x + xw / 2 + 0.25, 2.20, xw / 2 - 0.35, 0.70, "CON", size=11.5, fill=TINT2)
    arrow(s, x + xw / 2 - 0.22, 2.28, 0.46, 0.16, direction="right")
    arrow(s, x + xw / 2 - 0.22, 2.60, 0.46, 0.16, direction="left")
    chip(s, x + xw / 4 + 0.10, 3.15, xw / 2, 0.54, "Referee", size=10.5)
    label(s, x, 3.86, xw, "each answers the other · **agent talks 2**", size=11, color=INK)
    label(s, x, 4.16, xw, "debate, negotiation, review", size=10.5, color=GRAY)

    # 3 — pipeline
    x = M + 2 * (xw + 0.35)
    heading(s, x, BODY_TOP + 0.06, xw, "3 · Pipeline")
    for i, t in enumerate(["Research", "Write", "Edit"]):
        cy = 1.92 + i * 0.72
        chip(s, x + 0.35, cy, xw - 0.7, 0.54, t, size=11)
        if i < 2:
            arrow(s, x + xw / 2 - 0.09, cy + 0.56, 0.18, 0.14, direction="down")
    label(s, x, 4.16, xw, "output of one is input of the next", size=11, color=INK)

    box(s, M, 4.70, CW, 0.95, "The only thing that changes between them",
        ["**Who calls `message/send`, and in what order.** The protocol, the cards and "
         "the Task objects are identical in all three. That is why one `DebateAgent` "
         "class can play any role."], size=12.5)

    table(s, M, 5.88, CW, [
        ["Topology", "Who decides what happens next", "You will see it in"],
        ["Orchestrator – worker", "one central agent routes every question",
         "`06_orchestrator.py` · `09_llm_orchestrator.py`"],
        ["Peer to peer", "the agents themselves, turn by turn",
         "`agent talks 2 / 03_two_agents_talk.py`"],
    ], widths=[2.8, 5.0, 4.4], row_h=0.34)


def _s10_vocabulary(prs):
    s = slide(prs, "Part 2 · Vocabulary", "The eight words you need")

    table(s, M, BODY_TOP + 0.06, CW, [
        ["Word", "What it is", "Where you will meet it"],
        ["Agent Card", "A JSON résumé: identity, endpoint, skills, capabilities, auth",
         "`/.well-known/agent-card.json` — file 01"],
        ["Agent Skill", "One thing the agent can do, with `id`, `tags` and `examples`",
         "`skills[0]` in every card — file 04"],
        ["Message", "One turn of the conversation. Has a `role` and a list of `parts`",
         "`params.message` — file 03"],
        ["Part", "The smallest content unit: `text`, `file` or `data`",
         "`parts[0]` — every single call"],
        ["Task", "A stateful unit of work with an `id` and a lifecycle",
         "the `result` of `message/send` — agent talks 2"],
        ["Artifact", "The finished output the agent produced for a task",
         "`task[\"artifacts\"][0]` — agent talks 2"],
        ["Context (`contextId`)", "The id that groups related tasks into one conversation",
         "`ctx-debate-1` — agent talks 2"],
        ["Client / Server", "Who starts the call / who does the work",
         "orchestrator / specialist — file 06"],
    ], widths=[2.3, 5.4, 4.5], row_h=0.46)

    box(s, M, 5.96, CW, 0.86, "Two of these trip everyone up",
        ["A **Message** is a turn of talk; a **Task** is a job with a state. Simple agents "
         "reply with a Message; working agents reply with a Task, and the answer lives "
         "in its **Artifact**."], size=12.5)


# =====================================================================
#  PART 3 — THE OBJECTS  (11-22)
# =====================================================================

def _s11_card_idea(prs):
    s = slide(prs, "Part 3 · Agent Card", "The Agent Card — an agent's résumé")

    para(s, M, BODY_TOP + 0.04, CW, 0.5,
         "Before two agents can work together they must answer one question: "
         "~~\"Who are you, and what can you do?\"~~  A2A answers it with a single "
         "JSON file every agent publishes about itself.", size=13.5)

    # the card, drawn as a card
    cx, cw = 0.9, 5.3
    card = chip(s, cx, 2.20, cw, 3.55, "", fill=WHITE, edge=ORANGE)
    del card
    label(s, cx, 2.34, cw, "AGENT CARD", size=11, color=ORANGE)
    rule(s, cx + 0.3, 2.66, cw - 0.6, color=LINE)

    for i, (q, a, sub) in enumerate([
        ("WHO", "Weather Agent", "`name` · `description` · `version`"),
        ("WHERE", "http://localhost:8002/", "`url` — POST your messages here"),
        ("WHAT", "get_weather", "`skills[]` — with tags others match on"),
    ]):
        y = 2.84 + i * 0.94
        chip(s, cx + 0.30, y, 1.15, 0.72, q, size=11.5, fill=ORANGE_HI, edge=None)
        label(s, cx + 1.60, y + 0.06, cw - 1.95, a, size=13, color=INK,
              align=PP_ALIGN.LEFT)
        label(s, cx + 1.60, y + 0.36, cw - 1.95, sub, size=10.5, color=GRAY,
              align=PP_ALIGN.LEFT)

    bullets(s, 6.65, 2.24, CW - 6.10, 3.0, [
        "It is **public**. Anyone may read it — that is the point.",
        "It is **not** where your prompt goes. The card is the outside of the agent; the prompt is the inside.",
        "It lives at one fixed path so nobody has to be told where to look:",
        (1, "`https://<host>/.well-known/agent-card.json`"),
        "Every field exists to answer a client's question: *should I hire this agent, and how exactly do I talk to it?*",
    ], size=13)

    box(s, 6.65, 5.35, CW - 6.10, 1.40, "If you remember one thing",
        ["*\"If you know one thing about A2A, know this file.\"*  Publish a card and "
         "answer `message/send` — that is a valid A2A agent. Everything else is optional."],
        size=12.5, fill=TINT2)


def _s12_card_fields(prs):
    s = slide(prs, "Part 3 · Agent Card", "What is inside an Agent Card")

    table(s, M, BODY_TOP + 0.02, 6.55, [
        ["Field", "What it holds"],
        ["`protocolVersion`", "which A2A version this agent speaks"],
        ["`name` · `description`", "who it is, in plain words"],
        ["`url`", "the endpoint you POST messages to"],
        ["`preferredTransport`", "`JSONRPC` (default) · `GRPC` · `HTTP+JSON`"],
        ["`additionalInterfaces`", "other transport + URL pairs it also serves"],
        ["`version`", "the agent's own version, not the protocol's"],
        ["`provider`", "the organisation behind it"],
        ["`capabilities`", "streaming? push notifications? extensions?"],
        ["`defaultInputModes` / `OutputModes`", "the MIME types it takes and returns"],
        ["`skills`", "**the heart of the card** — what it can do"],
        ["`securitySchemes` · `security`", "how to authenticate to it"],
        ["`signatures`", "JSON Web Signatures proving the card is genuine"],
    ], widths=[2.5, 4.05], row_h=0.36, size=10.5)

    heading(s, 7.35, BODY_TOP + 0.02, CW - 6.80, "What session 12 actually uses")
    code(s, 7.35, 1.78, CW - 6.80, None, [
        '"name":              "Weather Agent",',
        '"description":       "Tells the weather.",',
        '"version":           "1.0.0",',
        '"url":               "http://localhost:8002/",',
        '"defaultInputModes":  ["text"],',
        '"defaultOutputModes": ["text"],',
        '"capabilities": {...},',
        '"skills":       [...]',
    ], size=10.5, title="the minimum viable card  —  a real, discoverable agent")

    box(s, 7.35, 4.18, CW - 6.80, 1.25, "Why the rest is missing",
        ["Every other field is **optional**. Add `securitySchemes` when the agent "
         "goes on a real network; add `signatures` when clients must prove the card "
         "was not swapped."], size=12)

    box(s, 7.35, 5.59, CW - 6.80, 1.23, "Careful",
        ["`version` is *your agent's* version. `protocolVersion` is *A2A's* version. "
         "They are different fields and people mix them up constantly."], size=12,
        fill=TINT2)


def _s13_card_code(prs):
    s = slide(prs, "Part 3 · Agent Card", "File 01 — the card, in code")

    code(s, XL, BODY_TOP + 0.06, HALF, None, [
        'agent_card = {',
        '    # --- WHO am I? ---',
        '    "name": "Weather Agent",',
        '    "description": "Tells the current weather.",',
        '    "version": "1.0.0",',
        '',
        '    # --- WHERE do you reach me? ---',
        '    "url": "http://localhost:8002/",',
        '',
        '    # --- HOW do we talk? ---',
        '    "defaultInputModes": ["text"],',
        '    "defaultOutputModes": ["text"],',
        '',
        '    # --- WHICH features do I support? ---',
        '    "capabilities": {',
        '        "streaming": False,',
        '        "pushNotifications": False,',
        '    },',
        '',
        '    # --- WHAT can I actually do? ---',
        '    "skills": [ ... ],',
        '}',
    ], size=10.5, title="01_what_is_an_agent_card.py")

    heading(s, XR, BODY_TOP + 0.06, HALF, "What it prints")
    code(s, XR, 1.78, HALF, None, [
        'Every card answers 3 questions:',
        '  1. WHO   -> Weather Agent',
        '  2. WHERE -> http://localhost:8002/',
        '  3. WHAT  -> [\'Get weather\']',
        '',
        'In real life published at:',
        '  .../.well-known/agent-card.json',
    ], size=10.5, fill=WHITE)

    box(s, XR, 3.72, HALF, 1.25, "No server, no LLM, no network",
        ["File 01 starts nothing. It builds one dictionary and prints it, so the "
         "JSON stops looking scary before we put it behind a web server in file 02."],
        size=12.5)

    box(s, XR, 5.10, HALF, 1.72, "The three questions, every time",
        ["**WHO** — so a human can tell what they hired.",
         "**WHERE** — so a machine knows where to POST.",
         "**WHAT** — so a machine can decide *whether* to POST at all."], size=12.5,
        fill=TINT2)


def _s14_skills(prs):
    s = slide(prs, "Part 3 · Agent Skills", "Agent Skills — and why `tags` decide everything")

    table(s, M, BODY_TOP + 0.04, 5.9, [
        ["Field", "What it is for"],
        ["`id`", "machine name, unique within the agent"],
        ["`name`", "human name, shown in a directory"],
        ["`description`", "what an LLM router reads to choose"],
        ["`tags`", "**keywords other agents match against**"],
        ["`examples`", "sample prompts that should hit this skill"],
        ["`inputModes` / `outputModes`", "override the card defaults for this skill"],
    ], widths=[2.3, 3.6], row_h=0.36)

    code(s, M, 4.16, 5.9, None, [
        '# 04_weather_agent.py',
        '"id":   "get_weather",',
        '"tags": ["weather", "forecast",',
        '         "temperature", "rain"],',
        '',
        '# 05_currency_agent.py',
        '"id":   "convert_currency",',
        '"tags": ["currency", "convert",',
        '         "exchange", "money", "forex"],',
    ], size=10.5, title="two skills, two tag lists")

    heading(s, XR, BODY_TOP + 0.04, HALF, "How a tag becomes a routing decision")
    chip(s, XR, 1.82, HALF, 0.62, '"Is it raining in London?"', size=12.5, fill=WHITE)
    arrow(s, XR + HALF / 2 - 0.09, 2.52, 0.18, 0.34, direction="down")
    chip(s, XR, 2.94, HALF, 0.62, 'scan every card\'s `skill["tags"]`',
         size=12.5, fill=TINT)
    arrow(s, XR + HALF / 2 - 0.09, 3.64, 0.18, 0.34, direction="down")
    chip(s, XR, 4.06, HALF / 2 - 0.15, 0.72, "Weather Agent",
         sub="\"rain\" matched", size=12, fill=ORANGE_HI, edge=None)
    chip(s, XR + HALF / 2 + 0.15, 4.06, HALF / 2 - 0.15, 0.72, "Currency Agent",
         sub="no tag matched", size=12, fill=WHITE, edge=GRAY_LT)

    box(s, XR, 5.05, HALF, 1.05, "Pick tags like a search engine would",
        ["The question said \"raining\", not \"weather\". The tag `rain` is what "
         "saved the routing. Thin tag lists are the number-one reason delegation fails."],
        size=12)

    box(s, XR, 6.20, HALF, 0.62, "Tags are a hint, not a contract",
        ["An LLM router (file 09) reads `description` instead."], size=12, fill=TINT2)


def _s15_capabilities(prs):
    s = slide(prs, "Part 3 · Agent Card", "`capabilities` — what the agent opts into")

    para(s, M, BODY_TOP + 0.04, CW, 0.44,
         "Four booleans that tell a client which *optional* parts of the protocol "
         "it may use. Declaring them is a promise: if you say `streaming: true`, "
         "you must actually serve `message/stream`.", size=13.2)

    xw = (CW - 0.9) / 4
    for i, (name, unlocks, how) in enumerate([
        ("streaming", "`message/stream`", "partial answers pushed live over Server-Sent Events"),
        ("pushNotifications", "`tasks/pushNotificationConfig/set`", "the agent calls your webhook when a long job finishes"),
        ("stateTransitionHistory", "the full `history`", "the client can replay every state the task passed through"),
        ("extensions", "custom behaviour", "agreed extras, declared by URI, beyond base A2A"),
    ]):
        x = M + i * (xw + 0.3)
        chip(s, x, 2.10, xw, 0.62, name, size=11.5, fill=TINT2)
        arrow(s, x + xw / 2 - 0.08, 2.80, 0.16, 0.26, direction="down")
        chip(s, x, 3.14, xw, 0.56, unlocks, size=10, fill=WHITE)
        label(s, x, 3.82, xw, how, size=10.5, color=GRAY)

    code(s, XL, 4.72, HALF, None, [
        '"capabilities": {',
        '    "streaming": False,',
        '    "pushNotifications": False,',
        '},',
        '',
        '# both false, on purpose',
    ], size=11, title="every card in session 12")

    box(s, XR, 4.72, HALF, 1.82, "Why we say false",
        ["Our agents answer in one shot, so there is nothing to stream and no long "
         "job to call back about. **Declaring a feature you have not built is worse "
         "than not declaring it** — a client will try to use it and fail.",
         "Exercise 3 in the lesson guide flips `streaming` to `true` and makes the "
         "reply arrive word by word."], size=12.5)


def _s16_discovery(prs):
    s = slide(prs, "Part 3 · Discovery", "Agent Discovery — one fixed address")

    chip(s, 0.75, 1.80, 2.9, 0.72, "A2A Client", size=12.5, fill=TINT)
    chip(s, 9.60, 1.80, 2.75, 0.72, "Remote Agent", size=12.5, fill=TINT2)
    arrow(s, 3.85, 1.94, 5.55, 0.20, direction="right")
    label(s, 3.85, 1.62, 5.55, "`GET /.well-known/agent-card.json`", size=11.5,
          color=ORANGE_DK)
    arrow(s, 3.85, 2.62, 5.55, 0.20, direction="left")
    label(s, 3.85, 2.30, 5.55, "`200 OK`  — the Agent Card as JSON", size=11.5,
          color=ORANGE_DK)
    label(s, 0.75, 2.60, 2.9, "now it knows the url,\nthe skills and the tags",
          size=10.5, color=GRAY)

    code(s, XL, 3.15, HALF, None, [
        '@app.get("/.well-known/agent-card.json")',
        'def get_agent_card():',
        '    return AGENT_CARD',
        '',
        '# the entire discovery half of the protocol',
    ], size=10.5, title="the server side — 02_greeting_agent.py")

    code(s, XR, 3.15, HALF, None, [
        'card = requests.get(',
        '    f"{AGENT_BASE}/.well-known/agent-card.json"',
        ').json()',
        'print("can do:", [s["name"]',
        '                  for s in card["skills"]])',
    ], size=10.5, title="the client side — 03_greeting_client.py")

    table(s, M, 4.90, CW, [
        ["How a client finds a card", "How it works", "Use it when"],
        ["Well-known URI", "`GET https://<host>/.well-known/agent-card.json`",
         "the agent is public, or you already know its domain"],
        ["Curated registry", "query a catalogue by skill, tag or provider",
         "an enterprise, or a marketplace with many agents"],
        ["Direct configuration", "the URL is hardcoded, in config, or in an env var",
         "private agents — what `KNOWN_AGENTS` does in file 06"],
    ], widths=[2.5, 5.6, 4.1], row_h=0.40)

    label(s, M, 6.56, CW, "Cards can be cached (`Cache-Control`, `ETag`), and a sensitive "
                          "agent can serve a fuller **authenticated extended card** only to "
                          "callers who log in.", size=11.5, color=GRAY, align=PP_ALIGN.LEFT)


def _s17_messages(prs):
    s = slide(prs, "Part 3 · Messages", "Messages and Parts")

    para(s, M, BODY_TOP + 0.04, CW, 0.44,
         "A **Message** is one turn of the conversation. Its content is never a bare "
         "string — it is always a **list of Parts**, so the same envelope carries text, "
         "a PDF and a JSON blob without changing shape.", size=13.2)

    # the envelope
    env = chip(s, XL, 2.10, HALF, 2.35, "", fill=TINT, edge=ORANGE)
    del env
    label(s, XL, 2.22, HALF, "MESSAGE", size=11, color=ORANGE)
    label(s, XL + 0.30, 2.52, HALF - 0.6, "`role`: \"user\"  |  \"agent\"", size=12,
          color=INK, align=PP_ALIGN.LEFT)
    label(s, XL + 0.30, 2.82, HALF - 0.6, "`messageId`  ·  `taskId`  ·  `contextId`",
          size=12, color=INK, align=PP_ALIGN.LEFT)
    label(s, XL + 0.30, 3.12, HALF - 0.6, "`parts`:", size=12, color=INK,
          align=PP_ALIGN.LEFT)
    for i, (k, d) in enumerate([("text", "plain words"),
                                ("file", "bytes or a URI"),
                                ("data", "structured JSON")]):
        chip(s, XL + 0.35 + i * 1.82, 3.42, 1.70, 0.72, f'kind:\n"{k}"',
             sub=d, size=10.5, fill=WHITE)

    code(s, XR, 2.10, HALF, None, [
        '"message": {',
        '    "role": "user",',
        '    "parts": [',
        '        {"kind": "text", "text": "Sara"}',
        '    ],',
        '    "messageId": uuid.uuid4().hex,',
        '}',
        '',
        '# coming back, the role flips to "agent"',
    ], size=10.5, title="03_greeting_client.py")

    box(s, XL, 4.62, HALF, 1.05, "Why a list, for one string?",
        ["Because next week you will send an image with a caption. The client code "
         "that reads `parts[0][\"text\"]` never has to change."], size=12)

    box(s, XR, 4.62, HALF, 1.05, "`role` has exactly two values",
        ["`\"user\"` is whoever is asking — often another agent. `\"agent\"` is the one "
         "answering. There is no `\"system\"` role on the wire."], size=12, fill=TINT2)

    box(s, M, 5.83, CW, 0.99, "The three ids, in one line each",
        ["`messageId` — this one turn.    `taskId` — the job this turn belongs to.    "
         "`contextId` — the whole conversation the job belongs to."], size=12.5)


def _s18_jsonrpc(prs):
    s = slide(prs, "Part 3 · Transport", "JSON-RPC 2.0 — the envelope every call travels in")

    code(s, XL, BODY_TOP + 0.06, HALF, None, [
        '{"jsonrpc": "2.0",         # always this',
        ' "id": 1,                  # echoed back',
        ' "method": "message/send", # what you want',
        ' "params": {',
        '   "message": {',
        '     "role": "user",',
        '     "parts": [{"kind": "text",',
        '                "text": "Sara"}],',
        '     "messageId": "..."}}}',
    ], size=10.5, title="the request  —  POST /")

    code(s, XR, BODY_TOP + 0.06, HALF, None, [
        '{"jsonrpc": "2.0",',
        ' "id": 1,                  # the same id',
        ' "result": {',
        '   "role": "agent",',
        '   "parts": [{"kind": "text",',
        '              "text": "Hello, Sara!"}],',
        '   "messageId": "greeting-reply-1"}}',
        '',
        '# on failure: "error" instead of "result"',
    ], size=10.5, title="the response")

    label(s, M, 4.10, CW, "Ten methods exist. **`message/send` alone is a useful agent** — "
                          "that is all files 02 to 09 implement.", size=12.5, color=INK,
          align=PP_ALIGN.LEFT)

    table(s, M, 4.46, CW, [
        ["Method", "What it does", "Needed?"],
        ["`message/send`", "send a message, get a Message or a Task back", "**yes — this is the protocol**"],
        ["`message/stream`", "same, but events arrive live over SSE", "only if `streaming: true`"],
        ["`tasks/get`", "look up a task you started earlier, by id", "for long jobs"],
        ["`tasks/cancel` · `tasks/resubscribe`", "stop a running task · reattach to a dropped stream", "for long jobs"],
        ["`tasks/pushNotificationConfig/*`", "set · get · list · delete your webhook", "only if `pushNotifications: true`"],
        ["`agent/getAuthenticatedExtendedCard`", "fetch the fuller card after logging in", "optional"],
    ], widths=[3.8, 5.6, 2.8], row_h=0.33)


def _s19_errors(prs):
    s = slide(prs, "Part 3 · Transport", "When things go wrong")

    heading(s, XL, BODY_TOP + 0.04, HALF, "Standard JSON-RPC 2.0")
    table(s, XL, 1.76, HALF, [
        ["Code", "Meaning"],
        ["`-32700`", "Parse error — that was not JSON"],
        ["`-32600`", "Invalid Request — not a JSON-RPC object"],
        ["`-32601`", "**Method not found** — the common one"],
        ["`-32602`", "Invalid params"],
        ["`-32603`", "Internal error"],
    ], widths=[1.4, 4.5], row_h=0.34)

    heading(s, XR, BODY_TOP + 0.04, HALF, "A2A-specific")
    table(s, XR, 1.76, HALF, [
        ["Code", "Name"],
        ["`-32001`", "TaskNotFoundError"],
        ["`-32002`", "TaskNotCancelableError"],
        ["`-32003`", "PushNotificationNotSupportedError"],
        ["`-32004`", "UnsupportedOperationError"],
        ["`-32005`", "ContentTypeNotSupportedError"],
        ["`-32006`", "InvalidAgentResponseError"],
        ["`-32007`", "ExtendedAgentCardNotConfiguredError"],
        ["`-32008`", "ExtensionSupportRequiredError"],
        ["`-32009`", "VersionNotSupportedError"],
    ], widths=[1.4, 4.5], row_h=0.34)

    code(s, XL, 3.98, HALF, None, [
        '# any method we do not implement',
        'return {"jsonrpc": "2.0", "id": rpc.get("id"),',
        '        "error": {"code": -32601,',
        '                  "message":',
        '                    f"Method not found: {method}"}}',
    ], size=10.5, title="02_greeting_agent.py")

    box(s, XL, 5.78, HALF, 1.04, "Errors are how discovery stays honest",
        ["A client that asks for something you did not declare gets a clean, "
         "numbered refusal instead of a 500."], size=12)

    box(s, XR, 5.78, HALF, 1.04, "Try it live",
        ["`agent talks 2 / 02_one_agent_replies.py` sends `make/coffee` and prints "
         "`-32601: Method not found: make/coffee`."], size=12, fill=TINT2)


def _s20_tasks(prs):
    s = slide(prs, "Part 3 · Tasks", "Tasks — work that has an id and a lifecycle")

    bullets(s, XL, BODY_TOP + 0.06, HALF, 2.4, [
        "A Message is a turn of talk. A **Task is a job** — it can take minutes, pause to ask you something, fail, or be cancelled.",
        "The agent creates the task and owns its state. The client only watches.",
        "This is what makes A2A ~~async first~~: you get an id immediately and the answer whenever it is ready.",
        "A simple agent may skip tasks and reply with a bare Message. Files 02–09 do exactly that; `agent talks 2` returns real Tasks.",
    ], size=13)

    code(s, XL, 4.05, HALF, None, [
        'task = {',
        '    "id":        "task-3f9a1c2b",',
        '    "contextId": "ctx-debate-1",',
        '    "status": {"state": "submitted",',
        '               "timestamp": "2026-08-08T..."},',
        '    "history":   [incoming_message],',
        '    "artifacts": [],',
        '    "kind":      "task",',
        '}',
        '',
        '# agent talks 2 / debate_agent.py',
    ], size=10.5, title="a Task, the moment it is born")

    table(s, XR, BODY_TOP + 0.06, HALF, [
        ["Field", "What it holds"],
        ["`id`", "unique id for this job"],
        ["`contextId`", "the conversation it belongs to"],
        ["`status`", "`state` + `timestamp` + an optional `message`"],
        ["`history`", "every Message exchanged for this task"],
        ["`artifacts`", "**the outputs the agent produced**"],
        ["`metadata`", "anything extra you want to carry"],
        ["`kind`", "always the literal `\"task\"`"],
    ], widths=[1.9, 4.0], row_h=0.40)

    box(s, XR, 4.64, HALF, 1.10, "The part people miss",
        ["`message/send` does **not** hand back a string. It hands back a Task, and "
         "the answer is inside `task[\"artifacts\"][0][\"parts\"][0][\"text\"]`."],
        size=12.5, fill=TINT2)

    box(s, XR, 5.90, HALF, 0.92, "Why an id at all?",
        ["So you can walk away. `tasks/get` lets a client that crashed, or a "
         "different client entirely, pick the job back up."], size=12.5)


def _s21_lifecycle(prs):
    s = slide(prs, "Part 3 · Tasks", "The Task lifecycle")

    # the happy path
    heading(s, M, BODY_TOP + 0.02, CW, "The happy path")
    chip(s, 1.55, 1.82, 2.55, 0.68, "submitted", sub="accepted, queued", size=13)
    arrow(s, 4.28, 2.05, 0.72, 0.22)
    chip(s, 5.20, 1.82, 2.55, 0.68, "working", sub="the agent is on it", size=13,
         fill=TINT2)
    arrow(s, 7.93, 2.05, 0.72, 0.22)
    chip(s, 8.85, 1.82, 2.55, 0.68, "completed", sub="TERMINAL", size=13,
         fill=INK, edge=None, color=WHITE)

    # the two detours
    heading(s, XL, 2.92, HALF, "Paused  —  not terminal")
    chip(s, XL, 3.24, HALF / 2 - 0.15, 0.62, "input-required", size=12, fill=TINT)
    chip(s, XL + HALF / 2 + 0.15, 3.24, HALF / 2 - 0.15, 0.62, "auth-required",
         size=12, fill=TINT)
    label(s, XL, 3.98, HALF, "the agent needs something from you. Reply with the "
                             "same `taskId` and it goes back to `working`.",
          size=11.5, color=GRAY, align=PP_ALIGN.LEFT)

    heading(s, XR, 2.92, HALF, "The other endings  —  terminal")
    tw = (HALF - 0.3) / 3
    for i, t in enumerate(["failed", "canceled", "rejected"]):
        chip(s, XR + i * (tw + 0.15), 3.24, tw, 0.62, t, size=12, fill=INK,
             edge=None, color=WHITE)
    label(s, XR, 3.98, HALF, "the agent broke · you called `tasks/cancel` · the agent "
                             "refused the work outright.", size=11.5, color=GRAY,
          align=PP_ALIGN.LEFT)

    rule(s, M, 4.62, CW, color=LINE)

    box(s, XL, 4.82, HALF, 1.05, "Terminal means terminal",
        ["`completed` · `canceled` · `failed` · `rejected` end the task **forever**. "
         "A task can never restart. That is what makes its artifacts trustworthy."],
        size=12.5, fill=TINT2)

    box(s, XR, 4.82, HALF, 1.05, "So how do you refine an answer?",
        ["You start a **new task** in the **same** `contextId`, and point at the old "
         "one with `referenceTaskIds`."], size=12.5)

    box(s, M, 6.02, CW, 0.82, "The ninth state",
        ["There is also `unknown` — an indeterminate state. You should never emit it; "
         "you handle it defensively when reading someone else's task."], size=12.5)


def _s22_artifacts(prs):
    s = slide(prs, "Part 3 · Artifacts", "Artifacts — the thing the agent actually made")

    para(s, M, BODY_TOP + 0.04, CW, 0.44,
         "A Message is what an agent **said**. An Artifact is what it **produced** — "
         "the report, the image, the converted file, the argument. Artifacts hang off "
         "the Task, not off the conversation.", size=13.2)

    # nesting diagram
    chip(s, XL, 2.10, HALF, 0.58, "Task", size=12.5, fill=TINT2)
    arrow(s, XL + 0.45, 2.72, 0.18, 0.26, direction="down")
    chip(s, XL + 0.35, 3.02, HALF - 0.35, 0.58, "`artifacts`  — a list", size=12,
         fill=TINT)
    arrow(s, XL + 0.80, 3.64, 0.18, 0.26, direction="down")
    chip(s, XL + 0.70, 3.94, HALF - 0.70, 0.58,
         "Artifact — `artifactId` · `name` · `parts`", size=11.5)
    arrow(s, XL + 1.15, 4.56, 0.18, 0.26, direction="down")
    chip(s, XL + 1.05, 4.86, HALF - 1.05, 0.58, "`{\"kind\": \"text\", \"text\": ...}`",
         size=11.5, fill=WHITE)

    code(s, XR, 2.10, HALF, None, [
        '# working -> completed, with the result',
        '# carried as an ARTIFACT',
        'task["artifacts"] = [{',
        '    "artifactId": _id("artifact"),',
        '    "name": "argument",',
        '    "parts": [{"kind": "text",',
        '               "text": reply_text}],',
        '}]',
        'task["status"] = {"state": "completed",',
        '                  "timestamp": _now()}',
        '',
        'def task_text(task):',
        '    return task["artifacts"][0]["parts"][0]["text"]',
    ], size=10, title="agent talks 2 / debate_agent.py")

    box(s, XL, 5.62, HALF, 1.20, "Message or Artifact?",
        ["If a human would call it *\"the deliverable\"*, it is an Artifact. "
         "If it is *\"what it said back\"*, it is a Message. Chatty agents produce "
         "only Messages; working agents produce both."], size=12.5)

    box(s, XR, 5.62, HALF, 1.20, "A task can produce many",
        ["`artifacts` is a list because one job can yield a chart **and** a CSV "
         "**and** a summary. Each artifact has its own `name` so the client can "
         "tell them apart."], size=12.5, fill=TINT2)


# =====================================================================
#  PART 4 — THE FLOW  (23)
# =====================================================================

def _s23_flow(prs):
    s = slide(prs, "Part 4 · The flow", "The A2A Communication Flow, end to end")

    ax, bx = 2.55, 10.15          # lifeline centres
    chip(s, ax - 1.45, 1.48, 2.90, 0.58, "A2A Client", size=12.5, fill=TINT)
    chip(s, bx - 1.45, 1.48, 2.90, 0.58, "Remote Agent", size=12.5, fill=TINT2)
    vrule(s, ax, 2.06, 3.95, color=LINE)
    vrule(s, bx, 2.06, 3.95, color=LINE)

    steps = [
        (1, "right", "`GET /.well-known/agent-card.json`", "discovery — one fixed path"),
        (2, "left", "the **Agent Card**  —  `name` · `url` · `skills` · `capabilities`", "now the client knows what it can ask for"),
        (3, "self", "match the question against every `skill[\"tags\"]`", "the client decides WHO, before it sends anything"),
        (4, "right", "`POST /`   `{\"method\": \"message/send\", \"params\": {\"message\": ...}}`", "delegation"),
        (5, "left", "`{\"result\": ...}`  —  a **Message**, or a **Task** with artifacts", "read `parts[0][\"text\"]`, or `artifacts[0]`"),
    ]

    y = 2.42
    for n, kind, txt, note in steps:
        chip(s, 0.60, y - 0.10, 0.36, 0.36, str(n), size=11, fill=ORANGE_HI,
             edge=None)
        if kind == "self":
            chip(s, ax - 1.45, y - 0.14, 2.90, 0.44, "pick_agent()", size=11,
                 fill=WHITE)
            label(s, ax + 1.60, y - 0.16, 8.0, txt, size=11.5, color=INK,
                  align=PP_ALIGN.LEFT)
            label(s, ax + 1.60, y + 0.10, 8.0, note, size=10, color=GRAY,
                  align=PP_ALIGN.LEFT)
        else:
            label(s, ax + 0.05, y - 0.30, bx - ax - 0.10, txt, size=11.5, color=INK)
            arrow(s, ax + 0.03, y, bx - ax - 0.06, 0.18, direction=kind)
            label(s, ax + 0.05, y + 0.19, bx - ax - 0.10, note, size=10, color=GRAY)
        y += 0.78

    box(s, M, 6.10, CW, 0.72, "The whole protocol, in one breath",
        ["~~publish a card  →  discover it  →  `message/send`  →  read the reply.~~   "
         "Everything else is built on that loop."], size=13)


def build(prs):
    _s01_title(prs)
    _s02_agenda(prs)
    _s03_why_talk(prs)
    _s04_nxm(prs)
    _s05_what_is_a2a(prs)
    _s06_vs(prs)
    _s07_when(prs)
    _s08_architecture(prs)
    _s09_topologies(prs)
    _s10_vocabulary(prs)
    _s11_card_idea(prs)
    _s12_card_fields(prs)
    _s13_card_code(prs)
    _s14_skills(prs)
    _s15_capabilities(prs)
    _s16_discovery(prs)
    _s17_messages(prs)
    _s18_jsonrpc(prs)
    _s19_errors(prs)
    _s20_tasks(prs)
    _s21_lifecycle(prs)
    _s22_artifacts(prs)
    _s23_flow(prs)
