"""
FILE 2: The SAME debate, but LangGraph runs it
==============================================
FILE 1 ran the debate with a while loop and an if/else. That works, but the
rules of the conversation were scattered all over the loop body.

LangGraph lets us draw the conversation instead:

        START ---> pro_agent ---.
                                 >--- whose_turn? ---> pro_agent
                   con_agent ---'                      con_agent
                                                       referee
                                                       END
                   referee ---> END

Three new ideas, and nothing else:

  1. STATE      one dictionary that every node reads and updates.
                Ours holds TWO separate memories -- one per agent.
  2. NODES      a node is just a Python function: state in, updates out.
  3. CONDITIONAL EDGE
                after each node, a small function decides where to go next.
                Pointing it back at an earlier node is what makes a LOOP.

The debate always ends with both agents on the SAME answer:
  - if they agree on their own, the graph stops early
  - if 20 messages go by and they still disagree, a referee node breaks the tie

While it runs it writes transcripts/debate_<topic>.md / .json / .html.
Double-click the .html BEFORE it finishes -- the page refreshes itself every
2 seconds, so the class can watch the chat fill up in a browser.

RUN:  python 02_debate_graph.py
      python 02_debate_graph.py "Python is better than JavaScript"
"""

import os
import sys
import time
import operator
from typing import Annotated
from typing_extensions import TypedDict

from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages

import live_transcript

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

load_dotenv()

MODEL = "openai/gpt-oss-120b"
MAX_MESSAGES = 20                 # 10 turns each, then the referee steps in
TOPIC = "Toyota is better than every other car brand."

if len(sys.argv) > 1:
    TOPIC = " ".join(sys.argv[1:])

if not os.getenv("GROQ_API_KEY", "").strip():
    print("Add GROQ_API_KEY to .env  ->  https://console.groq.com/keys")
    sys.exit(1)

LLM = ChatGroq(model=MODEL, temperature=0.7, max_tokens=600, reasoning_effort="low")
REFEREE_LLM = ChatGroq(model=MODEL, temperature=0, max_tokens=600, reasoning_effort="low")

LIVE = None                       # the transcript writer, created in __main__


# ============================================================
#  1. STATE -- the one dictionary the whole graph shares
# ============================================================

class DebateState(TypedDict):
    topic: str
    pro_memory: Annotated[list, add_messages]   # PRO's private context
    con_memory: Annotated[list, add_messages]   # CON's private context
    transcript: Annotated[list, operator.add]   # the public log both files use
    pro_verdict: str                            # "YES" / "NO" / ""
    con_verdict: str
    count: int                                  # messages spoken so far


# Annotated[..., add_messages] and Annotated[..., operator.add] mean "ADD to
# this list", not "replace it". Every other field is replaced by whatever a
# node returns for it.


# ============================================================
#  2. THE TWO PERSONALITIES
# ============================================================

def persona(who, topic, count):
    """System prompt for one agent. Rebuilt every turn, because the PHASE
    line changes as the debate runs out of time -- that is what pushes them
    to stop repeating themselves and actually agree on something."""
    if who == "PRO":
        side, start = "TRUE", "YES"
    else:
        side, start = "FALSE", "NO"

    if count < 10:
        phase = "PHASE: Argue hard. Do not concede."
    elif count < 15:
        phase = ("PHASE: Name the strongest point your opponent has made "
                 "and say what is true about it.")
    else:
        phase = ("PHASE: Time is nearly up. You MUST reach a shared verdict with "
                 "your opponent. If their case is stronger than yours, change your "
                 "VERDICT to match theirs.")

    return (
        f'You are {who}. You argue that "{topic}" is {side}.\n\n'
        "Rules:\n"
        "- Maximum 3 sentences. Talk directly to your opponent.\n"
        "- Answer their last point before you make a new one.\n"
        "- NEVER repeat an argument you have already used. Bring a new one, or "
        "admit you are out of new arguments and move toward a verdict.\n"
        "- End every reply with exactly one line:  VERDICT: YES  or  VERDICT: NO\n"
        f"- VERDICT is your honest answer to the claim right now. You start at {start}.\n\n"
        + phase
    )


def read_verdict(text, fallback):
    """Pull the VERDICT line out of a reply. Keep the old one if it is missing."""
    upper = text.upper()
    yes = upper.rfind("VERDICT: YES")
    no = upper.rfind("VERDICT: NO")
    if yes == -1 and no == -1:
        return fallback
    return "YES" if yes > no else "NO"


# ============================================================
#  3. NODES -- plain functions: state in, updates out
# ============================================================

