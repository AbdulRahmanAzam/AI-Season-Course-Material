"""
Slides 24-35 — walking the eleven numbered files in session 12: A2A by hand,
two specialists, the orchestrator, LLM brains, then the official a2a-sdk.
"""

from pptx.enum.text import PP_ALIGN

from theme import (
    ORANGE, ORANGE_HI, ORANGE_DK, TINT, TINT2, INK, GRAY, GRAY_LT, LINE,
    WHITE, RED, GREEN, M, CW, W, BODY_TOP,
    slide, divider, bullets, para, heading, code, box, table,
    chip, chip_row, arrow, label, rule, vrule, twocol,
)

XL, XR, HALF = twocol()



def _s24_the_files(prs):
    s = slide(prs, "Part 5 · The code", "The eleven files, and how to run them")

    table(s, M, BODY_TOP + 0.04, 7.25, [
        ["#", "File", "What it teaches"],
        ["01", "`01_what_is_an_agent_card.py`", "The Agent Card — an agent's résumé (no server)"],
        ["02", "`02_greeting_agent.py`", "An A2A **server** by hand — card + `message/send`"],
        ["03", "`03_greeting_client.py`", "An A2A **client** — discover → send → read"],
        ["04", "`04_weather_agent.py`", "A **specialist** agent (weather, mock data)"],
        ["05", "`05_currency_agent.py`", "A **specialist** agent (currency, mock data)"],
        ["06", "`06_orchestrator.py`", "⭐ Discovers both and **delegates** to the right one"],
        ["07", "`07_llm_weather_agent.py`", "Same weather agent, now with a **Groq LLM** brain"],
        ["08", "`08_llm_currency_agent.py`", "Same currency agent, with an LLM brain"],
        ["09", "`09_llm_orchestrator.py`", "The **router itself** becomes an LLM"],
        ["10", "`10_sdk_agent.py`", "The same agent with the official **`a2a-sdk`**"],
        ["11", "`11_sdk_client.py`", "The SDK **client**"],
    ], widths=[0.5, 3.0, 3.75], row_h=0.355, size=10.5)

    heading(s, 8.15, BODY_TOP + 0.04, CW - 7.60, "Every agent is a server")
    for i, (t, sub) in enumerate([("Terminal 1", "python 04_weather_agent.py   · 8002"),
                                  ("Terminal 2", "python 05_currency_agent.py  · 8003"),
                                  ("Terminal 3", "python 06_orchestrator.py")]):
        chip(s, 8.15, 1.80 + i * 0.80, CW - 7.60, 0.66, t, sub=sub, size=11.5,
             fill=TINT2 if i == 2 else WHITE)

    table(s, 8.15, 4.28, CW - 7.60, [
        ["Port", "Who lives there"],
        ["`8001`", "greeting agent"],
        ["`8002`", "weather agent (04 **or** 07)"],
        ["`8003`", "currency agent (05 **or** 08)"],
        ["`9999`", "the SDK agent"],
    ], widths=[1.0, 3.6], row_h=0.34)

    box(s, 8.15, 6.10, CW - 7.60, 0.74, "Before class",
        ["`pip install -r requirements.txt`, and pin **`a2a-sdk==1.1.1`** — files "
         "10 and 11 need it. A Groq key is optional; 07–09 fall back to mock."],
        size=11.5, fill=TINT2)


