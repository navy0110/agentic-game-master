# Agentverse Hosted Agent

`agent.py` is a generated single-file build for the Agentverse Build editor.
It includes the local engine's prompt, validators, canon corrections, command
normalization and state transitions. Regenerate with `python hosted/build.py`
after editing the local engine; do not manually change generated story logic.

## Deployment

1. In Agentverse Agents, select Launch an Agent → Generate Agent / Hosted Agent.
2. Name it Agentic Game Master. Open Build and replace the main agent.py with
   this folder's agent.py. This is NOT the repository root's local agent.py.
3. Save/compile and start the hosted agent; review Agent Logs.
4. Use the new profile's Chat with Agent link to test /help, /status, a world
   brief and a continuation. Stop/restart it and verify /status still works.

The hosted platform supplies its own identity. This agent will have a new address;
the external mailbox agent cannot be converted just by changing its seed in code.
No local AGENT_SEED or .env file should be pasted into Hosted Agent source.
Agentverse docs state it injects ASI1_API_KEY and ASI1_BASE_URL and meters model
usage against your account quota. Confirm available compute/storage/model quotas
in your dashboard; do not assume unlimited or paid resources have been enabled.

## Persistence

Campaigns are stored with `ctx.storage.get/set`, scoped by sender AND protocol
session. One write stores state plus duplicate reply cache. No globals are used
as campaign storage. /status shows only turn and counts, hiding even untagged
story spoilers. /gm-status and /export include the full record and secrets.
These are display modes for the campaign owner, NOT separate authenticated GM
and player roles. All four commands avoid model calls. Do not share /gm-status
or exports with players who should not see secrets.

This adapter deliberately uses synchronous model requests inside each handler,
with no await between reading and saving state. Actual hosted invocation ordering
and storage write durability must still be tested on the platform. Local tests
use fake persistent storage and cannot prove platform concurrency semantics.

Maximum record size is 200 KB per campaign (including reply history). On reaching
the cap, export and begin a new chapter. Overall Agentverse quotas also apply.

## Existing campaign

The old local campaign is untouched. A new hosted identity/conversation has a new
sender/session scope, so automatic migration is not yet implemented. Keep the local
backup and export. Start a separate demonstration campaign for the first hosted
test; don't claim history was migrated until its storage mapping is verified.

## Status

Deployed 2026-11-03 to Agentverse Hosted Agents:
`agent1qtxm6c6nwrshe40222wu3r7d6hy52h9flkqmhm39v4a6utulgf6qup7dkm5`.
AVCTL confirms compiled=true, running=true; logs confirm successful startup and
Almanac fast-track registration. Real ASI:One inference, persistent storage across
hosted invocations/restarts and account model quota remain to be verified.

## Official references

- https://docs.agentverse.ai/documentation/create-agents/hosted-code-editor
- https://docs.agentverse.ai/documentation/getting-started/enable-chat-protocol
- https://docs.agentverse.ai/v-2/documentation/advanced-usages/allowed-imports
- https://docs.agentverse.ai/documentation/advanced-usages/agentverse-cli

## Separate reviewer (November 5)

The hosted runtime now supports `/review [notes]`, which delegates to the separately deployed AGM Lorekeeper. This is read-only, may include GM secrets, and has an explicit unavailable fallback. Normal generation runs in a worker thread with per-campaign asynchronous locking; the earlier synchronous-handler paragraph above describes the initial version. See [LOREKEEPER.md](../LOREKEEPER.md) for actual deployed addresses, protocol, limits, and live evidence.
