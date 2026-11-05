# Hackathon evidence tracker

Updated 2026-11-05. This is a tracker, not a declaration that the challenge is complete.

## Public landing and outstanding verification

- Landing: https://agentic-game-master.atom139139.workers.dev/
- Published by the owner on Cloudflare; browser-verified November 5: page and
  images load, prompt-copy interaction succeeds, YouTube embed loads, and
  ASI:One buttons target the existing agent. This check did not run generation.
- The owner reports sending support the general-feedback versus Fetch.ai-track
  status discrepancy. Resolution remains pending; no support reply supplied.
- The landing explains the workflow and offers specific prompts in response to
  clarity feedback. It is an onboarding improvement, not proof of an external
  retest, repeat usage, payment, or challenge completion.

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

Owner screenshots supplied November 4 provide stronger, but distinct, signals:

- feedbackyopcional.jpg: project step 4, "Recibí feedback, anotá 1 cambio", is
  LISTO, reviewed by the system at 18:15. It explicitly confirms one outside-team
  builder trial with feedback plus a recorded change.
- tracks.jpg: Fetch.ai still says FALTA "1 prueba desde ASI:One con feedback y un
  cambio". Therefore the general feedback step is verified complete, but the
  challenge-specific ASI:One requirement remains unresolved in the UI. Do not
  infer its cause or claim Fetch.ai completion.
- The growth/repeat-use/payment section is explicitly optional; no revenue or
  return-usage proof has been supplied.

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

## November 5 update

Owner reports Fetch.ai now requests submission for review instead of the earlier missing-proof message. Challenge completion is not yet confirmed. Public short profile https://asi1.ai/ai/agenticgamemaster verified without login. The 56-second demo https://youtu.be/vDiybBDsA-Q replaces the long demo on the landing; new embed and link verified in the production browser.

## Optional agent collaboration — live technical verification

AGM Lorekeeper is deployed at
`agent1q007u0ldq88xpuxv6vweqkf5gqss468rn4363pufmhystwp4tc52wgd67ya`.
The existing AGM delegates `/review` through a typed uAgents request/reply exchange.
42 local tests pass. A real owner-operated hosted probe passed all six checks:
help advertises review, complete NPC output, successful saved-scene review,
standalone contradiction detection, unchanged status before/after review, and
normal story generation after the review (turn 2).

Proof: [live check summary](evidence/lorekeeper-live-2026-11-05.json),
[sanitized transport logs](evidence/lorekeeper-transport-2026-11-05.txt),
[probe source](evidence/lorekeeper-probe.py), and [integration details](LOREKEEPER.md).
The temporary probe is stopped after verification; AGM and Lorekeeper remain active.
This is technical team testing, not a real outside user, paid hiring, or a claim
that Fetch.ai has accepted bonus evidence. Testing the new command from the
owner's ASI:One chat and an external usability retest remain pending.