def _s25_file02(prs):
    s = slide(prs, "Part 5 · File 02", "An A2A server, built by hand")

    para(s, M, BODY_TOP + 0.04, CW, 0.44,
         "An A2A agent is not a special kind of program. It is a normal web server "
         "that keeps ~~exactly two promises~~ — and you can see both of them on this slide.",
         size=13.2)

    code(s, XL, 2.06, HALF, None, [
        'app = FastAPI()',
        '',
        '# PROMISE 1 — publish the card at the fixed path',
        '@app.get("/.well-known/agent-card.json")',
        'def get_agent_card():',
        '    return AGENT_CARD',
        '',
        '# PROMISE 2 — answer message/send at "/"',
        '@app.post("/")',
        'async def handle_rpc(request: Request):',
        '    rpc = await request.json()',
        '    method = rpc.get("method")',
        '    if method == "message/send":',
        '        user_text = rpc["params"]["message"] \\',
        '                       ["parts"][0]["text"]',
        '        reply_text = f"Hello, {user_text}!"',
    ], size=10.5, title="02_greeting_agent.py   ·   port 8001")

    code(s, XR, 2.06, HALF, None, [
        '        agent_message = {',
        '            "role": "agent",',
        '            "parts": [{"kind": "text",',
        '                       "text": reply_text}],',
        '            "messageId": "greeting-reply-1"}',
        '        return {"jsonrpc": "2.0",',
        '                "id": rpc.get("id"),',
        '                "result": agent_message}',
        '',
        '    # anything else -> a JSON-RPC error',
        '    return {"jsonrpc": "2.0", "id": rpc.get("id"),',
        '            "error": {"code": -32601, "message":',
        '                      f"Method not found: {method}"}}',
        '',
        'uvicorn.run(app, host="127.0.0.1", port=8001)',
    ], size=10.5, title="…the reply, and the error path")

    box(s, M, 5.98, CW, 0.84, "Checkpoint question for the room",
        ["*\"What are the only two things this server had to do to be a valid A2A agent?\"*   "
         "→  **serve a card**, and **answer `message/send`**."], size=12.5)


def _s26_file03(prs):
    s = slide(prs, "Part 5 · File 03", "An A2A client, built by hand")

    for i, (n, t, sub) in enumerate([
        ("1", "DISCOVER", "read the card"),
        ("2", "SEND", "POST message/send"),
        ("3", "READ", "pull the text out"),
    ]):
        x = M + i * (CW / 3)
        chip(s, x, 1.58, 0.42, 0.42, n, size=11, fill=ORANGE_HI, edge=None)
        label(s, x + 0.55, 1.58, 2.4, t, size=13, color=INK, align=PP_ALIGN.LEFT)
        label(s, x + 0.55, 1.86, 3.2, sub, size=10.5, color=GRAY, align=PP_ALIGN.LEFT)

    code(s, XL, 2.28, HALF, None, [
        '# 1) DISCOVER',
        'card = requests.get(',
        '  f"{AGENT_BASE}/.well-known/agent-card.json"',
        ').json()',
        'print("   can do:",',
        '      [s["name"] for s in card["skills"]])',
        '',
        '# 2) SEND',
        'rpc_request = {',
        '    "jsonrpc": "2.0",',
        '    "id": 1,',
        '    "method": "message/send",',
        '    "params": {"message": {',
        '        "role": "user",',
        '        "parts": [{"kind": "text",',
        '                   "text": "Sara"}],',
        '        "messageId": uuid.uuid4().hex,',
        '    }},',
    ], size=10.5, title="03_greeting_client.py")

    code(s, XR, 2.28, HALF, None, [
        '}',
        'response = requests.post(card["url"],',
        '                         json=rpc_request).json()',
        '',
        '# 3) READ',
        'reply_text = response["result"]["parts"][0]["text"]',
        'print("Agent replied:", reply_text)',
    ], size=10.5, title="…send it, and dig the answer out")

    box(s, XR, 4.36, HALF, 1.20, "Notice what is NOT here",
        ["No SDK. No client library. No schema. Just `requests` and a dictionary — "
         "because A2A is *JSON over HTTP you already know how to speak*."], size=12.5)

    box(s, XR, 5.72, HALF, 1.10, "Trace it live in class",
        ["Follow `\"Sara\"` from `parts[0][\"text\"]` on the way out to "
         "`\"Hello, Sara!\"` on the way back, and match it to the card's `greet` skill."],
        size=12.5, fill=TINT2)


