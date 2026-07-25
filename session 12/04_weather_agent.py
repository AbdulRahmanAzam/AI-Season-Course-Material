"""
FILE 4: A SPECIALIST agent — Weather (built by hand, still no SDK)
==================================================================
Remember Session 6, FILE 5? There, `get_weather` and `convert_currency` were
TOOLS that your ONE agent called directly. That is the MCP idea:
        agent  --->  tool        (an agent using its own tools)

A2A does something different. We take that SAME weather capability and turn it
into its OWN independent agent: its own address, its own Agent Card, running as
its own server. Now ANY other agent can discover it and hire it over the network:
        agent  --->  AGENT       (an agent delegating to another agent)

This file is the Weather Agent. FILE 5 is the Currency Agent. FILE 6 is an
orchestrator that discovers BOTH and routes questions to the right one.

RUN:  python 04_weather_agent.py     (listens on port 8002)
"""

import sys
from fastapi import FastAPI, Request
import uvicorn

try:                                    # let emoji / dashes print on Windows consoles
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

app = FastAPI()

# Same fake data as Session 6 FILE 5 — so you can see it's the same capability,
# just wrapped as a standalone agent now.
FAKE_WEATHER = {"karachi": "34 C, sunny", "london": "18 C, rainy", "tokyo": "25 C, cloudy"}


def look_up_weather(text: str) -> str:
    """The agent's actual 'skill': find a known city in the text and report it."""
    text = text.lower()
    for city, weather in FAKE_WEATHER.items():
        if city in text:
            return f"The weather in {city.title()} is {weather}."
    return "I can report Karachi, London, or Tokyo. Which city did you mean?"


# The Agent Card — note the skill tags. The orchestrator will match on these.
AGENT_CARD = {
    "name": "Weather Agent",
    "description": "Reports the current weather for a city.",
    "url": "http://localhost:8002/",
    "version": "1.0.0",
    "defaultInputModes": ["text"],
    "defaultOutputModes": ["text"],
    "capabilities": {"streaming": False, "pushNotifications": False},
    "skills": [
        {
            "id": "get_weather",
            "name": "Get weather",
            "description": "Returns the current weather for a city.",
            "tags": ["weather", "forecast", "temperature", "rain"],   # <-- routing keywords
            "examples": ["What's the weather in Tokyo?"],
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
        print(f"[weather-agent] was asked: {user_text!r}")
        answer = look_up_weather(user_text)              # do the actual work
        reply = {
            "role": "agent",
            "parts": [{"kind": "text", "text": answer}],
            "messageId": "weather-reply",
        }
        return {"jsonrpc": "2.0", "id": rpc.get("id"), "result": reply}
    return {"jsonrpc": "2.0", "id": rpc.get("id"),
            "error": {"code": -32601, "message": "Method not found"}}


if __name__ == "__main__":
    print("Weather Agent (A2A) running at http://localhost:8002")
    uvicorn.run(app, host="127.0.0.1", port=8002)
