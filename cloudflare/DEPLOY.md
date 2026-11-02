# Cloudflare deployment preparation

Status: prepared for validation; NOT deployed. Local Agentverse process remains
active. No Cloudflare secrets, account resources or paid runtime have been created.

## Architecture

- One Python container retains the existing AGENT_SEED and polls its mailbox.
- A Worker routes authenticated storage calls to one Durable Object per
  sender/session. Campaign state and response deduplication live there.
- Python uses disposable SQLite only to run the existing engine. A response is
  returned only after the Durable Object commit succeeds. Failed commits leave
  remote state unchanged. Repeated commits replay safely by message ID.
- Runtime lifecycle is managed by a separate Durable Object. A one-minute Cron
  Trigger keeps it active/restarts it when enabled. This incurs continuous runtime
  costs; it is NOT an on-demand/free hosting configuration.
- The checked-in configuration defaults to AGM_ENABLED=false, so the cron cannot
  start a paid container accidentally. /health does not start the container.
- Public requests cannot reach the uAgents inspector, /connect or /disconnect.
  Users interact through the existing Agentverse mailbox, not an exposed /submit.

## Prerequisites

1. Docker Desktop with the Linux engine running (`docker info` must succeed).
2. Node and npm; run `npm ci` after cloning.
3. `npx wrangler login` in your terminal. A dashboard login alone does not
   authenticate Wrangler. Review the account shown by `npx wrangler whoami`.
4. Workers Paid/Containers access. Review cost before deployment/activation.

## Validate before deployment

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
npm run test:storage
npm run cf:check
docker build -t agentic-game-master:local .
```

The dependency lock was captured on Windows. Docker's Linux dependency resolution
and the exact installed Wrangler configuration schema must pass validation before
calling this deployment ready. Do not ignore schema warnings.

## Deployment sequence (requires account access and cost approval)

1. Build/validate first. Keep AGM_ENABLED=false for the initial deployment.
2. Deploy the Worker/container image with `npm run cf:deploy`.
3. Set AGM_PUBLIC_URL in wrangler.jsonc to the returned HTTPS workers.dev URL.
4. Store secrets with `npx wrangler secret put NAME` (interactive input):
   - ASI_ONE_API_KEY: same model API key as the local .env.
   - AGENT_SEED: EXACTLY the existing local seed. A different seed changes agent identity.
   - AGM_STORAGE_TOKEN: a new cryptographically random private token, at least 32 bytes.
   Secrets go to Cloudflare; never include them in source, vars or Docker build args.
5. Move existing campaigns before enabling the cloud agent. Add the same
   AGM_STORAGE_TOKEN to the local ignored .env, then stop the local agent during
   the migration window and run (replace the URL):
   `python cloudflare/migrate.py --url https://YOUR-WORKER.workers.dev` previews
   locally; adding `--apply` copies and reads back each campaign. Imports cannot
   overwrite different existing cloud state. The source DB stays unchanged.
   Old response-cache entries are not migrated; don't replay old story messages.
6. After migration verification, stop the local agent, set AGM_ENABLED=true and
   deploy. Never run the local SQLite-backed and cloud-backed agent simultaneously
   with the same identity, as they could consume each other's mailbox messages.
7. Inspect /health and make an authenticated POST to /admin/runtime. It reports
   process readiness, not end-to-end ASI:One/model availability.
8. Test /status, a new quest and continuation through ASI:One. Restart the container
   and verify persistence and duplicate handling before sharing with testers.

## Rollback

Set AGM_ENABLED=false and deploy, then stop the existing cloud container from the
Cloudflare dashboard (disabling the cron alone does not immediately stop it).
Export/copy cloud campaign state before returning to the local SQLite process.
Do not resume the old local DB as if it included newer cloud turns.

## Remaining verification

- Actual Wrangler dry-run and container build in this environment.
- Local Workers integration tests covering authentication, per-campaign routing,
  durable transactions, restart and idempotent retry.
- Credential setup, real migration verification, cloud deployment and cost estimate.
- Live Agentverse/ASI:One round trip against the cloud runtime.

## Sources

- https://developers.cloudflare.com/containers/api/durable-object-container/
- https://developers.cloudflare.com/containers/examples/env-vars-and-secrets/
- https://developers.cloudflare.com/containers/faq/