def _s27_specialists(prs):
    s = slide(prs, "Part 5 · Files 04 + 05", "Two specialists that know nothing about each other")

    code(s, XL, BODY_TOP + 0.06, HALF, None, [
        'FAKE_WEATHER = {"karachi": "34 C, sunny",',
        '                "london":  "18 C, rainy",',
        '                "tokyo":   "25 C, cloudy"}',
        '',
        'def look_up_weather(text: str) -> str:',
        '    text = text.lower()',
        '    for city, weather in FAKE_WEATHER.items():',
        '        if city in text:',
        '            return f"The weather in ..."',
        '    return "I can report Karachi, London, Tokyo."',
        '"tags": ["weather", "forecast", "temperature",',
        '         "rain"],                      # port 8002',
    ], size=10.5, title="04_weather_agent.py")

    code(s, XR, BODY_TOP + 0.06, HALF, None, [
        'RATES = {"USD": 1.0, "PKR": 278.0, "EUR": 0.9}',
        'def convert_currency(text: str) -> str:',
        '    amount_match = re.search(r"(\\d+(?:\\.\\d+)?)", text)',
        '    codes = [w.upper() for w in',
        '             re.findall(r"[A-Za-z]{3}", text)]',
        '    known = [c for c in codes if c in RATES]',
        '    if not amount_match or len(known) < 2:',
        '        return "Ask me like: convert 100 USD to PKR."',
        '    amount = float(amount_match.group(1))',
        '    frm, to = known[0], known[1]',
        '    result = amount / RATES[frm] * RATES[to]',
        '    return f"{amount:.0f} {frm} = {result:.0f} {to}"',
    ], size=10.5, title="05_currency_agent.py   ·   port 8003")

    box(s, XL, 4.65, HALF, 1.10, "Why scan for known codes?",
        ["Guessing by position breaks on *\"I have 100 USD, convert it to PKR\"*. "
         "Scanning for codes we know survives messy phrasing — and messy phrasing "
         "is what students type."], size=12.5)

    box(s, XR, 4.65, HALF, 1.10, "The Session 6 callback",
        ["These are the **same two functions** from Session 6, where they were "
         "**tools** one agent owned. Same capability, new packaging."],
        size=12.5, fill=TINT2)

    box(s, M, 5.90, CW, 0.92, "Say this out loud",
        ["*\"Neither of these agents knows the other exists — no shared variable, no "
         "import, no memory. What makes them a **team** is file 06, and the only thing "
         "file 06 has is their cards.\"*"], size=13)


def _s28_orchestrator_a(prs):
    s = slide(prs, "Part 5 · File 06 ⭐", "The orchestrator — discover, then decide")

    code(s, XL, BODY_TOP + 0.06, HALF, None, [
        'KNOWN_AGENTS = ["http://localhost:8002",',
        '                "http://localhost:8003"]',
        '',
        '# 1) DISCOVER — build a directory of cards',
        'def discover(agent_urls):',
        '    directory = []',
        '    for base in agent_urls:',
        '        card = requests.get(',
        '            f"{base}/.well-known/agent-card.json"',
        '        ).json()',
        '        directory.append(card)',
        '        tags = [t for skill in card["skills"]',
        '                  for t in skill["tags"]]',
        '        print(f"  found {card[\'name\']} -> {tags}")',
        '    return directory',
        '',
        '# 2) ROUTE — whose tags appear in the question?',
        'def pick_agent(directory, question):',
    ], size=10.5, title="06_orchestrator.py")

    code(s, XR, BODY_TOP + 0.06, HALF, None, [
        '    q = question.lower()',
        '    for card in directory:',
        '        for skill in card["skills"]:',
        '            keywords = skill["tags"] + [',
        '                skill["id"], skill["name"].lower()]',
        '            if any(word.lower() in q',
        '                   for word in keywords):',
        '                return card',
        '    return None',
    ], size=10.5, title="…the routing rule, in eight lines")

    heading(s, XR, 4.02, HALF, "The shape it makes")
    chip(s, XR + HALF / 2 - 1.30, 4.34, 2.60, 0.52, "Orchestrator", size=12,
         fill=TINT2)
    vrule(s, XR + HALF / 2, 4.86, 0.18, color=ORANGE_HI, thick=0.028)
    rule(s, XR + 1.35, 5.04, HALF - 2.70, color=ORANGE_HI, thick=0.028)
    for cx in (XR + 1.35, XR + HALF - 1.35):
        vrule(s, cx, 5.04, 0.18, color=ORANGE_HI, thick=0.028)
    chip(s, XR + 0.30, 5.22, 2.10, 0.56, "Weather", sub="8002", size=11)
    chip(s, XR + HALF - 2.40, 5.22, 2.10, 0.56, "Currency", sub="8003", size=11)

    box(s, XR, 5.90, HALF, 0.92, "A whole new kind of program",
        ["*\"It cannot do weather. It cannot do currency. All it knows how to do is "
         "**read cards** and **delegate**.\"*"], size=12.5)

    box(s, XL, 5.90, HALF, 0.92, "In the real world",
        ["`KNOWN_AGENTS` would be a query to a registry. The rest of the function "
         "would not change one line."], size=12, fill=TINT2)


