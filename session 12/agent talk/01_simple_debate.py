"""
FILE 1: Two agents arguing -- built BY HAND
===========================================
Two LLM agents get opposite orders about the same claim:

    PRO  must argue the claim is TRUE
    CON  must argue the claim is FALSE

They take turns. Each one reads what the other just said before replying,
and each one keeps its OWN memory -- there is no shared brain anywhere.

The trick that makes this work is one line, and it is the whole lesson:

    PRO's reply goes into PRO's memory as an AIMessage   ("something I said")
    the SAME reply goes into CON's memory as a HumanMessage ("someone said this to me")

Swap the names and you get CON's side. That is all a conversation between two
agents is: my output is your input, with the label changed.

Everything here is plain Python -- a while loop and an if/else. FILE 2 does
exactly the same debate, but lets LangGraph run the loop instead of us.

RUN:  python 01_simple_debate.py
      python 01_simple_debate.py "Python is better than JavaScript"
"""

import os
import sys
import time
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

load_dotenv()

MODEL = "openai/gpt-oss-120b"     # Groq's id for GPT-OSS 120B
MAX_MESSAGES = 20                 # 10 turns each, then we stop no matter what
TOPIC = "Toyota is better than every other car brand."

if len(sys.argv) > 1:             # let the teacher pass a different topic
    TOPIC = " ".join(sys.argv[1:])

if not os.getenv("GROQ_API_KEY", "").strip():
    print("Add GROQ_API_KEY to .env  ->  https://console.groq.com/keys")
    sys.exit(1)

# temperature 0.7 so the two agents do not sound like the same person.
# reasoning_effort 'low' because GPT-OSS is a reasoning model -- 'low' means
# think briefly and answer fast, which is what we want in a live debate.
LLM = ChatGroq(model=MODEL, temperature=0.7, max_tokens=600, reasoning_effort="low")


# ---------- THE TWO PERSONALITIES ----------

def persona(who, topic, count):
    """The system prompt for one agent. Rebuilt every turn, because the
    PHASE line at the bottom changes as the debate runs out of time."""
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


# ---------- THE DEBATE LOOP (this is what FILE 2 replaces with a graph) ----------

if __name__ == "__main__":
    print("=" * 60)
    print("TOPIC:", TOPIC)
    print("=" * 60)

    # each agent's own private memory -- two separate lists, never merged
    pro_memory = [HumanMessage(f'The topic is: "{TOPIC}". Make your opening argument.')]
    con_memory = []

    pro_verdict, con_verdict = "", ""
    count = 0

    while count < MAX_MESSAGES:
        who = "PRO" if count % 2 == 0 else "CON"
        memory = pro_memory if who == "PRO" else con_memory

        # 1) build THIS agent's context: its own persona + its own memory
        messages = [SystemMessage(persona(who, TOPIC, count))] + memory

        # 2) stream the answer so the class watches it appear word by word
        print(f"\n[{count + 1}] {who}: ", end="", flush=True)
        text = ""
        for chunk in LLM.stream(messages):
            print(chunk.content, end="", flush=True)
            text += chunk.content
        print()

        # 3) the same reply lands in BOTH memories -- with different labels
        pro_memory.append(AIMessage(text) if who == "PRO" else HumanMessage(f"{who}: {text}"))
        con_memory.append(AIMessage(text) if who == "CON" else HumanMessage(f"{who}: {text}"))

        # 4) record who now believes what
        if who == "PRO":
            pro_verdict = read_verdict(text, pro_verdict)
        else:
            con_verdict = read_verdict(text, con_verdict)

        count += 1

        # 5) stop early if they have landed on the same answer
        if pro_verdict and pro_verdict == con_verdict:
            print("\n" + "=" * 60)
            print(f"THEY AGREE after {count} messages -> {pro_verdict}")
            print("=" * 60)
            break

        time.sleep(1)   # paces the chat, and is kind to the free Groq tier
    else:
        print("\n" + "=" * 60)
        print(f"{MAX_MESSAGES} messages used and they still disagree "
              f"(PRO says {pro_verdict}, CON says {con_verdict}).")
        print("FILE 2 fixes this with a referee.")
        print("=" * 60)

    print(f"\nPRO remembers {len(pro_memory)} messages, CON remembers {len(con_memory)}.")
    print("Two separate memories -- neither agent can read the other's list.")
