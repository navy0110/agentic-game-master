# Agentic Game Master

**Your world. Your players' choices. The next playable scene.**

Agentic Game Master helps tabletop GMs and game developers prepare short adventures
and continue them from player decisions. Bring your world's lore, rules, characters
and current situation. Get a playable quest, an NPC with motives and dialogue, and
a dynamic event with meaningful consequences.

## What you can do

- Generate a system-neutral adventure with objectives, rewards and success/failure conditions.
- Create NPCs and events connected to your existing world.
- Continue a campaign from choices you explicitly supply.
- Keep recorded facts, unresolved hooks and GM corrections between messages in the same session.
- Read a spoiler-safe status summary, inspect the full GM record, or export the campaign.

## Try it in two minutes

In a new conversation with this agent, send:

> Create a 10-minute adventure for two novice heroes in a coastal town. Magic
> permanently consumes a memory. An archivist needs help locating a missing bell.
> Include one quest, an NPC and a dynamic event. No player has accepted any offer yet.

Then continue in the same conversation:

> The players ask the archivist for terms but accept no bargain and make no promise.
> Describe the NPC's response and leave the decision open.

Use `/status` to check the saved turn without exposing story details. A new story
request may take about a minute; command replies do not call the model.

## Commands

| Command | Result |
|---|---|
| `/help` | Instructions and commands |
| `/status` | Spoiler-safe turn and record counts |
| `/gm-status` | Full facts and open threads, **including secrets** |
| `/export` | Full campaign JSON, **including secrets** |

## Who it is for

Tabletop game masters preparing one-shots, indie RPG developers prototyping quest
content, and worldbuilders testing how a story responds to player choices.

## Limits and data

- This is a session-preparation assistant. It does not control a live game engine,
  move characters, grant items, or modify Memeria or another game.
- Review generated rules, balance and continuity. Model output can contain mistakes;
  explicitly state corrections when needed.
- Commands are display modes for the campaign owner, not separate authenticated
  GM/player roles. Don't share the full GM record or exports with players who
  should not see the secrets. Free-form story responses may include GM-only content.
- Campaigns are scoped to sender and protocol session. Start a new conversation for
  a separate campaign; cross-session import and sharing are not implemented.
- Hosted campaign records and reply history have a 200 KB application cap, plus
  Agentverse account quotas. Export before starting a new chapter.
- World briefs, player decisions and campaign context are processed by the ASI
  model and stored in Agentverse. Use fictional data you are authorized to share.

## Implementation

Runs as an Agentverse Hosted Agent using Fetch.ai's Agent Chat Protocol and ASI
inference. Hosting is independent of the developer's computer. The local mailbox
prototype remains separate; its campaign history has not been migrated here.

Source and setup: https://github.com/navy0110/agentic-game-master

Version: early prototype, November 2026.
