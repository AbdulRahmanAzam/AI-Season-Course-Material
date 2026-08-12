"""
FILE 2: DISCOVER an agent, then SEND it one message
===================================================
The full A2A client flow, once, slowly:

    1. DISCOVER -- read the agent's card to learn what it does
    2. SEND     -- POST a JSON-RPC "message/send" with our text
    3. READ     -- the agent replies with a TASK, not just a string

That third step is the one people miss. A2A does not hand back a bare answer.
It hands back a Task: a unit of work with an id, a state, a history and
artifacts. This file prints the whole Task so the shape stops being abstract.

The Task went through three states while you waited:

    submitted  ->  working  ->  completed

We also call "tasks/get" afterwards, which is how a client checks on a job it
started earlier -- the same way you would track a long-running task.

RUN:  python 02_one_agent_replies.py
"""

import sys
import json

from debate_agent import make_pro, send_message, task_text, require_key

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

TOPIC = "Toyota is better than every other car brand."

require_key()


if __name__ == "__main__":
    pro = make_pro(TOPIC)

    # 1) DISCOVER ------------------------------------------------------------
    card = pro.get_agent_card()
    print("=" * 60)
    print("1. DISCOVER")
    print(f"   found '{card['name']}'")
    print(f"   it can: {card['skills'][0]['description']}")

    # 2) SEND ----------------------------------------------------------------
    # contextId names the conversation. The agent files its memory under it.
    context_id = "ctx-demo-1"
    print("\n2. SEND  (method: message/send)")
    print("   agent replies: ", end="", flush=True)

    task = send_message(pro, f'The topic is: "{TOPIC}". Make your opening argument.',
                        context_id)
    print()

    # 3) READ ----------------------------------------------------------------
    print("\n3. READ -- what came back is a TASK, not a string:")
    print(json.dumps(task, indent=2, default=str, ensure_ascii=False))

    print("\n" + "=" * 60)
    print(f"task id     : {task['id']}")
    print(f"contextId   : {task['contextId']}")
    print(f"final state : {task['status']['state']}   (it went submitted -> working -> completed)")
    print(f"artifacts   : {len(task['artifacts'])}  ->  '{task['artifacts'][0]['name']}'")
    print(f"the answer  : {task_text(task)[:70]}...")

    # BONUS: tasks/get -- check on a task you started earlier -----------------
    print("\n" + "=" * 60)
    print("4. tasks/get -- ask the agent about that task again by id")
    rpc = {"jsonrpc": "2.0", "id": 2, "method": "tasks/get",
           "params": {"id": task["id"]}}
    again = pro.handle_rpc(rpc)
    print(f"   state is still: {again['result']['status']['state']}")

    # and an unknown method gets a proper JSON-RPC error
    bad = pro.handle_rpc({"jsonrpc": "2.0", "id": 3, "method": "make/coffee", "params": {}})
    print(f"   unknown method -> {bad['error']['code']}: {bad['error']['message']}")

    print("\nOne agent answered once. Next: two of them, arguing.")
    print("Next:  python 03_two_agents_talk.py")
