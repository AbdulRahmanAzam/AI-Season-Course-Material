"""
FILE 5: A SPECIALIST agent — Currency (built by hand, still no SDK)
===================================================================
The twin of FILE 4. Same story: in Session 6 FILE 5, `convert_currency` was a
TOOL. Here it becomes its OWN agent with its own Agent Card and address.

Together, FILE 4 (weather) and FILE 5 (currency) are two independent agents that
know NOTHING about each other. FILE 6 (the orchestrator) is what makes them
useful as a team — by discovering each one's card and delegating the right job.

RUN:  python 05_currency_agent.py     (listens on port 8003)
"""

import re
import sys
from fastapi import FastAPI, Request
import uvicorn

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

app = FastAPI()

# Same fake rates as Session 6 FILE 5.
RATES = {"USD": 1.0, "PKR": 278.0, "EUR": 0.9}


def convert_currency(text: str) -> str:
    """The agent's skill: find the amount + the two currency codes, then convert.

    We look for currency codes we actually KNOW (USD/PKR/EUR) anywhere in the
    sentence, so messy phrasing like 'I have 100 USD, convert it to PKR' works.
    """
    amount_match = re.search(r"(\d+(?:\.\d+)?)", text)                 # the number
    codes = [w.upper() for w in re.findall(r"[A-Za-z]{3}", text)]      # every 3-letter word
    known = [c for c in codes if c in RATES]                           # keep only real currencies
    if not amount_match or len(known) < 2:
        return "Ask me like: 'convert 100 USD to PKR'. I know USD, PKR, EUR."
    amount = float(amount_match.group(1))
    frm, to = known[0], known[1]
    result = amount / RATES[frm] * RATES[to]
    return f"{amount:.0f} {frm} = {result:.0f} {to}"


AGENT_CARD = {
    "name": "Currency Agent",
    "description": "Converts money between currencies.",
    "url": "http://localhost:8003/",
    "version": "1.0.0",
    "defaultInputModes": ["text"],
    "defaultOutputModes": ["text"],
    "capabilities": {"streaming": False, "pushNotifications": False},
    "skills": [
        {
            "id": "convert_currency",
            "name": "Convert currency",
            "description": "Converts an amount from one currency to another.",
            "tags": ["currency", "convert", "exchange", "money", "forex"],  # routing keywords
            "examples": ["Convert 100 USD to PKR"],
        }
    ],
}


@app.get("/.well-known/agent-card.json")
def get_agent_card():
    return AGENT_CARD


@app.post("/")
async def handle_rpc(request: Request):
    rpc = await request.json()
    if rpc.get("method") == "message/send":
        user_text = rpc["params"]["message"]["parts"][0]["text"]
        print(f"[currency-agent] was asked: {user_text!r}")
        answer = convert_currency(user_text)
        reply = {
            "role": "agent",
            "parts": [{"kind": "text", "text": answer}],
            "messageId": "currency-reply",
        }
        return {"jsonrpc": "2.0", "id": rpc.get("id"), "result": reply}
    return {"jsonrpc": "2.0", "id": rpc.get("id"),
            "error": {"code": -32601, "message": "Method not found"}}


if __name__ == "__main__":
    print("Currency Agent (A2A) running at http://localhost:8003")
    uvicorn.run(app, host="127.0.0.1", port=8003)
