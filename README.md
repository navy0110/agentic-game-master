# Agentic Game Master

The current hosting target is [Agentverse Hosted Agents](hosted/README.md).
The hosted agent is compiled and running; end-to-end hosted chat tests are pending.
Cloudflare remains an optional, undeployed alternative in [cloudflare/DEPLOY.md](cloudflare/DEPLOY.md).

A world-aware Game Master agent for developers and tabletop GMs. Bring a world
brief, hire the agent to prepare a playable quest, and continue the story from
player decisions. Campaign canon and consequences persist in SQLite.

## Status

Initial implementation: CLI, ASI:One model adapter, campaign storage, JSON export,
and an Agentverse Chat Protocol adapter. Local ASI inference, mailbox message
delivery and continuation were verified. The separate Hosted build is deployed;
its model inference and persistence still require live verification.
No web interface or live game engine integration yet. No Memeria code is included.

## Local setup (PowerShell, Python 3.10+)

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
Copy-Item .env.example .env
```

Set ASI_ONE_API_KEY in .env using the ASI:One developer dashboard.
The MCP OAuth login does not supply this API key. Do not send keys in chat or
commit .env. World briefs and campaign state are sent to ASI:One for inference;
only supply content you are authorized to share. Local state is plaintext SQLite.

```powershell
.\.venv\Scripts\python.exe -m agm.cli start --session harbor --file world-example.txt
.\.venv\Scripts\python.exe -m agm.cli continue --session harbor --text "The players bargain with Iona instead of stealing the crystal."
.\.venv\Scripts\python.exe -m agm.cli show --session harbor
.\.venv\Scripts\python.exe -m agm.cli export --session harbor --output harbor.json
```

Without dependencies or credentials, core tests still run:

```powershell
python -m unittest discover -s tests -v
```

Tests use an explicit fake provider to verify persistence, isolation and rollback.
They do not validate model creativity or prove live Agentverse compatibility.

## Agentverse / ASI:One

1. Set a unique private AGENT_SEED in .env as well as the ASI API key.
2. Run `python agent.py` in the configured virtual environment.
3. Connect the agent's mailbox through the Agentverse inspector and keep the
   process online. Follow current Agentverse onboarding for external agents.
4. Open its profile and test through ASI:One. Start with the example world brief.
5. Send a player decision in the same conversation. `/export` returns its state.
   `/status` reads saved facts and open threads without a model call or story
   advancement. `/help` lists the commands. Unknown commands leave state unchanged.

Storage is scoped by sender address AND protocol session. A new session starts
a new campaign. Cross-device/session campaign sharing is not implemented.
The adapter deliberately does not send EndSessionContent after every turn.
Duplicate story messages are identified by sender, session and message ID; a
successful response is cached atomically with state and replayed on redelivery.
Failed generations can be retried. Reusing an ID with different text is rejected.
Independent campaigns can generate concurrently (up to four in-flight requests
in the adapter). A per-campaign lock preserves turn ordering within one process;
SQLite transactions cover only the final save. An optimistic check rejects stale
writes from another process instead of overwriting newer campaign state. Multiple
worker processes may still incur redundant model calls; run one agent process.
Canon retention is enforced, but semantic contradiction detection is not yet
implemented. GMs should review generated rulings and rewards.

## Hackathon evidence to collect

- New repository and first commit timestamps; independent entry point.
- Agentverse address, public source and a working ASI:One conversation link.
- Three assigned participant trials through ASI:One, with written feedback.
- At least one documented change from that feedback; working public demo.
- Declare Memeria as a pre-existing example world, if used later.

## Official implementation references

- https://docs.asi1.ai/documentation/getting-started/overview
- https://uagents.fetch.ai/docs/examples/asi-1
- https://docs.agentverse.ai/documentation/launch-agents/agentverse-sdk/u-agents

Dependencies use bounded ranges pending a clean live installation and lockfile.