def _s29_orchestrator_b(prs):
    s = slide(prs, "Part 5 · File 06 ⭐", "The orchestrator — then delegate")

    code(s, XL, BODY_TOP + 0.06, HALF, None, [
        '# 3) DELEGATE — the A2A call itself',
        'def ask_agent(card, question):',
        '    rpc_request = {',
        '        "jsonrpc": "2.0", "id": 1,',
        '        "method": "message/send",',
        '        "params": {"message": {',
        '            "role": "user",',
        '            "parts": [{"kind": "text",',
        '                       "text": question}],',
        '            "messageId": uuid.uuid4().hex,',
        '        }}}',
        '    response = requests.post(card["url"],',
        '                             json=rpc_request).json()',
        '    return response["result"]["parts"][0]["text"]',
    ], size=10.5, title="06_orchestrator.py")

    heading(s, XR, BODY_TOP + 0.06, HALF, "What it prints")
    table(s, XR, 1.78, HALF, [
        ["The user asks", "It routes to", "Because"],
        ["What's the weather in Tokyo?", "Weather Agent", "tag `weather`"],
        ["Convert 100 USD to PKR", "Currency Agent", "tag `convert`"],
        ["Is it raining in London?", "Weather Agent", "tag `rain`"],
    ], widths=[2.7, 1.8, 1.4], row_h=0.42)

    box(s, XR, 3.72, HALF, 1.10, "The third question is the interesting one",
        ["It never says *\"weather\"*. It says *\"raining\"*. The tag `rain` is the "
         "only reason it routes correctly — tags are a real design decision."],
        size=12.5, fill=TINT2)

    box(s, XR, 5.00, HALF, 0.92, "The same idea as Session 4's verifier",
        ["One agent checking another's work — but standardised, so it works across "
         "the network between agents built by people who never met."], size=12.5)

    box(s, M, 6.04, CW, 0.78, "Exercise 1, and why it lands",
        ["Copy `04_weather_agent.py` into a `math_agent` on port 8004, add it to "
         "`KNOWN_AGENTS`, and *\"what is 2+2\"* routes with ~~zero changes~~ elsewhere."],
        size=13)


def _s30_file07(prs):
    s = slide(prs, "Part 5 · File 07", "Giving an agent a real brain")

    code(s, XL, BODY_TOP + 0.06, HALF, None, [
        'MODEL = "openai/gpt-oss-120b"   # Groq',
        '',
        'def use_mock() -> bool:',
        '    """Mock unless a real Groq key is set."""',
        '    key = os.getenv("GROQ_API_KEY", "").strip()',
        '    provider = os.getenv("LLM_PROVIDER", "mock")',
        '    return (provider.lower() == "mock" or not key',
        '            or key == "your_groq_key_here")',
        '',
        'def weather_brain(user_text: str) -> str:',
        '    if use_mock():',
        '        text = user_text.lower()   # = FILE 4 logic',
        '        for city, w in FAKE_WEATHER.items():',
        '            if city in text:',
        '                return f"The weather in ..."',
        '        return "I can report Karachi, London, Tokyo."',
    ], size=10.5, title="07_llm_weather_agent.py   ·   port 8002")

    code(s, XR, BODY_TOP + 0.06, HALF, None, [
        '    from groq import Groq        # the real path',
        '    client = Groq()              # reads the env var',
        '    system = (',
        '        "You are a Weather Agent. Only use this "',
        '        f"weather data: {FAKE_WEATHER}. Answer in "',
        '        "ONE short, friendly sentence.")',
        '    resp = client.chat.completions.create(',
        '        model=MODEL, temperature=0, messages=[',
        '            {"role": "system", "content": system},',
        '            {"role": "user",   "content": user_text}])',
        '    return resp.choices[0].message.content.strip()',
    ], size=10.5, title="…the LLM call")

    box(s, XR, 4.48, HALF, 1.22, "The card did not change",
        ["Same `name`, same `url`, same `skills`, same **port 8002**. Only the "
         "function behind `message/send` is different. Hold that thought — it "
         "becomes the point two slides from now."], size=12.5, fill=TINT2)

    box(s, M, 5.86, CW, 0.96, "The prompt is inside the agent, not on the card",
        ["Notice where `system` lives — in the agent's private code. A client reading "
         "the card learns *what* this agent does and never *how*. And with no key it "
         "silently falls back to file 04's dictionary, so the demo never breaks in class."],
        size=12.5)


