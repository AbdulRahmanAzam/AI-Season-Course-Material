"""
THE AGENT BASE -- what every debate agent is made of
====================================================
This is the "agent base" both debaters share. Session 12 wrote the same server
code four times (files 02, 04, 05, 07, 08). Here it is written ONCE.

An A2A agent keeps exactly two promises. That is the whole protocol:

    1. it publishes an AGENT CARD      ->  GET  /.well-known/agent-card.json
    2. it answers JSON-RPC calls       ->  POST /   with "message/send"

In session 12 those two promises were HTTP endpoints on a FastAPI server.
Here they are two Python methods -- get_agent_card() and handle_rpc() -- so the
whole debate runs in ONE terminal. Everything else is byte-for-byte the same
A2A: the same card fields, the same JSON-RPC envelope, the same Task object.
Wrapping these two methods back in FastAPI is a 10-line job (see the README).

The one field that matters most here is contextId:

    contextId = "which conversation is this?"

Each agent keeps a memory dict keyed by contextId. That is how an agent
remembers a debate without ever seeing the other agent's memory. "Each agent
has its own memory" stops being a Python variable and becomes a protocol idea.
"""

import os
import uuid
from datetime import datetime, timezone

from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage

load_dotenv()

MODEL = "openai/gpt-oss-120b"     # Groq's id for GPT-OSS 120B
MAX_MESSAGES = 20                 # 10 turns each, then a referee steps in

LLM = ChatGroq(model=MODEL, temperature=0.7, max_tokens=400, reasoning_effort="low")


def _now():
    """A2A timestamps are ISO 8601."""
    return datetime.now(timezone.utc).isoformat()


def _id(prefix):
    return f"{prefix}-{uuid.uuid4().hex[:8]}"


# ============================================================
#  THE AGENT
# ============================================================

class DebateAgent:
    """One A2A agent that argues one side of a claim."""

    def __init__(self, name, description, url, skill, side, opening_verdict,
                 persona_intro, llm=None):
        # ---- THE AGENT CARD: how this agent introduces itself ----
        self.card = {
            "name": name,
            "description": description,
            "url": url,                     # where messages are POSTed (see README)
            "version": "1.0.0",
            "defaultInputModes": ["text"],
            "defaultOutputModes": ["text"],
            "capabilities": {"streaming": False, "pushNotifications": False},
            "skills": [skill],              # what it can actually DO
        }

        self.side = side                    # "TRUE" or "FALSE" -- which way it argues
        self.opening_verdict = opening_verdict
        self.llm = llm or LLM

        # NOT part of the card. The card is public -- it is how OTHER agents
        # decide whether to hire this one. The persona is this agent's private
        # instructions to itself. Never put your prompt in your Agent Card.
        self.persona_intro = persona_intro

        self.memory = {}                    # contextId -> [messages]   ITS OWN memory
        self.tasks = {}                     # taskId    -> Task object

    # --------------------------------------------------------
    #  PROMISE 1 -- DISCOVERY
    #  real agent:  GET /.well-known/agent-card.json
    # --------------------------------------------------------
    def get_agent_card(self):
        return self.card

    # --------------------------------------------------------
    #  PROMISE 2 -- THE A2A ENDPOINT
    #  real agent:  POST /   with a JSON-RPC 2.0 body
    # --------------------------------------------------------
    def handle_rpc(self, rpc):
        method = rpc.get("method")

        if method == "message/send":
            return self._message_send(rpc)

        if method == "tasks/get":
            task = self.tasks.get(rpc["params"]["id"])
            if task:
                return {"jsonrpc": "2.0", "id": rpc.get("id"), "result": task}
            return {"jsonrpc": "2.0", "id": rpc.get("id"),
                    "error": {"code": -32001, "message": "Task not found"}}

        return {"jsonrpc": "2.0", "id": rpc.get("id"),
                "error": {"code": -32601, "message": f"Method not found: {method}"}}

    # --------------------------------------------------------
    #  message/send -- the only method that does real work
    # --------------------------------------------------------
    def _message_send(self, rpc):
        incoming = rpc["params"]["message"]
        context_id = incoming.get("contextId") or _id("ctx")
        text_in = incoming["parts"][0]["text"]

        # the orchestrator tells us how far along the debate is, in metadata
        count = incoming.get("metadata", {}).get("debateMessageCount", 0)

        # ---- A TASK is born the moment we accept the work ----
        task = {
            "id": _id("task"),
            "contextId": context_id,
            "status": {"state": "submitted", "timestamp": _now()},
            "history": [incoming],
            "artifacts": [],
            "kind": "task",
        }
        self.tasks[task["id"]] = task

        # ---- MY memory for THIS debate. Nobody else can see this list. ----
        history = self.memory.setdefault(context_id, [])
        history.append(HumanMessage(text_in))       # what they said TO me

        # ---- submitted -> working ----
        task["status"] = {"state": "working", "timestamp": _now()}

        # think. (streaming here is just console output -- the card says
        # streaming: false because we do not offer message/stream.)
        prompt = [SystemMessage(self.persona(count))] + history
        reply_text = ""
        for chunk in self.llm.stream(prompt):
            print(chunk.content, end="", flush=True)
            reply_text += chunk.content

        history.append(AIMessage(reply_text))       # what I said, in MY memory

        # ---- the answer, wrapped as an A2A message ----
        agent_message = {
            "role": "agent",
            "parts": [{"kind": "text", "text": reply_text}],
            "messageId": _id("msg"),
            "taskId": task["id"],
            "contextId": context_id,
            "kind": "message",
        }

        # ---- working -> completed, with the result as an ARTIFACT ----
        task["history"].append(agent_message)
        task["artifacts"] = [{
            "artifactId": _id("artifact"),
            "name": "argument",
            "parts": [{"kind": "text", "text": reply_text}],
        }]
        task["status"] = {"state": "completed", "timestamp": _now(),
                          "message": agent_message}

        return {"jsonrpc": "2.0", "id": rpc.get("id"), "result": task}

    # --------------------------------------------------------
    #  this agent's personality
    # --------------------------------------------------------
    def persona(self, count):
        """Rebuilt every turn: the PHASE line changes as time runs out, which
        is what stops the two of them arguing forever."""
        if count < 10:
            phase = "PHASE: Argue hard. Do not concede."
        elif count < 15:
            phase = ("PHASE: Name the strongest point your opponent has made "
                     "and say what is true about it.")
        else:
            phase = ("PHASE: Time is nearly up. You MUST reach a shared verdict with "
                     "your opponent. If their case is stronger than yours, change "
                     "your VERDICT to match theirs.")

        return (
            f"{self.persona_intro}\n\n"
            "Rules:\n"
            "- Maximum 3 sentences. Talk directly to your opponent.\n"
            "- Answer their last point before you make a new one.\n"
            "- NEVER repeat an argument you have already used. Bring a new one, or "
            "admit you are out of new arguments and move toward a verdict.\n"
            "- End every reply with exactly one line:  VERDICT: YES  or  VERDICT: NO\n"
            f"- VERDICT is your honest answer to the claim right now. "
            f"You start at {self.opening_verdict}.\n\n"
            + phase
        )


