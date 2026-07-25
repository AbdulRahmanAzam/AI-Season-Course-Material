"""
FILE 10: The SAME agent, but with the OFFICIAL A2A SDK
=======================================================
In Files 02-09 we built A2A BY HAND to prove there is no magic: an Agent Card at
a well-known URL, plus a JSON-RPC "message/send" endpoint. That's it.

Now meet the real tool: the official SDK  ->  pip install a2a-sdk
It does the same job, but also hands you streaming, task tracking, auth, and
push notifications for FREE. The trade-off is more moving parts. That is exactly
why we built it by hand first — so each of these pieces makes sense:

    AgentExecutor   ->  where YOUR logic goes  (our old "if method == message/send")
    EventQueue      ->  you push your reply/updates onto this
    InMemoryTaskStore -> remembers long-running tasks (our by-hand version had none)
    DefaultRequestHandler -> routes incoming A2A calls to your executor
    AgentCard       ->  same idea as before, just a typed object now

(Remember Session 6's "raw HTTP vs the SDK"? Same lesson, new protocol.)

Tested with a2a-sdk 1.1.1.

RUN:
    Terminal 1:  python 10_sdk_agent.py
    Terminal 2:  python 11_sdk_client.py
"""

import uvicorn
from fastapi import FastAPI

# ---- the SDK building blocks ----
from a2a.server.agent_execution import AgentExecutor, RequestContext
from a2a.server.events import EventQueue
from a2a.server.request_handlers import DefaultRequestHandler
from a2a.server.tasks import InMemoryTaskStore
from a2a.server.routes import (
    add_a2a_routes_to_fastapi,
    create_agent_card_routes,
    create_jsonrpc_routes,
)
from a2a.types import AgentCard, AgentInterface, AgentCapabilities, AgentSkill
from a2a.utils import TransportProtocol
from a2a.utils.constants import DEFAULT_RPC_URL      # this is simply "/"
from a2a.helpers import new_text_message             # builds an "agent" Message for us


# 1) YOUR AGENT'S LOGIC lives in an AgentExecutor. ----------------------------
#    Compare with File 02's "if method == 'message/send'" block — same job.
class GreetingExecutor(AgentExecutor):
    async def execute(self, context: RequestContext, event_queue: EventQueue) -> None:
        user_text = context.get_user_input()             # the text the client sent us
        reply = new_text_message(f"Hello, {user_text}! (from the SDK agent)")
        await event_queue.enqueue_event(reply)           # push our answer back out

    async def cancel(self, context: RequestContext, event_queue: EventQueue) -> None:
        # No long-running task here, so there is nothing to cancel.
        raise NotImplementedError("This simple agent has nothing to cancel.")


# 2) THE AGENT CARD — same info as before, now a typed object. ----------------
#    Note: the endpoint URL now lives inside a "supported interface".
AGENT_CARD = AgentCard(
    name="Greeting Agent (SDK)",
    description="Greets a person by name — built with the official a2a-sdk.",
    version="1.0.0",
    capabilities=AgentCapabilities(streaming=True),
    default_input_modes=["text"],
    default_output_modes=["text"],
    skills=[
        AgentSkill(id="greet", name="Greet a person",
                   description="Says a warm hello by name.", tags=["greeting"]),
    ],
    supported_interfaces=[
        AgentInterface(
            url="http://localhost:9999/",
            protocol_binding=TransportProtocol.JSONRPC,   # we speak JSON-RPC (same as by hand)
            protocol_version="1.0",
        )
    ],
)


# 3) WIRE IT UP. The handler routes A2A calls to our executor; the route -------
#    factories turn all of that into normal web routes on a FastAPI app.
request_handler = DefaultRequestHandler(
    agent_executor=GreetingExecutor(),
    task_store=InMemoryTaskStore(),        # tracks tasks (unused by this tiny agent)
    agent_card=AGENT_CARD,
)

app = FastAPI()
add_a2a_routes_to_fastapi(
    app,
    agent_card_routes=create_agent_card_routes(AGENT_CARD),            # serves the card
    jsonrpc_routes=create_jsonrpc_routes(request_handler, rpc_url=DEFAULT_RPC_URL),
)


if __name__ == "__main__":
    print("SDK Greeting Agent running at http://localhost:9999")
    print("  Card: http://localhost:9999/.well-known/agent-card.json")
    uvicorn.run(app, host="127.0.0.1", port=9999)