def _s31_file08(prs):
    s = slide(prs, "Part 5 · File 08", "Let Python do the maths; let the LLM do the words")

    code(s, XL, BODY_TOP + 0.06, HALF, None, [
        'def do_math(text: str):',
        '    amount_match = re.search(r"(\\d+(?:\\.\\d+)?)", text)',
        '    codes = [w.upper() for w in',
        '             re.findall(r"[A-Za-z]{3}", text)]',
        '    known = [c for c in codes if c in RATES]',
        '    if not amount_match or len(known) < 2:',
        '        return None',
        '    amount = float(amount_match.group(1))',
        '    frm, to = known[0], known[1]',
        '    return (amount, frm, to,',
        '            amount / RATES[frm] * RATES[to])',
        '',
        'def currency_brain(user_text: str) -> str:',
        '    result = do_math(user_text)      # exact, always',
        '    if result is None:',
        '        return "Ask me like convert 100 USD to PKR."',
        '    amount, frm, to, converted = result',
    ], size=10.5, title="08_llm_currency_agent.py")

    code(s, XR, BODY_TOP + 0.06, HALF, None, [
        '    from groq import Groq',
        '    client = Groq()',
        '    system = ("You are a Currency Agent. Rephrase "',
        '              "the given conversion result in one "',
        '              "friendly sentence. "',
        '              "Do not change the numbers.")',
        '    fact = f"{amount:.0f} {frm} = {converted:.2f} {to}"',
        '    resp = client.chat.completions.create(',
        '        model=MODEL, temperature=0.3, messages=[...])',
    ], size=10.5, title="…the LLM only phrases it")

    heading(s, XR, 4.02, HALF, "Two jobs, two tools")
    chip(s, XR, 4.34, HALF / 2 - 0.20, 1.05, "the numbers",
         sub="Python · deterministic · testable", size=12, fill=TINT2)
    chip(s, XR + HALF / 2 + 0.20, 4.34, HALF / 2 - 0.20, 1.05, "the sentence",
         sub="the LLM · fluent · never sees the maths", size=12, fill=TINT)

    box(s, XR, 5.62, HALF, 1.20, "The rule worth stealing",
        ["**Never let the model do arithmetic it can get wrong.** Compute the fact "
         "in code, hand the model the fact, ask only for wording."], size=12.5)

    box(s, XL, 5.62, HALF, 1.20, "Same shape as file 07",
        ["`use_mock()` again, so this runs offline too — it returns the bare "
         "`100 USD = 27800 PKR`. Card, port and skill are identical to file 05."],
        size=12.5, fill=TINT2)


def _s32_opacity(prs):
    s = slide(prs, "Part 5 · The big idea ⭐", "Protocol opacity — agents are black boxes")

    chip(s, 3.90, 1.56, 5.55, 0.72, "06_orchestrator.py", sub="not one line changes",
         size=13, fill=TINT2)
    arrow(s, 6.55, 2.32, 0.24, 0.40, direction="down")
    label(s, 3.90, 2.76, 5.55, "`GET /.well-known/agent-card.json`   then   "
                               "`POST /  message/send`", size=11.5, color=ORANGE_DK)
    chip(s, 3.90, 3.06, 5.55, 0.56, "http://localhost:8002/", size=12,
         fill=ORANGE_HI, edge=None)
    arrow(s, 6.55, 3.66, 0.24, 0.34, direction="down")

    chip(s, XL, 4.10, HALF, 1.35, "FILE 04",
         sub="a Python dict lookup — 3 cities, hardcoded", size=13)
    chip(s, XR, 4.10, HALF, 1.35, "FILE 07",
         sub="a 120-billion-parameter model on Groq", size=13, fill=TINT2)
    label(s, M, 5.52, CW, "same card  ·  same port  ·  same `message/send`  ·  "
                          "~~the client cannot tell the difference~~", size=13,
          color=INK)

    box(s, M, 5.92, CW, 0.90, "Say this out loud",
        ["*\"I am going to kill the hand-made agents and start LLM ones on the SAME ports, "
         "then run the SAME orchestrator. Watch — nothing changes. The client never knew "
         "whether the brain was a dict or a 120-billion-parameter model. **That is the "
         "whole design.**\"*"], size=12.5)


