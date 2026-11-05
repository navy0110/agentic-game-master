# Agentic Game Master

**Your world. Your players' choices. The next playable scene.**

Agentic Game Master helps tabletop GMs and game developers prepare short adventures
and continue them from player decisions. Bring your world's lore, rules, characters
and current situation. Get a playable quest, an NPC with motives and dialogue, and
a dynamic event with meaningful consequences.

## Key features

- Generate a system-neutral adventure with objectives, rewards and success/failure conditions.
- Create NPCs and events connected to your existing world.
- Continue a campaign from choices you explicitly supply.
- Keep recorded facts, unresolved hooks and GM corrections between messages in the same session.
- Read a spoiler-safe status summary, inspect the full GM record, or export the campaign.

## Try it in two minutes

Visit our [website](https://agentic-game-master.atom139139.workers.dev/) for
starting prompts and a short demo, then open the agent in ASI:One.

In ASI:One, **select @agenticgamemaster as the recipient for every message**.
Messages without a mention may go to your personal AI instead. First send
`@agenticgamemaster /help` to confirm that Agentic Game Master answers.

The agent turns your brief into text you can use at the table: a quest, an NPC
or an event. It records facts and open threads so you can send a player choice
and continue in the same conversation. You remain the GM and choose what to use.
You can request a single NPC without creating a campaign first.

In a new conversation with this agent selected, send:

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
| `/review [notes]` | Read-only consistency review by the separate Lorekeeper agent; **may include secrets** |

### Optional second-agent review

After generating an NPC or scene, send `/review` in the same conversation.
AGM sends the saved draft, canon, open threads and optional review notes to the
separate **AGM Lorekeeper** agent. It returns supported issues, exact source
quotes and suggested changes, or reports that no supported conflict was found.
The GM decides what to apply; the review never advances the story or edits canon.
If the reviewer is unavailable or its answer fails validation, AGM says so and
leaves your campaign unchanged. A review is advice, not a correctness guarantee.

## Use cases

- Tabletop GMs: prepare a one-shot with a quest, NPC and event tied to your lore.
- Indie RPG developers: prototype quest content and possible consequences.
- Worldbuilders: explore how a scene responds to explicit player choices.

## Limitations

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

## Metadata

| Field | Value |
|---|---|
| Agent handle | `@agenticgamemaster` |
| Category | Tabletop RPGs, storytelling and session preparation |
| Hosting | Agentverse Hosted Agent |
| Protocol | Fetch.ai Agent Chat Protocol |
| Inference | ASI |
| Version | Early prototype, November 2026 |
| Source | https://github.com/navy0110/agentic-game-master |

## Implementation

Runs as an Agentverse Hosted Agent using Fetch.ai's Agent Chat Protocol and ASI
inference. Hosting is independent of the developer's computer. The local mailbox
prototype remains separate; its campaign history has not been migrated here.

Source and setup: https://github.com/navy0110/agentic-game-master

Version: early prototype, November 2026.
