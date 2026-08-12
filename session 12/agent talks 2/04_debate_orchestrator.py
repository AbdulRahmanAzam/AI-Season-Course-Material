"""
FILE 4: The ORCHESTRATOR -- LangGraph drives, A2A carries
=========================================================
FILE 3 relayed 4 messages with a for loop. That works, but the rules of the
conversation ended up scattered through the loop body. Here LangGraph holds
the rules and A2A carries the words:

        START ---> pro_turn ---.
                                >--- whose_turn? ---> pro_turn
                   con_turn ---'                     con_turn
                                                     referee
                                                     END
                   referee ---> END

    LangGraph  = the conductor. Whose turn is it, are we done, who breaks a tie.
    A2A        = the wire. Every arrow above is a JSON-RPC message/send.

Say this out loud in class: THE GRAPH DOES NOT HOLD THE MEMORY. Look at
DebateState below -- there is no message history in it. Each agent keeps its
own history inside itself, filed under this debate's contextId. The graph only
tracks whose turn it is and what each side currently believes.

The debate always ends with both agents on the SAME answer:
  - if they agree on their own, the graph stops early
  - after 20 messages a third agent, the REFEREE, is discovered and hired

While it runs it writes transcripts/debate_<topic>.md / .json / .html.
Double-click the .html BEFORE it finishes -- it refreshes itself every 2
seconds, so the class watches the chat fill up in a browser.

RUN:  python 04_debate_orchestrator.py
      python 04_debate_orchestrator.py "Python is better than JavaScript"
"""

import os
import sys
import time
import operator
from typing import Annotated
from typing_extensions import TypedDict

from langgraph.graph import StateGraph, START, END

from debate_agent import (make_pro, make_con, make_referee, send_message,
                          task_text, read_verdict, require_key, MAX_MESSAGES)
import live_transcript

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

TOPIC = "Ronaldo is better than Messi"
if len(sys.argv) > 1:
    TOPIC = " ".join(sys.argv[1:])

require_key()

# the three agents. Nothing is shared between them but the messages we relay.
PRO = make_pro(TOPIC)
CON = make_con(TOPIC)
REFEREE = make_referee(TOPIC)

CONTEXT_ID = "ctx-debate-1"       # one id for the whole debate
LIVE = None                       # transcript writer, created in __main__


# ============================================================
#  1. STATE -- notice what is NOT here: any message history
# ============================================================

class DebateState(TypedDict):
    topic: str
    last_text: str                              # what the next agent will hear
    transcript: Annotated[list, operator.add]   # public log, for the files
    pro_verdict: str                            # "YES" / "NO" / ""
    con_verdict: str
    count: int                                  # messages spoken so far


# ============================================================
#  2. NODES -- each one is a single A2A call
# ============================================================

def relay(state, label):
    """Send whatever was last said to one agent, and keep what it says back."""
    agent = PRO if label == "PRO" else CON

    print(f"\n[{state['count'] + 1}] {label}: ", end="", flush=True)
    task = send_message(agent, state["last_text"], CONTEXT_ID, state["count"])
    print()
    print(f"      [a2a] {task['id']} -> {task['status']['state']}", flush=True)

    reply = task_text(task)                     # the answer lives in the artifact
    verdict = read_verdict(reply, state[f"{label.lower()}_verdict"])
    LIVE.add(label, reply, verdict)             # .md + .json + .html, right now
    time.sleep(1)                               # paces the chat, eases the free tier

    return {
        # THE WHOLE TRICK: this agent's answer is the next agent's question
        "last_text": f"{label} said: {reply}",
        "transcript": [{"n": state["count"] + 1, "who": label,
                        "text": reply, "verdict": verdict}],
        f"{label.lower()}_verdict": verdict,
        "count": state["count"] + 1,
    }


def pro_turn(state):
    return relay(state, "PRO")


def con_turn(state):
    return relay(state, "CON")