def _s33_file09(prs):
    s = slide(prs, "Part 5 · File 09", "When the router itself is an LLM")

    code(s, XL, BODY_TOP + 0.06, HALF, None, [
        'def choose_agent(directory, question):',
        '    if use_mock():           # FILE 6 keyword routing',
        '        q = question.lower()',
        '        for card in directory:',
        '            for skill in card["skills"]:',
        '                keywords = skill["tags"] + [...]',
        '                if any(w in q for w in keywords):',
        '                    return card',
        '        return None',
        '    from groq import Groq                 # LLM router',
        '    client = Groq()',
        '    catalog = "\\n".join(',
        '        f"- {c[\'name\']}: "',
        '        f"{c[\'skills\'][0][\'description\']}"',
        '        for c in directory)',
    ], size=10.5, title="09_llm_orchestrator.py")

    code(s, XR, BODY_TOP + 0.06, HALF, None, [
        '    system = ("You are a router. Pick the single "',
        '              "best agent for the user\'s question. "',
        '              "Reply with ONLY the agent\'s name.")',
        '    choice = client.chat.completions.create(',
        '        model=MODEL, temperature=0, messages=[...]',
        '    ).choices[0].message.content.strip()',
        '',
        '    for card in directory:   # name -> card',
        '        if card["name"].lower() in choice.lower():',
        '            return card',
    ], size=10.5, title="…then match the name back to a card")

    heading(s, XR, 4.24, HALF, "The questions it can now handle")
    code(s, XR, 4.56, HALF, None, [
        '"I\'m flying to Tokyo soon - what\'s the',
        ' weather there?"',
        '',
        '"I\'ve got 100 USD, can you convert it',
        ' to PKR?"',
    ], size=10.5, fill=WHITE)

    box(s, XR, 6.02, HALF, 0.80, "Same cards. Smarter reader.",
        ["Keyword matching reads `tags`. The LLM reads `description`."],
        size=12.5, fill=TINT2)

    box(s, XL, 5.31, HALF, 1.51, "Two things worth saying",
        ["**One router, either set of specialists.** File 09 works with the hand-made "
         "agents (04 + 05) **or** the LLM ones (07 + 08) — they share ports.",
         "**The orchestrator is an agent too.** Give it a card and a `/` endpoint and "
         "somebody else could hire **it**."], size=12.2)


