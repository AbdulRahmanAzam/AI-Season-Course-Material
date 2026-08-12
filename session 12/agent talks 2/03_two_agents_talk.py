"""
FILE 3: The A2A COMMUNICATION FLOW -- one agent's answer is the other's question
===============================================================================
Now put two agents in a room. Neither one knows the other exists. Something in
the middle -- an orchestrator -- discovers both and passes messages across:

    discover both cards
        |
        v
    message/send  -> PRO   -> Task(completed) -> PRO's argument
        |
        '-- that same text becomes the message we send to CON
        |
        v
    message/send  -> CON   -> Task(completed) -> CON's rebuttal
        |
        '-- and that goes back to PRO ... and around again

Two things to say out loud in class:

  1. ONE contextId is used for the whole debate. Each agent files its own
     memory under that id, so each one remembers its own side of the
     conversation and NEITHER can read the other's list.

  2. Nothing is shared except the text. No shared variable, no shared object.
     If these two agents were on different servers in different countries,
     this exact code would still work -- only the transport would change.

This file relays 4 messages by hand so you can watch the flow. FILE 4 hands
the same loop to LangGraph and runs the whole 20-message debate.

RUN:  python 03_two_agents_talk.py
"""

import sys

from debate_agent import (make_pro, make_con, send_message, task_text,
                          read_verdict, require_key)

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

TOPIC = "Toyota is better than every other car brand."
ROUNDS = 4                       # just enough to see the flow

require_key()


if __name__ == "__main__":
    # ---- DISCOVERY: the orchestrator learns who is in the room -------------
    agents = [make_pro(TOPIC), make_con(TOPIC)]

    print("=" * 60)
    print("TOPIC:", TOPIC)
    print("=" * 60)
    print("discovering agents...")
    for agent in agents:
        card = agent.get_agent_card()
        print(f"  found '{card['name']}'  skill={card['skills'][0]['id']}")

    # ---- ONE contextId for the whole debate -------------------------------
    context_id = "ctx-debate-1"
    print(f"\ncontextId for this debate: {context_id}")
    print("(each agent will file its own memory under that id)\n")

    # the first thing PRO hears
    text = f'The topic is: "{TOPIC}". Make your opening argument.'
    verdicts = {"PRO": "", "CON": ""}

    for count in range(ROUNDS):
        speaker = agents[count % 2]                     # PRO, CON, PRO, CON...
        label = "PRO" if count % 2 == 0 else "CON"

        print(f"[{count + 1}] {label}: ", end="", flush=True)

        # send whatever the OTHER agent just said
        task = send_message(speaker, text, context_id, count)
        print()

        reply = task_text(task)
        verdicts[label] = read_verdict(reply, verdicts[label])
        print(f"      task {task['id']} -> {task['status']['state']}"
              f"   verdict now: {verdicts[label]}\n")

        # THE WHOLE TRICK: this answer is the next agent's question
        text = f"{label} said: {reply}"

    # ---- proof that the memories really are separate ----------------------
    print("=" * 60)
    for agent in agents:
        name = agent.get_agent_card()["name"]
        print(f"{name}: {len(agent.memory[context_id])} messages in its own memory, "
              f"{len(agent.tasks)} tasks handled")
    print("\nNeither agent can reach into the other's memory dict.")
    print("They only ever saw text that arrived in a message/send.")
    print("\nNext:  python 04_debate_orchestrator.py")
