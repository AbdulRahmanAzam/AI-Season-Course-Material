"""
FILE 7: The Weather Agent — now with a REAL BRAIN (Groq LLM)
============================================================
FILE 4's weather agent used a dumb dict lookup. This one uses a real LLM
(Groq, model openai/gpt-oss-120b) to phrase its answer.

The magic point to say out loud in class:
    The Agent Card and the "/" endpoint are IDENTICAL to FILE 4.
    It still listens on port 8002. So the orchestrator (FILE 6) can talk to
    THIS agent without changing a single line — it has no idea whether the
    agent's brain is a dict or a 120-billion-parameter model. That hiding of
    internals is exactly what makes A2A powerful: agents are "black boxes"
    that only agree on the protocol.

No Groq key? No problem — it falls back to MOCK mode automatically (same
offline lookup as FILE 4), so the demo always runs.

RUN:  python 07_llm_weather_agent.py     (listens on port 8002)
"""

import os
import sys
from dotenv import load_dotenv
from fastapi import FastAPI, Request
import uvicorn

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

load_dotenv()
MODEL = "openai/gpt-oss-120b"   # Groq's id for GPT-OSS 120B (swap for llama-3.3-70b-versatile if you like)

FAKE_WEATHER = {"karachi": "34 C, sunny", "london": "18 C, rainy", "tokyo": "25 C, cloudy"}


def use_mock() -> bool:
    """Same rule the rest of the course uses: mock unless a real Groq key is set."""
    key = os.getenv("GROQ_API_KEY", "").strip()
    provider = os.getenv("LLM_PROVIDER", "mock").strip().lower()
    return provider == "mock" or not key or key == "your_groq_key_here"


def weather_brain(user_text: str) -> str:
    """Answer a weather question — via the LLM, or an offline fallback."""
    if use_mock():
        text = user_text.lower()                       # offline fallback = FILE 4 logic
        for city, weather in FAKE_WEATHER.items():
            if city in text:
                return f"The weather in {city.title()} is {weather}."
        return "I can report Karachi, London, or Tokyo."

    from groq import Groq                               # real LLM path
    client = Groq()                                     # reads GROQ_API_KEY from env
    system = (
        "You are a Weather Agent. Only use this weather data: "
        f"{FAKE_WEATHER}. If the city is not in it, say you don't have that city. "
        "Answer in ONE short, friendly sentence."
    )
    resp = client.chat.completions.create(
        model=MODEL, temperature=0,
        messages=[{"role": "system", "content": system},
                  {"role": "user", "content": user_text}],
    )
    return resp.choices[0].message.content.strip()


app = FastAPI()

# NOTE: identical card to FILE 4 (same name, same port) — this is a drop-in brain swap.
AGENT_CARD = {
    "name": "Weather Agent",
    "description": "Reports the current weather for a city.",
    "url": "http://localhost:8002/",
    "version": "1.0.0",
    "defaultInputModes": ["text"],
    "defaultOutputModes": ["text"],
    "capabilities": {"streaming": False, "pushNotifications": False},
    "skills": [{
        "id": "get_weather", "name": "Get weather",
        "description": "Returns the current weather for a city.",
        "tags": ["weather", "forecast", "temperature", "rain"],
        "examples": ["What's the weather in Tokyo?"],
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
        print(f"[weather-agent] asked: {user_text!r}")
        answer = weather_brain(user_text)
        reply = {"role": "agent",
                 "parts": [{"kind": "text", "text": answer}],
                 "messageId": "weather-reply"}
        return {"jsonrpc": "2.0", "id": rpc.get("id"), "result": reply}
    return {"jsonrpc": "2.0", "id": rpc.get("id"),
            "error": {"code": -32601, "message": "Method not found"}}


if __name__ == "__main__":
    mode = "MOCK (no Groq key)" if use_mock() else f"LIVE Groq · {MODEL}"
    print(f"Weather Agent (A2A) running at http://localhost:8002  [brain: {mode}]")
    uvicorn.run(app, host="127.0.0.1", port=8002)
