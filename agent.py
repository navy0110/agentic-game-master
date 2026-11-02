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
from agm.engine import Engine, render_status, normalize_message

load_dotenv()
if not os.getenv("AGENT_SEED") or not os.getenv("ASI_ONE_API_KEY"):
    raise RuntimeError("Configure AGENT_SEED and ASI_ONE_API_KEY in your local .env.")
engine = Engine()
generation_slots = asyncio.Semaphore(4)
agent = Agent(name="Agentic Game Master", seed=os.environ["AGENT_SEED"],
              port=int(os.getenv("AGENT_PORT", "8001")), mailbox=True,
              publish_agent_details=True, handle_messages_concurrently=True)
protocol = Protocol(spec=chat_protocol_spec)


@protocol.on_message(ChatMessage)
async def handle_message(ctx: Context, sender: str, msg: ChatMessage):
    await ctx.send(sender, ChatAcknowledgement(timestamp=datetime.now(timezone.utc),
                                              acknowledged_msg_id=msg.msg_id))
    text = "\n".join(item.text for item in msg.content if isinstance(item, TextContent)).strip()
    text = normalize_message(text, agent.address)
    session = str(ctx.session)
    try:
        if not text:
            reply = "Describe your world, its rules, and the adventure you want to run."
        elif text.lower() == "/help":
            reply = ("Agentic Game Master\nDescribe your world, rules and desired adventure to start. "
                     "Continue with player decisions in this conversation.\n"
                     "/status — read saved facts and open threads without advancing the story\n"
                     "/export — export this campaign as JSON\n"
                     "/help — show these commands\n"
                     "For a correction, explicitly state what was wrong and the correct fact. "
                     "A new protocol session starts a separate campaign.")
        elif text.lower() == "/status":
            state = await asyncio.to_thread(engine.get, sender, session)
            reply = render_status(state)
            ctx.logger.info("Read-only /status served; saved turn=%s; no model call", state["turn"] if state else 0)
        elif text.lower().startswith("/") and text.lower() != "/export":
            reply = "Unknown command. Send /help to see available commands. Your campaign is unchanged."
        elif text.lower() == "/export":
            import json
            state = await asyncio.to_thread(engine.get, sender, session)
            reply = json.dumps(state, ensure_ascii=False, indent=2) if state else "No campaign in this session yet."
        else:
            async with generation_slots:
                result = await asyncio.to_thread(engine.turn, sender, session, text, str(msg.msg_id))
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