def _s34_file10(prs):
    s = slide(prs, "Part 5 · File 10", "Now meet the official SDK")

    code(s, XL, BODY_TOP + 0.06, HALF, None, [
        'from a2a.server.agent_execution import (',
        '    AgentExecutor, RequestContext)',
        'from a2a.server.events import EventQueue',
        'from a2a.server.request_handlers import DefaultRequestHandler',
        'from a2a.server.tasks import InMemoryTaskStore',
        'from a2a.server.routes import (add_a2a_routes_to_fastapi,',
        '    create_agent_card_routes, create_jsonrpc_routes)',
        'from a2a.types import (AgentCard, AgentInterface,',
        '                       AgentCapabilities, AgentSkill)',
        '',
        '# YOUR logic goes in an AgentExecutor',
        'class GreetingExecutor(AgentExecutor):',
        '    async def execute(self, context: RequestContext,',
        '                      event_queue: EventQueue) -> None:',
        '        user_text = context.get_user_input()',
        '        reply = new_text_message(f"Hello, {user_text}!")',
        '        await event_queue.enqueue_event(reply)',
    ], size=10.5, title="10_sdk_agent.py   ·   port 9999")

    code(s, XR, BODY_TOP + 0.06, HALF, None, [
        'AGENT_CARD = AgentCard(          # typed, not a dict',
        '    name="Greeting Agent (SDK)",',
        '    capabilities=AgentCapabilities(streaming=True),',
        '    skills=[AgentSkill(id="greet", ...)],',
        '    supported_interfaces=[AgentInterface(',
        '        url="http://localhost:9999/",',
        '        protocol_binding=TransportProtocol.JSONRPC)])',
        '',
        'request_handler = DefaultRequestHandler(',
        '    agent_executor=GreetingExecutor(),',
        '    task_store=InMemoryTaskStore(), ...)',
    ], size=10.5, title="…the card and the wiring")

    table(s, XR, 4.30, HALF, [
        ["By hand — file 02", "With the SDK — file 10"],
        ["`if method == \"message/send\":`", "your `AgentExecutor.execute()`"],
        ["building the reply dict", "`new_text_message()` + `event_queue`"],
        ["(we ignored long jobs)", "`InMemoryTaskStore` tracks tasks"],
        ["our `@app.post(\"/\")` route", "`create_jsonrpc_routes(...)`"],
        ["our card dict", "typed `AgentCard(...)`"],
    ], widths=[2.9, 3.0], row_h=0.38)

    box(s, XL, 5.66, HALF, 1.16, "Why we built it by hand first",
        ["Every SDK name here maps to something you already wrote. Nothing is new "
         "protocol — it is the same two promises with types, a task store and a "
         "router bolted on."], size=12.5, fill=TINT2)


def _s35_file11(prs):
    s = slide(prs, "Part 5 · File 11", "The SDK client, and the trade you are making")

    code(s, XL, BODY_TOP + 0.06, HALF, None, [
        'async def main():',
        '    async with httpx.AsyncClient() as http_client:',
        '        config = ClientConfig(',
        '            httpx_client=http_client, streaming=False,',
        '            supported_protocol_bindings=[',
        '                TransportProtocol.JSONRPC])',
        '',
        '        # fetches the card AND picks the transport',
        '        client = await ClientFactory(config) \\',
        '            .create_from_url("http://localhost:9999")',
        '',
        '        request = SendMessageRequest(',
        '            message=Message(role=Role.ROLE_USER,',
        '                            parts=[Part(text="Sara")],',
        '                            message_id="msg-1"))',
        '        async for event in client.send_message(request):',
        '            if event.HasField("message"): ...',
    ], size=10.5, title="11_sdk_client.py")

    box(s, XR, BODY_TOP + 0.06, HALF, 1.62, "Careful — two spellings of one protocol",
        ["The SDK objects use the **protobuf** flavour: `Role.ROLE_USER`, "
         "`event.HasField(\"message\")`. Files 01–09 use the **JSON-RPC** flavour: "
         "`\"user\"`, `\"message/send\"`, `{\"kind\": \"text\"}`.",
         "~~Same protocol, same wire, different names in the docs.~~"],
        size=12, fill=TINT2)

    heading(s, XR, 3.22, HALF, "What the extra code buys you")
    table(s, XR, 3.54, HALF, [
        ["You wrote by hand", "The SDK hands you"],
        ["one-shot replies", "streaming over SSE"],
        ["nothing", "task tracking + `tasks/get`"],
        ["nothing", "auth and push notifications"],
        ["one transport", "JSON-RPC, gRPC or REST"],
    ], widths=[2.9, 3.0], row_h=0.38)

    box(s, M, 5.80, CW, 1.02, "The same lesson as Session 6's raw-vs-LangChain",
        ["*\"More code for a hello-world — but you get streaming, task tracking, auth "
         "and push notifications for free. That is the trade: ~~structure now, power later~~.\"*",
         "Google ADK, LangGraph and CrewAI all speak A2A. The protocol reached v1.0 "
         "and is governed under the Linux Foundation."], size=12.5)


def build(prs):
    _s24_the_files(prs)
    _s25_file02(prs)
    _s26_file03(prs)
    _s27_specialists(prs)
    _s28_orchestrator_a(prs)
    _s29_orchestrator_b(prs)
    _s30_file07(prs)
    _s31_file08(prs)
    _s32_opacity(prs)
    _s33_file09(prs)
    _s34_file10(prs)
    _s35_file11(prs)
