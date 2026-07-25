"""
FILE 1: The Agent Card — an agent's resume / business card
===========================================================
Before two agents can work together, they must answer one question:
        "Who are you, and what can you do?"

A2A (Agent2Agent) solves this with the AGENT CARD: a small JSON document that
every agent publishes about itself at ONE fixed web address:

        https://<the-agent>/.well-known/agent-card.json

This file does NOT start a server. It just builds one card and walks through
every field, so the JSON stops looking scary.

Run me:   python 01_what_is_an_agent_card.py
"""

import json

# A real Agent Card is just a dictionary (which becomes JSON).
# Every field below is something ANOTHER agent reads to decide:
# "should I hire this agent, and how exactly do I talk to it?"
agent_card = {
    # --- WHO am I? -----------------------------------------------------------
    "name": "Weather Agent",
    "description": "Tells the current weather for a city.",
    "version": "1.0.0",

    # --- WHERE do you reach me? ----------------------------------------------
    # The address other agents POST their messages to (the A2A endpoint).
    "url": "http://localhost:8002/",

    # --- HOW do we talk? -----------------------------------------------------
    # What input/output content types I default to. Here: plain text.
    "defaultInputModes": ["text"],
    "defaultOutputModes": ["text"],

    # --- WHICH protocol features do I support? -------------------------------
    "capabilities": {
        "streaming": False,          # can I send partial answers live? (via SSE)
        "pushNotifications": False,  # can I call a webhook when a long job is done?
    },

    # --- WHAT can I actually do? ---------------------------------------------
    # The heart of the card: a list of SKILLS. This is what a client scans
    # to decide whether THIS agent is the right one for a job.
    "skills": [
        {
            "id": "get_weather",
            "name": "Get weather",
            "description": "Returns the current weather for a given city.",
            "tags": ["weather", "forecast"],       # keywords others match against
            "examples": ["What's the weather in Tokyo?"],
        }
    ],
}

# ---- Show it ---------------------------------------------------------------
print("An Agent Card is just this JSON:\n")
print(json.dumps(agent_card, indent=2))

print("\nEvery card answers 3 questions:")
print("  1. WHO   ->", agent_card["name"], "-", agent_card["description"])
print("  2. WHERE ->", agent_card["url"], "  (send messages here)")
print("  3. WHAT  ->", [s["name"] for s in agent_card["skills"]], "  (its skills)")

print("\nIn real life this card is published at:")
print("   " + agent_card["url"].rstrip("/") + "/.well-known/agent-card.json")
print("...so ANY agent, built by ANY team, can fetch it and learn how to")
print("work with this agent. That is the whole idea of A2A: discovery.")
