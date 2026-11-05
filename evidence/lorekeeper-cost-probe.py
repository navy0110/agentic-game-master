import json
import re
from datetime import datetime, timezone
from uuid import uuid4
from uagents import Agent, Context, Protocol
from uagents_core.contrib.protocols.chat import ChatMessage, ChatAcknowledgement, TextContent, chat_protocol_spec

agent = Agent()
protocol = Protocol(spec=chat_protocol_spec)
GM = 'agent1qtxm6c6nwrshe40222wu3r7d6hy52h9flkqmhm39v4a6utulgf6qup7dkm5'
STEPS = [('before', '/status'), ('review1', '/review Rules: Every spell permanently consumes one memory of its caster. Draft: A mage casts three spells. No memory was lost, and there was no exception to the rule. Identify the contradiction and suggest a correction without choosing which memory is lost.'), ('review2', '/review Rules: Every spell permanently consumes one memory of its caster. Draft: A mage casts three spells. No memory was lost, and there was no exception to the rule. Identify the contradiction and suggest a correction without choosing which memory is lost.'), ('review3', '/review Rules: Every spell permanently consumes one memory of its caster. Draft: A mage casts three spells. No memory was lost, and there was no exception to the rule. Identify the contradiction and suggest a correction without choosing which memory is lost.'), ('after', '/status')]


async def send_step(ctx, phase):
    label, text = STEPS[phase]
    ctx.storage.set('phase', phase)
    ctx.logger.info('PROBE sending=' + label)
    status = await ctx.send(GM, ChatMessage(content=[TextContent(type='text', text=text)]))
    ctx.logger.info('PROBE dispatched=' + label + '; status=' + str(status))


@protocol.on_message(ChatMessage)
async def unexpected(ctx: Context, sender: str, msg: ChatMessage):
    await ctx.send(sender, ChatAcknowledgement(acknowledged_msg_id=msg.msg_id))
    if sender != GM or ctx.storage.get('done'):
        return
    phase = ctx.storage.get('phase')
    if not isinstance(phase, int) or phase >= len(STEPS):
        return
    label = STEPS[phase][0]
    answer = '\n'.join(c.text for c in msg.content if isinstance(c, TextContent))
    results = ctx.storage.get('results-v3') or {}
    results[label] = answer
    ctx.storage.set('results-v3', results)
    ctx.logger.info('PROBE result=' + label + '; text=' + answer)
    if phase + 1 < len(STEPS):
        await send_step(ctx, phase + 1)
        return
    checks = {f'review{i}_detected_conflict': '## Lorekeeper review' in results[f'review{i}'] and 'Suggested change:' in results[f'review{i}'] for i in range(1,4)}
    for i in range(1,4):
        suggestions = [line.lower() for line in results[f'review{i}'].splitlines() if 'Suggested change:' in line]
        checks[f'review{i}_preserves_cost'] = bool(suggestions) and any(re.search(r'three memories (?:in )?total|total (?:cost )?of three memories|one memory per spell|three memories overall|total loss of three memories', line) for line in suggestions) and not any(re.search(r'each.{0,55}(?:three|3) (?:distinct )?memories', line) for line in suggestions)
    checks['review_read_only'] = results['before'] == results['after'] and 'No campaign' in results['after']
    ctx.storage.set('checks', checks)
    ctx.storage.set('done', True)
    ctx.logger.info('PROBE checks=' + json.dumps(checks))


@protocol.on_message(ChatAcknowledgement)
async def ack(ctx: Context, sender: str, msg: ChatAcknowledgement):
    pass


@agent.on_interval(period=8)
async def verify(ctx: Context):
    if ctx.storage.get('started-v8'):
        return
    ctx.storage.set('started-v8', True)
    ctx.storage.set('done', False)
    ctx.storage.set('results-v3', {})
    await send_step(ctx, 0)
    return



agent.include(protocol, publish_manifest=True)
