# Agentic Game Master — feedback-driven improvement

Updated: November 4, 2026.

## Submission recap

A tester reported that the agent did not respond and that its capabilities were
unclear. We improved onboarding with an immediate explanation of what the agent
does and explicit ASI:One recipient instructions. During follow-up testing, logs
revealed JSON decoding failures and model timeouts, while one NPC response was
saved with missing content. We added schema-constrained generation, required NPC
fields, bounded retries for transient model failures, and clearer error messages.
We also kept model calls off the event loop and protected same-campaign updates.
The owner then confirmed that all three Agentverse regression prompts passed in
one run: spoiler-safe command guidance, NPC generation, and continuation from a
player's decision. An independent post-fix retest is still pending.

## Feedback received

> The agent doesn't respond and there is no feedback. I like the concept though curious how an agent can fufill this.

The owner confirms this original feedback was posted through Stranger Builds
and that a request for a retest has been sent. A platform feedback/assignment
link has not yet been attached here. Additional Slack feedback was reported,
but its registration as a separate platform trial has not been confirmed.

## What changed

| Observed problem | Change |
|---|---|
| Unclear capabilities and recipient selection | Immediate greeting explains text generation, campaign persistence, limitations and selecting @agenticgamemaster for every ASI:One message; public listing includes the same guidance. |
| JSON decoding failures in hosted logs | Request ASI schema-constrained responses; reject empty, malformed and token-truncated results before saving; distinguish response-envelope, content and storage failures in diagnostics. |
| ModelTimeout in hosted logs | One bounded retry for timeouts/transient connection or gateway failures; lower reasoning effort; attempt-level timing logs and actionable failure messages. |
| NPC response ended mid-sentence but claimed all requested details existed | For the tested three-dialogue NPC request, require separate name, role, motives, secret and three dialogue fields; render the visible NPC from validated fields rather than accepting a summary claim. |
| Command explanation depended on generation | Recognize the tested command-guidance question and answer without model inference or campaign changes. |
| Model request blocked hosted processing | Move processing off the event loop and serialize updates per campaign. |

## Verification

- 31 local automated tests passed on the current source, including recovery from
  one timeout, stopping after repeated timeouts, rejection of incomplete NPC
  fields, and keeping invalid results out of campaign storage.
- The owner shared a complete NPC response through ASI:One during testing.
- The owner reported **All 3 prompts passed — Nothing needs attention for this
  run** in Agentverse Testing after the current fixes.
- The three prompts cover command guidance, a harbor official NPC with three
  dialogue lines, and continuation after selling a forged deed to Baron Hult.
- Local mock tests and Agentverse Testing are technical evidence; they are not
  independent participant feedback.

## Evidence to attach before final submission

- Original assigned Trick or Feedback note/link and confirmation of ASI:One use.
- Screenshot of the successful three-prompt Agentverse Testing run.
- Public source commit containing these changes:
  https://github.com/navy0110/agentic-game-master/commit/1aec485fd31521cfd1dabaf9ee22243146cd71d7
- Independent tester's post-fix response, when received.

Do not describe automatic test success as universal reliability. Model latency
and service availability remain external dependencies. Existing older campaigns
are not retroactively repaired by these changes.