def speak(state, who):
    """One agent takes one turn. Both agent nodes are this same function."""
    mine, theirs = ("pro_memory", "con_memory") if who == "PRO" else ("con_memory", "pro_memory")

    # this agent's OWN context: its persona + everything it has heard and said.
    # the persona is NOT stored in memory -- we rebuild it fresh every turn.
    messages = [SystemMessage(persona(who, state["topic"], state["count"]))] + state[mine]

    print(f"\n[{state['count'] + 1}] {who}: ", end="", flush=True)
    text = ""
    for chunk in LLM.stream(messages):          # stream = the class sees it typing
        print(chunk.content, end="", flush=True)
        text += chunk.content
    print()

    verdict = read_verdict(text, state[f"{who.lower()}_verdict"])
    LIVE.add(who, text, verdict)                # .md + .json + .html, right now
    time.sleep(1)                               # paces the chat, eases the free tier

    return {
        mine:   [AIMessage(text)],                     # my words -> MY memory, as "assistant"
        theirs: [HumanMessage(f"{who}: {text}")],      # ...and -> THEIR memory, as "user"
        "transcript": [{"n": state["count"] + 1, "who": who,
                        "text": text, "verdict": verdict}],
        f"{who.lower()}_verdict": verdict,
        "count": state["count"] + 1,
    }


def pro_agent(state):
    return speak(state, "PRO")


def con_agent(state):
    return speak(state, "CON")


def referee(state):
    """Only runs if all 20 messages went by and they STILL disagree.
    One neutral call decides it, and both agents adopt that answer -- so
    every single run ends with the two of them on the same side."""
    debate = "\n".join(f"{m['who']}: {m['text']}" for m in state["transcript"])
    prompt = (
        f'Two agents debated this claim: "{state["topic"]}"\n\n'
        f"{debate}\n\n"
        "You are a neutral referee. They ran out of time without agreeing. "
        "Decide which side argued better.\n"
        "Reply with exactly one line 'VERDICT: YES' or 'VERDICT: NO', "
        "then one sentence saying why."
    )

    print(f"\n[referee] no agreement in {MAX_MESSAGES} messages -- deciding: ",
          end="", flush=True)
    text = ""
    for chunk in REFEREE_LLM.stream([HumanMessage(prompt)]):
        print(chunk.content, end="", flush=True)
        text += chunk.content
    print()

    verdict = read_verdict(text, "NO")
    LIVE.add("REFEREE", text, verdict)
    return {"pro_verdict": verdict, "con_verdict": verdict,   # both now say the same thing
            "transcript": [{"n": state["count"] + 1, "who": "REFEREE",
                            "text": text, "verdict": verdict}]}


# ============================================================
#  4. THE CONDITIONAL EDGE -- where do we go after a turn?
# ============================================================

def whose_turn(state):
    """Runs after every agent node and returns the NAME of the next node."""
    if state["pro_verdict"] and state["pro_verdict"] == state["con_verdict"]:
        return END                                      # they agreed -> stop early
    if state["count"] >= MAX_MESSAGES:
        return "referee"                                # out of time -> break the tie
    return "con_agent" if state["count"] % 2 == 1 else "pro_agent"


# ============================================================
#  5. BUILD THE GRAPH
# ============================================================

builder = StateGraph(DebateState)
builder.add_node("pro_agent", pro_agent)
builder.add_node("con_agent", con_agent)
builder.add_node("referee", referee)

builder.add_edge(START, "pro_agent")                    # PRO always opens
builder.add_conditional_edges("pro_agent", whose_turn, ["con_agent", "referee", END])
builder.add_conditional_edges("con_agent", whose_turn, ["pro_agent", "referee", END])
builder.add_edge("referee", END)

GRAPH = builder.compile()

# pro_agent -> con_agent -> pro_agent -> ... is a LOOP. A plain graph could
# never do that; conditional edges are what allow a node to be visited again.


# ============================================================
#  6. RUN IT
# ============================================================

if __name__ == "__main__":
    LIVE = live_transcript.Transcript(TOPIC)

    print("=" * 60)
    print("TOPIC:", TOPIC)
    print("=" * 60)
    print("watch it live ->", os.path.abspath(LIVE.html_path))
    print("(double-click that file now; it refreshes itself every 2 seconds)")

    start_state = {
        "topic": TOPIC,
        "pro_memory": [HumanMessage(f'The topic is: "{TOPIC}". Make your opening argument.')],
        "con_memory": [],
        "transcript": [],
        "pro_verdict": "",
        "con_verdict": "",
        "count": 0,
    }

    # recursion_limit = how many node visits LangGraph allows before it gives up.
    # 20 messages + a referee needs more than the default, so we raise it.
    final = GRAPH.invoke(start_state, config={"recursion_limit": 50})

    agreed_alone = final["count"] < MAX_MESSAGES
    how = ("they talked each other into it"
           if agreed_alone else "the referee broke the tie")
    LIVE.finish(final["pro_verdict"], how)

    print("\n" + "=" * 60)
    print(f'CONSENSUS after {final["count"]} messages: {final["pro_verdict"]}  ({how})')
    print("=" * 60)
    print(f'PRO memory: {len(final["pro_memory"])} messages   '
          f'CON memory: {len(final["con_memory"])} messages')
    print("Two separate memories -- neither agent ever read the other's list.")
    print("\nsaved:")
    print(" ", LIVE.md_path)
    print(" ", LIVE.json_path)
    print(" ", LIVE.html_path)