# ============================================================
#  THE CLIENT SIDE -- how one agent talks to another
# ============================================================

def send_message(agent, text, context_id, count=0):
    """Build a JSON-RPC 'message/send' call, hand it over, return the Task.

    In session 12 this line was:   requests.post(card["url"], json=rpc).json()
    Here it is:                    agent.handle_rpc(rpc)
    Same envelope either way.
    """
    rpc = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "message/send",
        "params": {
            "message": {
                "role": "user",
                "parts": [{"kind": "text", "text": text}],
                "messageId": _id("msg"),
                "contextId": context_id,                 # which debate this is
                "metadata": {"debateMessageCount": count},
                "kind": "message",
            }
        },
    }
    response = agent.handle_rpc(rpc)
    return response["result"]


def task_text(task):
    """Pull the agent's answer out of a completed Task."""
    return task["artifacts"][0]["parts"][0]["text"]


def read_verdict(text, fallback):
    """Pull the VERDICT line out of a reply. Keep the old one if it is missing."""
    upper = text.upper()
    yes = upper.rfind("VERDICT: YES")
    no = upper.rfind("VERDICT: NO")
    if yes == -1 and no == -1:
        return fallback
    return "YES" if yes > no else "NO"


def require_key():
    if not os.getenv("GROQ_API_KEY", "").strip():
        raise SystemExit("Add GROQ_API_KEY to .env  ->  https://console.groq.com/keys")


# ============================================================
#  THE TWO DEBATERS -- same base, opposite orders
# ============================================================

def make_pro(topic):
    return DebateAgent(
        name="Debate Agent (PRO)",
        description="Argues that a given claim is true and defends it.",
        url="http://localhost:8010/",
        skill={
            "id": "argue_for",
            "name": "Argue in favour",
            "description": "Argues that a given claim is true, and defends it.",
            "tags": ["debate", "argue", "for", "pro"],
            "examples": ["Toyota is better than every other car brand."],
        },
        side="TRUE",
        opening_verdict="YES",
        persona_intro=f'You are PRO. You argue that "{topic}" is TRUE.',
    )


def make_con(topic):
    return DebateAgent(
        name="Debate Agent (CON)",
        description="Argues that a given claim is false and attacks it.",
        url="http://localhost:8011/",
        skill={
            "id": "argue_against",
            "name": "Argue against",
            "description": "Argues that a given claim is false, and attacks it.",
            "tags": ["debate", "argue", "against", "con"],
            "examples": ["Toyota is better than every other car brand."],
        },
        side="FALSE",
        opening_verdict="NO",
        persona_intro=f'You are CON. You argue that "{topic}" is FALSE.',
    )


# ============================================================
#  A THIRD AGENT -- and this is what the agent base buys you
# ============================================================

class RefereeAgent(DebateAgent):
    """Same base class, different job. A new agent is a new CARD and a new
    PERSONA -- not a new server, not a new protocol, not a new memory system.
    It inherits discovery, message/send, tasks/get and Task tracking for free.
    """

    def persona(self, count):
        return (
            "You are a neutral referee in a debate. The two debaters ran out of "
            "time without agreeing. Read the debate you were given and decide "
            "which side argued better.\n\n"
            "Reply with exactly one line 'VERDICT: YES' or 'VERDICT: NO', "
            "then one sentence saying why."
        )


def make_referee(topic):
    return RefereeAgent(
        name="Debate Referee",
        description="Reads a debate transcript and declares which side argued better.",
        url="http://localhost:8012/",
        skill={
            "id": "judge_debate",
            "name": "Judge a debate",
            "description": "Reads a full debate transcript and declares the winning side.",
            "tags": ["debate", "judge", "referee", "verdict"],
            "examples": ["PRO said... CON said... who won?"],
        },
        side="NEUTRAL",
        opening_verdict="NONE",
        persona_intro="You are a neutral referee.",
        llm=ChatGroq(model=MODEL, temperature=0, max_tokens=600, reasoning_effort="low"),
    )
