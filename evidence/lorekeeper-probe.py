import json
from datetime import datetime, timezone
from uuid import uuid4
from uagents import Agent, Context, Protocol
from uagents_core.contrib.protocols.chat import ChatMessage, ChatAcknowledgement, TextContent, chat_protocol_spec

agent = Agent()
protocol = Protocol(spec=chat_protocol_spec)
GM = 'agent1qtxm6c6nwrshe40222wu3r7d6hy52h9flkqmhm39v4a6utulgf6qup7dkm5'
STEPS = [
    ('standalone_review', '/review Rules: Every spell permanently consumes one memory. Draft: A mage casts three spells. No memory was lost, and there was no exception to the rule.'),
    ('help', '/help'),
    ('npc', 'I need an NPC for my harbor campaign: a port official who secretly reports to a rival trade house. Give me her motives, her secret, and three lines of dialogue.'),
    ('before', '/status'),
    ('review', '/review Additional example to check: Rules: Every spell permanently consumes one memory. Draft: A mage casts three spells. No memory was lost, and there was no exception to the rule. Suggest a correction without choosing which memory is lost.'),
    ('after', '/status'),
    ('continuation', 'The players ask the harbor official about inspection fees, but accept no deal and make no promise. Continue the scene without committing the players.'),
    ('end', '/status'),
]


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
    checks = {
        'help_has_review': '/review' in results['help'],
        'npc_has_actual_content': 'Motives' in results['npc'] and 'Secret' in results['npc'] and '3.' in results['npc'],
        'review_received': '## Lorekeeper review' in results['review'],
        'standalone_detects_conflict': 'Suggested change:' in results['standalone_review'],
        'review_read_only': results['before'] == results['after'] and 'turn 1' in results['before'],
        'normal_generation_after_review': 'turn 2' in results['end'],
    }
    ctx.storage.set('checks', checks)
    ctx.storage.set('done', True)
    ctx.logger.info('PROBE checks=' + json.dumps(checks))


@protocol.on_message(ChatAcknowledgement)
async def ack(ctx: Context, sender: str, msg: ChatAcknowledgement):
    pass


@agent.on_interval(period=8)
async def verify(ctx: Context):
    if ctx.storage.get('started-v6'):
        return
    ctx.storage.set('started-v6', True)
    ctx.storage.set('done', False)
    ctx.storage.set('results-v3', {})
    await send_step(ctx, 0)
    return



agent.include(protocol, publish_manifest=True)
