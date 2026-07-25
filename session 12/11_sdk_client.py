"""
FILE 11: Talking to an A2A agent with the OFFICIAL SDK client
=============================================================
Compare this with File 03 (our by-hand client). Same three ideas — DISCOVER,
SEND, READ — but now the SDK handles the JSON-RPC wiring, the transport choice,
and (if you ask for it) streaming.

Tested with a2a-sdk 1.1.1.

RUN:
    Terminal 1:  python 10_sdk_agent.py
    Terminal 2:  python 11_sdk_client.py
"""

import asyncio
import httpx

from a2a.client import ClientFactory, ClientConfig
from a2a.types import SendMessageRequest, Message, Part, Role
from a2a.utils import TransportProtocol
from a2a.helpers import get_message_text     # pulls the text out of a Message for us


async def main():
    async with httpx.AsyncClient() as http_client:
        # 1) DISCOVER + build a client.
        #    create_from_url() fetches the agent card from
        #    /.well-known/agent-card.json and sets up the matching transport.
        config = ClientConfig(
            httpx_client=http_client,
            streaming=False,                                  # we want one final answer
            supported_protocol_bindings=[TransportProtocol.JSONRPC],
        )
        client = await ClientFactory(config).create_from_url("http://localhost:9999")

        # 2) SEND a message. Notice the TYPED objects instead of raw dicts —
        #    this is the same "role/parts/messageId" shape from File 03.
        request = SendMessageRequest(
            message=Message(
                role=Role.ROLE_USER,
                parts=[Part(text="Sara")],
                message_id="msg-1",
            )
        )

        # 3) READ the reply. send_message() streams events back; a simple agent
        #    sends just one, carrying the reply Message.
        print("Sending 'Sara' to the SDK agent...")
        async for event in client.send_message(request):
            if event.HasField("message"):
                print("Agent replied:", get_message_text(event.message))

        await client.close()


if __name__ == "__main__":
    asyncio.run(main())