def referee_turn(state):
    """Out of time and still no agreement -- so we hire a third agent.
    Discovery, message/send, Task: exactly the same flow as the debaters."""
    card = REFEREE.get_agent_card()
    print(f"\n[referee] no agreement in {MAX_MESSAGES} messages")
    print(f"[referee] discovered '{card['name']}' skill={card['skills'][0]['id']}")
    print("[referee] deciding: ", end="", flush=True)

    debate = "\n".join(f"{m['who']}: {m['text']}" for m in state["transcript"])
    task = send_message(REFEREE, f'Claim: "{state["topic"]}"\n\n{debate}',
                        "ctx-referee-1")
    print()

    reply = task_text(task)
    verdict = read_verdict(reply, "NO")
    LIVE.add("REFEREE", reply, verdict)

    # both debaters adopt the referee's answer, so the run always ends agreed
    return {"pro_verdict": verdict, "con_verdict": verdict,
            "transcript": [{"n": state["count"] + 1, "who": "REFEREE",
                            "text": reply, "verdict": verdict}]}


# ============================================================
#  3. THE CONDITIONAL EDGE -- where do we go after a turn?
# ============================================================

def whose_turn(state):
    """Runs after every turn and returns the NAME of the next node."""
    if state["pro_verdict"] and state["pro_verdict"] == state["con_verdict"]:
        return END                                  # they agreed -> stop early
    if state["count"] >= MAX_MESSAGES:
        return "referee"                            # out of time -> break the tie
    return "con_turn" if state["count"] % 2 == 1 else "pro_turn"


# ============================================================
#  4. BUILD THE GRAPH
# ============================================================

builder = StateGraph(DebateState)
builder.add_node("pro_turn", pro_turn)
builder.add_node("con_turn", con_turn)
builder.add_node("referee", referee_turn)

builder.add_edge(START, "pro_turn")                 # PRO always opens
builder.add_conditional_edges("pro_turn", whose_turn, ["con_turn", "referee", END])
builder.add_conditional_edges("con_turn", whose_turn, ["pro_turn", "referee", END])
builder.add_edge("referee", END)

GRAPH = builder.compile()

# pro_turn -> con_turn -> pro_turn -> ... is a LOOP. Conditional edges are the
# only reason a node can be visited more than once.


# ============================================================
#  5. RUN IT
# ============================================================

if __name__ == "__main__":
    LIVE = live_transcript.Transcript(TOPIC)

    print("=" * 60)
    print("TOPIC:", TOPIC)
    print("=" * 60)
    print("discovering agents...")
    for agent in (PRO, CON):
        card = agent.get_agent_card()
        print(f"  found '{card['name']}'  skill={card['skills'][0]['id']}  {card['url']}")
    print(f"contextId: {CONTEXT_ID}")
    print("\nwatch it live ->", os.path.abspath(LIVE.html_path))
    print("(double-click that file now; it refreshes itself every 2 seconds)")

    start_state = {
        "topic": TOPIC,
        "last_text": f'The topic is: "{TOPIC}". Make your opening argument.',
        "transcript": [],
        "pro_verdict": "",
        "con_verdict": "",
        "count": 0,
    }

    # recursion_limit = how many node visits LangGraph allows before giving up.
    final = GRAPH.invoke(start_state, config={"recursion_limit": 50})

    agreed_alone = final["count"] < MAX_MESSAGES
    how = "they talked each other into it" if agreed_alone else "the referee broke the tie"
    LIVE.finish(final["pro_verdict"], how)

    print("\n" + "=" * 60)
    print(f'CONSENSUS after {final["count"]} messages: {final["pro_verdict"]}  ({how})')
    print("=" * 60)

    # proof the memories were never shared
    for agent in (PRO, CON):
        name = agent.get_agent_card()["name"]
        own = len(agent.memory.get(CONTEXT_ID, []))
        print(f"{name}: {own} messages in its own memory, {len(agent.tasks)} tasks handled")
    print("Neither agent could read the other's memory. They only ever received text.")

    print("\nsaved:")
    print(" ", LIVE.md_path)
    print(" ", LIVE.json_path)
    print(" ", LIVE.html_path)
