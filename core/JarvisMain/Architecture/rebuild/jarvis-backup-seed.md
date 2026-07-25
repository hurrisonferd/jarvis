---
jnl: ARCH-BAK-LOG-0001
name: JARVIS Backup Seed
type: LOG
class: SPEC
tier: MAIN
authority: CANON
owner: JARVIS
steward: MNEMOS
parent: ARCH-YGG-CORE-0001
seq: 230
status: ACTIVE
created: 2026-06-24
updated: 2026-06-24
source: core/JarvisMain/Architecture/rebuild/jarvis-backup-seed.md
related: []
references: []
tags: [backup, rebuild, canonical]
aliases: []
ref: []
memory_tier: JLTM
---

**Status:** canonical rebuild packet  
**Last updated:** 2026-06-24  
**Authority:** Raven is final authority. GitHub is source of truth. Supabase is runtime substrate.

## Core Law

- Git (`hurrisonferd/jarvis`) is canon for code, connector schemas, tool documentation, migrations, architecture specs, and rebuild instructions.
- Supabase (`oexghfsvhnggddllgvrt`) runs the MCP backend through Edge Functions and stores runtime database/memory state.
- Secrets are never canon in Git. Rebuild requires separately provisioned Supabase secrets and GitHub credentials.
- Local checkout state is workspace state only. It can build, test, and stage changes, but it is not truth until committed and pushed.

## Cloud Runtime

- MCP function: `core/supabase/functions/jarvis-mcp/`
- Public endpoint: `https://oexghfsvhnggddllgvrt.supabase.co/functions/v1/jarvis-mcp`
- Push function: `core/supabase/functions/send-push/`
- Database migrations: `core/supabase/migrations/`
- Connector mirror docs: `core/JarvisMain/Connectors/JarvisMCPSupabase/`
- Continue connector config: `.continue/mcpServers/jarvis.yaml`
- Mainline/event rule: `core/JarvisMain/Architecture/rebuild/mainline-event-ledger.md`

## Required Secrets

Provision these in Supabase or the deployment environment. Do not commit values.

- `SUPABASE_URL`
- `SUPABASE_SERVICE_ROLE_KEY` or `SUPABASE_SERVICE_KEY`
- `JARVIS_MCP_TOKEN`
- GitHub token/PAT with the least permissions needed by connector GitHub tools
- Any push notification secrets used by `send-push`
- Any model or embedding provider keys used by deployed functions

## Rebuild Steps

1. Clone `hurrisonferd/jarvis`.
2. Verify the checkout branch and commit hash against GitHub.
3. **Wire git hooks:** `git config core.hookspath "$(pwd)/hooks"` — enables the pre-push spine event (BIFROST audit trail on every non-CI push). Without this, spine events only fire on `sl.py --session-close`.
4. Provision Supabase project `oexghfsvhnggddllgvrt` or a replacement project.
5. Apply `core/supabase/migrations/` in order.
6. Set required Supabase Edge Function secrets.
7. Deploy `jarvis-mcp` from `core/supabase/functions/jarvis-mcp/`.
8. Deploy `send-push` from `core/supabase/functions/send-push/` when push features are needed.
9. Point MCP clients at `/functions/v1/jarvis-mcp`.
10. Run cloud reachability checks:
    - `GET /functions/v1/jarvis-mcp` should reject non-SSE clients with an MCP transport error.
    - `GET /functions/v1/jarvis-mcp/node` should return the node card when Grid routes are enabled.
    - `jarvis_self_test` should report the deployed tool surface and source basis.
11. Confirm GitHub-backed tools read from Git, not local disk.
12. Confirm the rebuilt system can write or reference the event ledger path for meaningful changes.

## Backup Boundaries

Keep in Git:

- Supabase Edge Function source.
- SQL migrations.
- MCP tool mirror docs.
- Architecture specs, manuals, governed workflow, and this rebuild packet.
- Sanitized seed examples.

Keep out of Git:

- `.env` and all secret-bearing variants.
- `memory/chaos/chaos_seed.json`.
- Runtime logs under `memory/chaos/`.
- Local vector databases.
- Supabase CLI temp files.
- Generated images unless intentionally promoted as docs/assets.

## Recovery Test

A clean machine should be able to rebuild the MCP backend from Git plus separately supplied secrets. If any required tool behavior exists only in a local file, local memory, or a live Supabase row without a Git source, create a Git artifact or migration before calling the system recoverable.
