"""
FILE 6: The ORCHESTRATOR — one agent that hires other agents  ⭐
================================================================
THIS is the whole point of A2A.

The orchestrator is itself an agent (a "client agent"). It does NOT know how to
do weather or currency. Instead it:

    1. DISCOVERS specialists by reading their Agent Cards.
    2. Looks at each card's skills/tags to decide WHO can help.
    3. DELEGATES the question to the right agent with "message/send".
    4. Returns that agent's answer.

(Recall Session 4's verifier: one LLM checking another LLM's work. Same spirit —
agents talking to agents. A2A just turns that into a standard protocol that works
across the network, even between agents built by totally different teams.)

RUN (need 3 terminals):
    Terminal 1:  python 04_weather_agent.py
    Terminal 2:  python 05_currency_agent.py
    Terminal 3:  python 06_orchestrator.py
"""

import sys
import uuid
import requests

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

# The specialists we know about. In the real world you might get these from a
# registry; here we just list their base URLs.
KNOWN_AGENTS = [
    "http://localhost:8002",   # weather
    "http://localhost:8003",   # currency
]


# 1) DISCOVER -- fetch every agent's card and build a little "directory". ------
def discover(agent_urls):
    directory = []
    for base in agent_urls:
        card = requests.get(f"{base}/.well-known/agent-card.json").json()
        directory.append(card)
        tags = [t for skill in card["skills"] for t in skill["tags"]]
        print(f"  found '{card['name']}'  ->  skills: {tags}")
    return directory


# 2) ROUTE -- pick the agent whose skill tags appear in the question. ----------
def pick_agent(directory, question):
    q = question.lower()
    for card in directory:
        for skill in card["skills"]:
            keywords = skill["tags"] + [skill["id"], skill["name"].lower()]
            if any(word.lower() in q for word in keywords):
                return card
    return None


# 3) DELEGATE -- send the question to that agent via A2A "message/send". -------
def ask_agent(card, question):
    rpc_request = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "message/send",
        "params": {
            "message": {
                "role": "user",
                "parts": [{"kind": "text", "text": question}],
                "messageId": uuid.uuid4().hex,
            }
        },
    }
    response = requests.post(card["url"], json=rpc_request).json()
    return response["result"]["parts"][0]["text"]


if __name__ == "__main__":
    print("Trip Assistant (orchestrator) starting up.")
    print("Discovering the agents it can work with...")
    directory = discover(KNOWN_AGENTS)

    # A few user questions. The orchestrator figures out who should answer each.
    questions = [
        "What's the weather in Tokyo?",
        "Convert 100 USD to PKR",
        "Is it raining in London?",
    ]

    for question in questions:
        print("\n" + "-" * 55)
        print("User asks: ", question)
        chosen = pick_agent(directory, question)
        if chosen is None:
            print("  No agent I know can handle that.")
            continue
        print(f"  -> delegating to: {chosen['name']}")
        answer = ask_agent(chosen, question)
        print(f"  -> answer: {answer}")
