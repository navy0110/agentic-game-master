"""Agentverse adapter. Run only after configuring API key and private agent seed."""
import asyncio
import os
from datetime import datetime, timezone
from uuid import uuid4
from dotenv import load_dotenv
from uagents import Agent, Context, Protocol
from uagents_core.contrib.protocols.chat import (
    ChatAcknowledgement, ChatMessage, TextContent, chat_protocol_spec,
)
from agm.engine import Engine

load_dotenv()
if not os.getenv("AGENT_SEED") or not os.getenv("ASI_ONE_API_KEY"):
    raise RuntimeError("Configure AGENT_SEED and ASI_ONE_API_KEY in your local .env.")
engine = Engine()
agent = Agent(name="Agentic Game Master", seed=os.environ["AGENT_SEED"],
              port=int(os.getenv("AGENT_PORT", "8001")), mailbox=True,
              publish_agent_details=True)
protocol = Protocol(spec=chat_protocol_spec)


@protocol.on_message(ChatMessage)
async def handle_message(ctx: Context, sender: str, msg: ChatMessage):
    await ctx.send(sender, ChatAcknowledgement(timestamp=datetime.now(timezone.utc),
                                              acknowledged_msg_id=msg.msg_id))
    text = "\n".join(item.text for item in msg.content if isinstance(item, TextContent)).strip()
    session = str(ctx.session)
    try:
        if not text:
            reply = "Describe your world, its rules, and the adventure you want to run."
        elif text.lower() == "/export":
            import json
            state = await asyncio.to_thread(engine.get, sender, session)
            reply = json.dumps(state, ensure_ascii=False, indent=2) if state else "No campaign in this session yet."
        else:
            result = await asyncio.to_thread(engine.turn, sender, session, text)
            reply = result["adventure"] + "\n\nConsequences: " + "; ".join(result["changes"])
    except Exception:
        ctx.logger.error("Campaign request failed; check model availability and local configuration.")
        reply = "I could not complete that turn. Your previous campaign state is unchanged. Please retry."
    await ctx.send(sender, ChatMessage(timestamp=datetime.now(timezone.utc),
                                     msg_id=uuid4(), content=[TextContent(type="text", text=reply)]))


@protocol.on_message(ChatAcknowledgement)
async def handle_ack(ctx: Context, sender: str, msg: ChatAcknowledgement):
    pass


agent.include(protocol, publish_manifest=True)
if __name__ == "__main__":
    agent.run()
