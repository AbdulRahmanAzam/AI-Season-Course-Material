"""
FILE 1: The two debaters' AGENT CARDS
=====================================
Session 12 FILE 1 showed one Agent Card for a weather agent. Same idea here,
but now look at what changes and what does NOT change between two agents that
are built to disagree with each other.

Everything is identical -- the version, the input/output modes, the
capabilities -- EXCEPT the name, the url, and the one skill. That is the point
of a card: another agent reads it and knows which one to hire for which job,
without knowing anything about how either one is built inside.

No server, no LLM call. Just two dictionaries.

RUN:  python 01_agent_card.py
"""

import sys
import json

from debate_agent import make_pro, make_con

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

TOPIC = "Toyota is better than every other car brand."


if __name__ == "__main__":
    pro = make_pro(TOPIC)
    con = make_con(TOPIC)

    for agent in (pro, con):
        card = agent.get_agent_card()      # real agent: GET /.well-known/agent-card.json
        print("=" * 60)
        print(json.dumps(card, indent=2))
        print()

    print("=" * 60)
    print("Every card answers 3 questions:\n")
    for agent in (pro, con):
        card = agent.get_agent_card()
        skill = card["skills"][0]
        print(f"  WHO   -> {card['name']}")
        print(f"  WHERE -> {card['url']}")
        print(f"  WHAT  -> {skill['name']}  (id: {skill['id']}, tags: {skill['tags']})")
        print()

    print("Notice: the two cards are the SAME SHAPE. Only name, url and the")
    print("one skill differ. An orchestrator does not need to know these are")
    print("debaters -- it just reads the skills and picks who to send work to.")
    print("\nNext:  python 02_one_agent_replies.py")
