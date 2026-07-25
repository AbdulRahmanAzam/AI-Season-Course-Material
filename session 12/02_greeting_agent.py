"""
FILE 2: Your first A2A agent — built BY HAND (no SDK, no magic)
===============================================================
Big idea: an "A2A agent" is NOT some special magical thing. It is just a
normal web server that keeps two simple promises:

    1. It publishes an AGENT CARD (its resume) at a fixed address:
              /.well-known/agent-card.json
    2. It accepts a JSON-RPC request at "/" with the method "message/send",
       and replies with a message.

That is the WHOLE protocol for a basic agent. Once you see it is "just JSON
over HTTP", A2A stops being intimidating.

HOW TO RUN:
    Terminal 1:   python 02_greeting_agent.py
    Terminal 2:   python 03_greeting_client.py
    Or open in a browser:   http://localhost:8001/.well-known/agent-card.json
"""

import sys
from fastapi import FastAPI, Request   # a tiny web framework
import uvicorn                          # the server that actually runs FastAPI

try:                                    # so the 👋 emoji prints fine on Windows
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

app = FastAPI()


# 1) THE AGENT CARD ----------------------------------------------------------
# How this agent introduces itself. Any other agent can read this to learn:
# who are you, what can you do, and where do I send work?
AGENT_CARD = {
    "name": "Greeting Agent",
    "description": "A friendly agent that greets a person by name.",
    "url": "http://localhost:8001/",        # where to SEND messages (A2A endpoint)
    "version": "1.0.0",
    "defaultInputModes": ["text"],
    "defaultOutputModes": ["text"],
    "capabilities": {"streaming": False, "pushNotifications": False},
    "skills": [
        {
            "id": "greet",
            "name": "Greet a person",
            "description": "Says a warm hello to a person by name.",
            "tags": ["greeting", "hello"],
            "examples": ["Sara", "Ali"],
        }
    ],
}


# 2) THE DISCOVERY ENDPOINT --------------------------------------------------
# A2A says: publish your card at EXACTLY this path. Clients look here first.
@app.get("/.well-known/agent-card.json")
def get_agent_card():
    return AGENT_CARD


# 3) THE A2A ENDPOINT --------------------------------------------------------
# Every A2A call is JSON-RPC 2.0: a JSON body with a "method" and "params".
# A basic agent only needs to handle one method: "message/send".
@app.post("/")
async def handle_rpc(request: Request):
    rpc = await request.json()
    print("\n[server] incoming JSON-RPC:", rpc)   # show the raw wire format in class

    method = rpc.get("method")

    if method == "message/send":
        # The user's text lives at: params -> message -> parts -> [0] -> text
        user_text = rpc["params"]["message"]["parts"][0]["text"]

        # Do our "work". (Here it's trivial: build a greeting.)
        reply_text = f"Hello, {user_text}! Nice to meet you. 👋"

        # Wrap the answer as an A2A "message" spoken by the agent.
        agent_message = {
            "role": "agent",
            "parts": [{"kind": "text", "text": reply_text}],   # kind = "text" | "file" | "data"
            "messageId": "greeting-reply-1",
        }

        # JSON-RPC success: echo the same id, put the answer in "result".
        return {"jsonrpc": "2.0", "id": rpc.get("id"), "result": agent_message}

    # Any other method -> standard JSON-RPC "method not found" error.
    return {
        "jsonrpc": "2.0",
        "id": rpc.get("id"),
        "error": {"code": -32601, "message": f"Method not found: {method}"},
    }


if __name__ == "__main__":
    print("Greeting Agent (A2A) is running.")
    print("  Card:     http://localhost:8001/.well-known/agent-card.json")
    print("  Endpoint: http://localhost:8001/   (POST message/send here)")
    uvicorn.run(app, host="127.0.0.1", port=8001)
