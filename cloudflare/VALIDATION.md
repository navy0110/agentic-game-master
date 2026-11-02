# Local validation — 2026-11-02

- 14 Python tests passed: local state, corrections, duplicate messages,
  concurrency, remote engine restart/replay and failed remote commit.
- 4 JavaScript storage tests passed: revision checks, replay, imports and turn order.
- Worker JavaScript syntax checks passed.
- wrangler.jsonc validated against installed Wrangler 4.156.2 JSON schema: 0 errors.
- Migration preview found one local campaign; no data was sent to Cloudflare.
- Source and Docker context exclude .env, local databases and generated trial data.

Not verified:

- Docker Desktop Linux engine did not become available after launch; `docker info`
  reports the dockerDesktopLinuxEngine pipe is missing. Image build not run.
- Wrangler dry-run failed with Windows `spawn EPERM`, including when invoking its
  CLI directly (esbuild subprocess). Worker was not compiled or deployed.
- JavaScript storage tests use a fake transaction store, not the actual Durable
  Objects runtime. No Cloudflare integration or restart test has run yet.
- Wrangler OAuth, account, paid entitlement, secrets, cloud migration and live
  Agentverse round trip remain unverified.

The existing local agent is still running using local SQLite. No cloud runtime
was started, no secrets were uploaded, and no account billing settings changed.
