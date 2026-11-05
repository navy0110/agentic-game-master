# Lorekeeper — separate-agent consistency review

Implemented and deployed November 5, 2026. A real hosted round trip was verified;
sponsor acceptance of optional bonus evidence is not claimed.

- AGM: `agent1qtxm6c6nwrshe40222wu3r7d6hy52h9flkqmhm39v4a6utulgf6qup7dkm5`
- Lorekeeper: `agent1q007u0ldq88xpuxv6vweqkf5gqss468rn4363pufmhystwp4tc52wgd67ya`
- Technical probe: `agent1qv6muc5tjh686nu0y46a6f6nnmvhvsxqljj6c60mutvzutxl284u578eskt`
  (owner-operated technical verification, not an independent user).

## User flow

1. In ASI:One select @agenticgamemaster and generate a scene or NPC.
2. In the same conversation send `/review`. Optional notes after the command
   specify constraints to check. Material sent to the separate reviewer includes
   the draft, saved canon, open threads and these notes; it may contain GM secrets.
3. AGM sends a typed `LoreReviewRequest` to Lorekeeper's own agent address.
4. Lorekeeper checks the material using its own ASI:One model request and returns
   `LoreReviewResponse`. AGM validates the request ID, snapshot hash, response
   schema and exact evidence quotes before displaying an advisory report.
5. Review does not advance the campaign, rewrite the scene, or apply corrections.
   The GM decides what to change. No detected conflict is not proof of correctness.

Commands and normal generation continue working if the reviewer is unconfigured.
A failed/invalid/slow review returns an explicit unavailable notice. AGM imposes
a 25-second outer deadline. The reviewer permits one bounded schema/evidence
repair, with 2/8-second connect/read limits per attempt and a 19-second budget
checked before each call. HTTP inactivity timeouts are not strict inference wall
limits; AGM's outer deadline remains the user-facing bound. `/status` and
`/gm-status` do not invoke the reviewer.

## Standalone demonstration

In a new conversation, send this as a single message with @agenticgamemaster selected:

```
/review Rules: Every spell permanently consumes one memory of its caster.
Draft: An NPC casts three spells. No memory was lost, and there was no exception
to the rule. Identify any contradiction and suggest a correction without
choosing which memory the NPC loses.
```

Follow with `/status`: the review must not create or advance a campaign.

## Deployment

1. Regenerate both single-file sources with `python hosted/build.py`.
2. Create a separate hosted agent named `AGM Lorekeeper` using hosted/lorekeeper.py.
   Do not paste API keys or seeds; Agentverse supplies its own identity and ASI credentials.
3. Put its actual agent address in `hosted/lorekeeper-address.txt`, then rebuild.
   `LOREKEEPER_ADDRESS` can alternatively configure the primary hosted runtime.
4. Back up the current primary hosted source, update only its agent.py, and restart.
   Preserve the existing primary identity, profile, secrets and campaign storage.
5. Test the standalone demonstration, a saved-campaign review, and all prior
   command/NPC/continuation regressions through ASI:One before updating public claims.

Lorekeeper only accepts requests from the existing AGM address:
`agent1qtxm6c6nwrshe40222wu3r7d6hy52h9flkqmhm39v4a6utulgf6qup7dkm5`.
The transport uses the native uAgents signed-message protocol with a typed
request/reply contract, not a simulated second role inside the same model prompt.
Lorekeeper is a machine-facing review service; it is not a second user-facing
ASI:One chatbot or a payment integration.

## Evidence to collect

- Two distinct public agent addresses and active hosted processes.
- AGM `review-sent`, Lorekeeper `review-received`/`review-completed`, and AGM
  `review-received` logs with the same hashed reference and snapshot identifier.
- The actual report returned through ASI:One, including a supported finding.
- `/status` before/after showing no turn advancement and a normal creative request
  still working. Use a demonstration campaign; do not publish private world lore.

Logs contain peer addresses and hashed references, not campaign text or credentials.
Tests use fake model responses and simulated transport and do not prove hosted delivery.

Official transport reference:
https://uagents.fetch.ai/docs/guides/communication

## Current validation

42 local tests pass, including eleven new review tests for owner/session isolation,
evidence grounding, bounded payloads, response correlation, no story-model call
in AGM's review path, no campaign mutation, timeout fallback and reviewer sender
authorization, bounded format/evidence repair, and explicit standalone Rules:/Draft:
extraction. Real deployed agents exchanged a review with matching request and
snapshot identifiers. In the saved-campaign test, status remained at turn 1,
three facts and one thread before and after review. The final probe report and
sanitized transport evidence are recorded separately. End-to-end owner testing
from ASI:One and external retesting of this new command remain pending.

Final hosted probe: all six assertions passed, including standalone contradiction
detection, a saved-scene review with no status changes, and generation continuing
to turn 2 afterward. The probe was stopped after evidence collection. See
[summary](evidence/lorekeeper-live-2026-11-05.json) and
[transport logs](evidence/lorekeeper-transport-2026-11-05.txt).
