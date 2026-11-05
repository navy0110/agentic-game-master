# Hackathon evidence tracker

Updated 2026-11-04. This is a tracker, not a declaration that the challenge is complete.

## Verified implementation

- Public source: https://github.com/navy0110/agentic-game-master
- Reliability fixes published and remote branch verified:
  https://github.com/navy0110/agentic-game-master/commit/1aec485fd31521cfd1dabaf9ee22243146cd71d7
- Hosted Agentverse address: `agent1qtxm6c6nwrshe40222wu3r7d6hy52h9flkqmhm39v4a6utulgf6qup7dkm5`
- Verified profile handle: `@agenticgamemaster`
- Hosted compile/start and Almanac registration confirmed via AVCTL logs.
- User tested generation through ASI:One; subsequent /status recovered 12 facts
  and 6 open threads. After restart it recovered the saved campaign at turn 2.
- /status hides story details; /gm-status includes secrets. These are display
  modes, not distinct authenticated GM and player roles.
- Owner/assistant development tests are NOT external Trick or Feedback trials.

## Event status

- Project created in Stranger Builds: user confirmed.
- Fetch.ai challenge accepted: VERIFIED on the public Stranger Builds project
  page on 2026-11-03. It shows FETCH.AI · EN CURSO and the house on Fetch.ai's island.
- Stranger Builds public project: https://app.strangerbuilds.com/p/agentic-game-master
- Public project link is published and points to the correct hosted Agentverse profile.
- Public page rechecked on 2026-11-04: team members @navynox and @ivavala
  are both listed explicitly.
- Public project now shows ONLINE, MEJORADO and USUARIOS REALES. Both Fetch.ai
  and Base44 challenges are listed as EN CURSO; neither is represented here as
  completed. Base44's actual build and qualifying evidence remain unverified.
- Public evidence gallery shows one team proof image dated November 4 with the
  caption: "After the fixes, all three Agentverse automated tests passed: command
  guidance, NPC generation, and story continuation." This gallery count is not
  a count of independent participant trials.
- Public Agentverse profile verified logged out:
  https://agentverse.ai/agents/details/agent1qtxm6c6nwrshe40222wu3r7d6hy52h9flkqmhm39v4a6utulgf6qup7dkm5/profile
  Profile shows Active and ASI Available.
- Direct ASI:One link copied from the profile's Chat with Agent button:
  https://asi1.ai/ai/agent1qtxm6c6nwrshe40222wu3r7d6hy52h9flkqmhm39v4a6utulgf6qup7dkm5
  End-to-end conversation verified by the owner; independent participant testing pending.
- Public repository creation verified via GitHub: 2026-11-02 19:36:24 UTC
  (16:36:24 ART), after the event opening. Preserve first-commit history too.
- Demo produced locally: videos/agentic-game-master-demo/renders/agentic-game-master-demo.mp4,
  113.1 seconds, English voice/subtitles, 1080p. Encoded-file checks passed.
  Published demo: https://youtu.be/WqWlwnUzFIE — public watch page verified on
  November 4, title "Agentic Game Master | Stranger Builds Demo", duration 1:53.
  Attach this watch URL in the actual submission; submission itself remains pending.
- Current rules updated November 4 allow team/community changes until submission
  close on November 8, 23:59 ART; older November 3 lock guidance is superseded.

## Participant feedback — owner-confirmed platform note

Rules rechecked on 2026-11-04: the current minimum is ONE outside-team builder's
written feedback via assigned Trick or Feedback, with tries through ASI:One,
and one resulting improvement. Earlier guidance requiring three was incorrect
for these current rules. Additional rows below are optional additional evidence.
The owner reports all three automatic regression prompts passed together, and
the corresponding team proof is now listed publicly on the project page. Those
automatic tests do not count as outside-builder feedback.

| Trial | Assigned participant reference | Date | ASI:One usage proof | Original note | Verified in event |
|---|---|---|---|---|---|
| 1 | Owner confirms original feedback was posted through Stranger Builds; assignment reference pending | Report supplied 2026-11-04 | Usage proof link pending | Original response/clarity feedback supplied in this conversation | Platform note confirmed by owner; app completion status not independently checked |
| 2 | Additional Slack comment reported by owner; platform registration requested | Unknown | Pending | Exact note/reference pending | Not confirmed as a separate qualifying platform trial |
| 3 | Pending | | | | No |

Do not add personal information to this public repository. Store only participant
references/proof links whose publication is authorized. Keep private evidence private.

## Feedback-driven improvement — implemented; external retest pending

### Report supplied by the owner on 2026-11-04

Original note: "The agent doesn't respond and there is no feedback. I like the
concept though curious how an agent can fufill this."

The owner confirms the original note was submitted through Stranger Builds.
Its assignment reference and ASI:One usage proof have not been supplied here;
platform challenge-completion status has not been independently checked. Follow-up logs supplied by
the owner confirmed JSONDecodeError and ModelTimeout failures. These do not
establish the exact cause of the original tester's individual incident.

Changes implemented: move blocking hosted processing off the event loop,
serialize requests per campaign, shorten model network waits, distinguish model
timeout/unavailability from validation errors, answer greetings without inference,
and clarify recipient selection and actual capabilities in the public listing.
The final demo watch page is verified at https://youtu.be/WqWlwnUzFIE.
The owner updated the hosted code and confirmed all three Agentverse regression
prompts passed together. An independent retest remains pending. See
IMPROVEMENT-RECAP.md for the full recap and missing proof links.

Record the real note, the problem, the change, its commit and the follow-up result.
Existing fixes (player-agency instructions, corrected canon, spoiler-safe status,
deduplication and hosted logger compatibility) came from development testing.
Do not present them as changes requested by assigned outside participants.

## Before submission

- Complete the sponsor brief and required feedback/improvement steps in the app.
- Verify public repo, hosted agent and ASI:One link from a tester's account.
- Explain what existed before: Memeria predates this event and is not the entry;
  this repository and independent agent are the new work. No Memeria code included.
- Declare libraries/tools and licenses actually used.
- Team writes its own submission answers; use verified evidence only.
- Submit in the app before 2026-11-08 23:59 ART; a draft is not a submission.
- Keep the agent available through results on 2026-11-19; check hosting/model quotas.

Official rules: https://strangerbuilds.com/rules
