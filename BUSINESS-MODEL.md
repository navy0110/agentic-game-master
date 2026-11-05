# Agentic Game Master — monetization hypothesis

Research date: November 4, 2026. Proposed prices and validation targets are
experiments, not existing offers, implemented billing, customers or revenue.

## Customer and job

Start with tabletop GMs preparing recurring campaigns in original worlds. The GM
is the buyer; players do not need to pay to benefit from material the GM uses.
Prioritize people with an upcoming session and an actual preparation task.
RPG developers and worldbuilders are secondary segments; API licensing and
studio integrations should be validated separately after the first segment.

Value proposition: turn a brief from an existing world into usable session
material, with explicit player choices and a saved GM record in the same
conversation. Do not promise an autonomous live game engine or flawless memory.

## Initial offer to validate

Keep the working ASI:One demo accessible during the hackathon. Test a proposed
USD 5 one-time "Session Prep Pack" with interested GMs after they have used it.

Proposed deliverable: one short quest, one NPC with motives, GM secret and three
dialogue lines, and one triggered event, based on the customer's world brief.
Include up to two requested revisions. A pilot would be manually fulfilled and
reviewed by the team using the agent, clearly disclosed; this is not an
implemented self-service checkout or an unlimited campaign subscription.

Human review effort must be measured and costed. A valid payment test must
deliver what was offered; a hypothetical willingness-to-pay answer is not sales.

## Later recurring model

If users return for their next session and actual costs support it, test a
USD 9–12/month GM subscription with a clearly published successful-generation
allowance and context limits. These prices are hypotheses, not final pricing.
Do not sell unlimited use before measuring costs and heavy-user behavior.

Only usable delivered generations should consume a proposed paid allowance.
Internal retries, failures, /help, /status, /gm-status and exports should not
consume generation credits. Metering, entitlements, payment integration and
durable customer identity still need implementation before launching this plan.

## Competition and differentiation

- Friends & Fables offers a free tier and a USD 19.95/month Starter tier with
  broader game features; its higher tiers are USD 29.95 and 39.95/month.
  Source: https://fables.gg/pricing
- Quest Portal separates free tabletop tools from Pro AI preparation tools;
  one GM's subscription covers the workflow while players can remain free.
  Source: https://www.questportal.com/pricing
- Generic AI assistants already generate characters and quests. Generating
  text alone is not a defensible advantage. Test whether consistent world rules,
  complete structured outputs, session records and a focused preparation workflow
  make this agent worth returning to and paying for. These are differentiators
  to validate, not a proven moat.

## Validation before expanding scope

Recruit five GMs with sessions scheduled in the next week as an initial target.
Do not represent this target as achieved. For each, record with consent:

1. Their actual task, session date, and current preparation method.
2. Whether they obtained a complete usable result without live team assistance.
3. What they actually used in a real session, not just whether they liked the idea.
4. Preparation time measured against their normal method; correction effort.
5. Whether they returned within seven days.
6. Whether they accept a clearly described USD 5 pilot, and whether they pay.

An initial signal worth pursuing: at least three use material at the table,
two return, and one pays for the delivered pilot. These are decision thresholds
for a small exploratory sample, not statistically validated product-market fit.
Keep assigned Trick or Feedback trials separate from this customer experiment.

## Unit economics

Track input/output tokens, context size, all provider attempts including failures,
hosting, payment fees, refunds, and manual fulfillment/support time. Never log
customer secrets or private story content just to measure costs.

Contribution per pack = collected price minus inference (including retries),
allocated hosting, payment/refund costs, and variable human fulfillment costs.
For a USD 5 pack, a proposed goal is total variable costs no higher than USD 1.50
(70% contribution before fixed costs). This is a target, not measured performance.
If manual fulfillment cannot fit, increase price, reduce scope or automate only
after validating repeat demand. Free sponsor quota must not be mistaken for the
long-term operating cost.

## Hackathon positioning

The current Fetch.ai challenge requires a live Agentverse agent discoverable in
ASI:One, a public GitHub repository, qualifying assigned outside-team feedback
through ASI:One, and an improvement from that feedback. Revenue is not stated as
a mandatory completion condition in the current official rules.
Source: https://strangerbuilds.com/rules

Proposed submission wording:

> Our initial customer is a tabletop GM preparing a recurring campaign. We plan
> to validate a USD 5 session-preparation pack, then test a recurring GM plan if
> users return for subsequent sessions and measured costs support it. The current
> agent is a free prototype; billing is not yet implemented and we do not claim
> paying customers. We measure usable session content, repeat use and actual
> willingness to purchase a delivered outcome.
