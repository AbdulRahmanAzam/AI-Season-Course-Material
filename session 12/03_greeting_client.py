"""
FILE 3: Talking to an A2A agent — the CLIENT side
==================================================
An A2A "client" is whoever starts the conversation. It does 3 simple steps:

    1. DISCOVER — read the agent's card to learn its address + skills.
    2. SEND     — POST a JSON-RPC "message/send" with the user's text.
    3. READ     — pull the reply text out of the response.

That's it. No SDK — just the `requests` library you already know.

HOW TO RUN:
    Terminal 1 (must be running first):   python 02_greeting_agent.py
    Terminal 2:                           python 03_greeting_client.py
"""

import sys
import uuid
import requests   # the same dead-simple HTTP client used across the course

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

AGENT_BASE = "http://localhost:8001"

# 1) DISCOVER ----------------------------------------------------------------
# Fetch the card from the well-known path to learn who we're talking to.
card = requests.get(f"{AGENT_BASE}/.well-known/agent-card.json").json()
print("Discovered an agent!")
print("   name:  ", card["name"])
print("   can do:", [skill["name"] for skill in card["skills"]])
print("   talk to it at:", card["url"])

# 2) SEND --------------------------------------------------------------------
# Build a JSON-RPC 2.0 request. The important part is params.message.
rpc_request = {
    "jsonrpc": "2.0",
    "id": 1,                              # any id; the reply echoes it back
    "method": "message/send",             # the A2A method we are calling
    "params": {
        "message": {
            "role": "user",               # this message is from the user (us)
            "parts": [                    # content is a LIST of "parts"...
                {"kind": "text", "text": "Sara"}   # ...here, one text part
            ],
            "messageId": uuid.uuid4().hex,   # a unique id for this message
        }
    },
}

print("\nSending name:", rpc_request["params"]["message"]["parts"][0]["text"])
response = requests.post(card["url"], json=rpc_request).json()
print("\n[client] raw JSON-RPC response:", response)

# 3) READ --------------------------------------------------------------------
# Dig the agent's text back out of result -> parts -> [0] -> text.
reply_text = response["result"]["parts"][0]["text"]
print("\nAgent replied:", reply_text)
