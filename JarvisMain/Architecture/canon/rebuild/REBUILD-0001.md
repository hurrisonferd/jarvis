---
jnl: ARCH-ARCH-SPEC-0006
name: JARVIS Rebuild Reference
type: RT
class: SPEC
tier: MAIN
authority: CANON
owner: JARVIS
steward: MNEMOS
parent: ARCH-ARCH-IDX-0001
seq: 006
status: ACTIVE
created: 2026-06-25
updated: 2026-06-25
tags: [rebuild, recovery, secrets, canonical, jarvis-private]
related: [ARCH-ARCH-IDX-0001, ARCH-ARCH-SPEC-0003, ARCH-ARCH-SPEC-0004]
ref: [ARCHITECTURE, REBUILD]
---

# JARVIS Rebuild Reference

**JNL:** `ARCH-ARCH-SPEC-0006` · **Parent:** `ARCH-ARCH-IDX-0001`

## The full rebuild seed lives in Jarvis-Private

The canonical rebuild seed — secrets, full step-by-step, recovery test — is in:

```
Jarvis-Private/rebuild/JARVIS_REBUILD_SEED.md
```

This repo holds the public-facing structure. Jarvis-Private holds the private execution layer.

---

## Quick reference (this repo)

### What to clone
| Repo | Role |
|------|------|
| `hurrisonferd/jarvis` | Canon, MCP source, governed record |
| `hurrisonferd/Jarvis-Private` | Secrets, private rebuild seed, personal context |

### Bring-up order

```
1. Clone both repos
2. Provision Supabase project oexghfsvhnggddllgvrt
   (or a replacement — update SUPABASE_URL in Jarvis-Private)
3. Apply supabase/migrations/ in order
4. Set required secrets (see Jarvis-Private/JARVIS_REBUILD_SEED.md)
5. Deploy edge functions in order (see SERVICES-0001.md)
6. Verify with jarvis_self_test
```

### CI pipeline

- `yggdrasil-validate.yml` — JVE on every PR (fails if ungoverned objects)
- `deploy-edge-functions.yml` — deploys all edge functions on push to main
- `MNEMOS Decision Capture` — cron-gated (check status in GitHub Actions)

### Verification commands

```bash
# MCP live check
curl https://oexghfsvhnggddllgvrt.supabase.co/functions/v1/jarvis-mcp
# → MCP transport error (rejects non-SSE, expected)

# Function list
curl https://oexghfsvhnggddllgvrt.supabase.co/functions/v1/jarvis-mcp/node
# → node card JSON when Grid routes enabled

# Run self-test via MCP connector (Claude Code / GPT)
jarvis_self_test

# Check JVE locally
python3 JarvisMain/yggdrasil/tools/seed.py
python3 JarvisMain/yggdrasil/tools/validate.py
```

---

## What lives where

| Artifact | Location |
|----------|----------|
| Canon structure | `JarvisMain/Architecture/canon/` |
| Edge function source | `supabase/functions/<name>/` |
| DB migrations | `supabase/migrations/` |
| MCP tool mirrors | `JarvisMain/Connectors/JarvisMCPSupabase/tools/` |
| Rebuild seed (private) | `Jarvis-Private/rebuild/JARVIS_REBUILD_SEED.md` |
| Secrets | Supabase env vars + Jarvis-Private |
| Chaos state | `chaos/` (never commit) |

---

## If GitHub goes dark

If `hurrisonferd/jarvis` is unavailable:
1. Every governed object is git-backed — clone the last known commit
2. Supabase may still be running (if the account is active)
3. Jarvis-Private has the personal context and last-known good state
4. Without GitHub: MCP write tools (`jarvis_mint`, `jarvis_jip_apply`) cannot propose git-first changes

---

## Backup boundaries

**Keep in Git:**
- Supabase Edge Function source
- SQL migrations
- MCP tool mirror docs
- Architecture specs, manuals, governed workflow
- This canon structure

**Keep out of Git:**
- `.env` and all secret-bearing variants
- `chaos/chaos_seed.json`
- Runtime logs under `chaos/`
- Local vector databases
- Supabase CLI temp files
- Generated images unless intentionally promoted as docs/assets
