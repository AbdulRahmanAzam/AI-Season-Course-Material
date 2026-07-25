"""
FILE 9: A SMARTER orchestrator — the router is an LLM too
=========================================================
FILE 6 routed by simple keyword matching. This orchestrator asks a Groq LLM
"which of these agents should handle this question?" — so it can route messy,
real-world phrasing that keyword matching would miss.

It works with EITHER set of specialists, because they share the same ports:
    - the hand-made agents (FILE 4 + FILE 5), OR
    - the LLM agents          (FILE 7 + FILE 8)

Falls back to keyword routing (FILE 6 logic) when there's no Groq key.

RUN (3 terminals) — start any weather agent + any currency agent, then:
    Terminal 1:  python 04_weather_agent.py     (or 07_llm_weather_agent.py)
    Terminal 2:  python 05_currency_agent.py     (or 08_llm_currency_agent.py)
    Terminal 3:  python 09_llm_orchestrator.py
"""

import os
import sys
import uuid
import requests
from dotenv import load_dotenv

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

load_dotenv()
MODEL = "openai/gpt-oss-120b"
KNOWN_AGENTS = ["http://localhost:8002", "http://localhost:8003"]


def use_mock() -> bool:
    key = os.getenv("GROQ_API_KEY", "").strip()
    provider = os.getenv("LLM_PROVIDER", "mock").strip().lower()
    return provider == "mock" or not key or key == "your_groq_key_here"


def discover(agent_urls):
    """Fetch every agent's card -> our directory of who-can-do-what."""
    directory = []
    for base in agent_urls:
        card = requests.get(f"{base}/.well-known/agent-card.json").json()
        directory.append(card)
        print(f"  found '{card['name']}': {card['skills'][0]['description']}")
    return directory


def choose_agent(directory, question):
    """Decide which agent should answer. LLM if available, else keywords."""
    if use_mock():
        q = question.lower()                            # FILE 6 keyword routing
        for card in directory:
            for skill in card["skills"]:
                keywords = skill["tags"] + [skill["id"], skill["name"].lower()]
                if any(w.lower() in q for w in keywords):
                    return card
        return None

    from groq import Groq                               # LLM router
    client = Groq()
    catalog = "\n".join(f"- {c['name']}: {c['skills'][0]['description']}" for c in directory)
    system = (
        "You are a router. Pick the single best agent for the user's question. "
        "Reply with ONLY the agent's exact name, nothing else.\n\nAgents:\n" + catalog
    )
    choice = client.chat.completions.create(
        model=MODEL, temperature=0,
        messages=[{"role": "system", "content": system},
                  {"role": "user", "content": question}],
    ).choices[0].message.content.strip()
    for card in directory:                              # match the name back to a card
        if card["name"].lower() in choice.lower():
            return card
    return None


def ask_agent(card, question):
    """Delegate the question to the chosen agent via A2A message/send."""
    rpc_request = {
        "jsonrpc": "2.0", "id": 1, "method": "message/send",
        "params": {"message": {
            "role": "user",
            "parts": [{"kind": "text", "text": question}],
            "messageId": uuid.uuid4().hex,
        }},
    }
    response = requests.post(card["url"], json=rpc_request).json()
    return response["result"]["parts"][0]["text"]


if __name__ == "__main__":
    print(f"Smart Trip Assistant  [router: {'keywords (mock)' if use_mock() else 'Groq LLM'}]")
    print("Discovering agents...")
    directory = discover(KNOWN_AGENTS)

    for question in ["I'm flying to Tokyo soon - what's the weather there?",
                     "I've got 100 USD, can you convert it to PKR?"]:
        print("\n" + "-" * 55)
        print("User asks: ", question)
        chosen = choose_agent(directory, question)
        if chosen is None:
            print("  No suitable agent found.")
            continue
        print(f"  -> delegating to: {chosen['name']}")
        print(f"  -> answer: {ask_agent(chosen, question)}")
