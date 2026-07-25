"""
FILE 8: The Currency Agent — now with a REAL BRAIN (Groq LLM)
=============================================================
Twin of FILE 7. Same Agent Card and port (8003) as FILE 5, so it is a drop-in
replacement — the orchestrator can't tell the difference.

Teaching note: we still keep the ACTUAL math in Python (deterministic) and let
the LLM only phrase the reply. A real production agent often works like this:
code does the exact/critical part, the LLM does the natural-language part.

Falls back to MOCK mode with no Groq key.

RUN:  python 08_llm_currency_agent.py     (listens on port 8003)
"""

import os
import re
import sys
from dotenv import load_dotenv
from fastapi import FastAPI, Request
import uvicorn

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

load_dotenv()
MODEL = "openai/gpt-oss-120b"
RATES = {"USD": 1.0, "PKR": 278.0, "EUR": 0.9}


def use_mock() -> bool:
    key = os.getenv("GROQ_API_KEY", "").strip()
    provider = os.getenv("LLM_PROVIDER", "mock").strip().lower()
    return provider == "mock" or not key or key == "your_groq_key_here"


def do_math(text: str):
    """Find the amount + the two KNOWN currency codes in the text and convert.

    Scanning for codes we know (USD/PKR/EUR) is more robust than guessing by
    position, so 'I have 100 USD, convert it to PKR' parses correctly.
    """
    amount_match = re.search(r"(\d+(?:\.\d+)?)", text)
    codes = [w.upper() for w in re.findall(r"[A-Za-z]{3}", text)]
    known = [c for c in codes if c in RATES]
    if not amount_match or len(known) < 2:
        return None
    amount = float(amount_match.group(1))
    frm, to = known[0], known[1]
    return amount, frm, to, amount / RATES[frm] * RATES[to]


def currency_brain(user_text: str) -> str:
    result = do_math(user_text)
    if result is None:
        return f"Ask me like 'convert 100 USD to PKR'. I know {', '.join(RATES)}."
    amount, frm, to, converted = result

    if use_mock():
        return f"{amount:.0f} {frm} = {converted:.0f} {to}"           # offline fallback

    from groq import Groq                                              # LLM just phrases it
    client = Groq()
    system = "You are a Currency Agent. Rephrase the given conversion result in one friendly sentence. Do not change the numbers."
    fact = f"{amount:.0f} {frm} = {converted:.2f} {to}"
    resp = client.chat.completions.create(
        model=MODEL, temperature=0.3,
        messages=[{"role": "system", "content": system},
                  {"role": "user", "content": f"Conversion: {fact}"}],
    )
    return resp.choices[0].message.content.strip()


app = FastAPI()

# Identical card to FILE 5 (same name, same port 8003).
AGENT_CARD = {
    "name": "Currency Agent",
    "description": "Converts money between currencies.",
    "url": "http://localhost:8003/",
    "version": "1.0.0",
    "defaultInputModes": ["text"],
    "defaultOutputModes": ["text"],
    "capabilities": {"streaming": False, "pushNotifications": False},
    "skills": [{
        "id": "convert_currency", "name": "Convert currency",
        "description": "Converts an amount from one currency to another.",
        "tags": ["currency", "convert", "exchange", "money", "forex"],
        "examples": ["Convert 100 USD to PKR"],
    }],
}


@app.get("/.well-known/agent-card.json")
def get_agent_card():
    return AGENT_CARD


@app.post("/")
async def handle_rpc(request: Request):
    rpc = await request.json()
    if rpc.get("method") == "message/send":
        user_text = rpc["params"]["message"]["parts"][0]["text"]
        print(f"[currency-agent] asked: {user_text!r}")
        answer = currency_brain(user_text)
        reply = {"role": "agent",
                 "parts": [{"kind": "text", "text": answer}],
                 "messageId": "currency-reply"}
        return {"jsonrpc": "2.0", "id": rpc.get("id"), "result": reply}
    return {"jsonrpc": "2.0", "id": rpc.get("id"),
            "error": {"code": -32601, "message": "Method not found"}}


if __name__ == "__main__":
    mode = "MOCK (no Groq key)" if use_mock() else f"LIVE Groq · {MODEL}"
    print(f"Currency Agent (A2A) running at http://localhost:8003  [brain: {mode}]")
    uvicorn.run(app, host="127.0.0.1", port=8003)
