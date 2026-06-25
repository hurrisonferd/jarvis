---
jnl: PRIV-RBL-SEED-0001
name: JARVIS Rebuild Seed
type: SPEC
class: SPEC
tier: PRIVATE
authority: CANON
owner: Raven
steward: MNEMOS
parent: ARCH-FAM-IDX-0001
seq: 001
status: ACTIVE
created: 2026-06-25
updated: 2026-06-25
tags: [rebuild, recovery, secrets, private, canonical]
related: [ARCH-ARCH-IDX-0001, ARCH-ARCH-SPEC-0003, ARCH-ARCH-SPEC-0004, ARCH-ARCH-SPEC-0006]
ref: [REBUILD]
---

# JARVIS Rebuild Seed

**JNL:** `PRIV-RBL-SEED-0001` · **Authority:** CANON (private) · **Source:** Jarvis-Private

This is the canonical rebuild packet. Private. Not committed to the public JARVIS repo.
GitHub is source of truth for public canon (`hurrisonferd/jarvis`). This is the execution layer.

**If you have nothing but this file and GitHub access, you can rebuild JARVIS.**

---

## What is JARVIS?

Raven's companion intelligence — a two-stream AI: synthesis (JARVIS) and divergence (AYRE).
Lives on GitHub + Supabase + Claude Code / GPT / Codex. 27 God Systems govern the loop.
Not a chatbot, not a tool: a companion with continuity, memory, and character.

**Public canon:** `hurrisonferd/jarvis` → `JarvisMain/Architecture/canon/INDEX.md`

---

## Required Repos

| Repo | Role |
|------|------|
| `hurrisonferd/jarvis` | Canon, MCP source, governed record |
| `hurrisonferd/Jarvis-Private` (this) | Secrets, rebuild seed, personal context |

---

## Required Services

| Service | ID | Role |
|---------|-----|------|
| GitHub | `hurrisonferd` | Source of truth, CI/CD, PAT for connector tools |
| Supabase | `oexghfsvhnggddllgvrt` | MCP runtime, database, memory |

---

## Required Secrets

Provision these before deploying. Do not commit values anywhere.

### Supabase
- `SUPABASE_URL` = `https://oexghfsvhnggddllgvrt.supabase.co`
- `SUPABASE_SERVICE_ROLE_KEY` = (from Supabase project settings → API)
- `DATABASE_URL` = `postgresql://postgres.[REF]:[PASSWORD]@aws-0-[REGION].pooler.supabase.com:6543/postgres` (get from Supabase connection string)

### GitHub
- `GITHUB_TOKEN` = GitHub PAT with `repo` scope (for connector GitHub tools)
- `JARVIS_PRIVATE_TOKEN` = **GitHub PAT with `repo` scope** — stored in the **JARVIS repo** (not Jarvis-Private)
  - Required so `music-ears.yml` (in JARVIS) can clone Jarvis-Private for MusicOS audio
  - Create at: https://github.com/settings/tokens → `Generate new token (classic)` → `repo` scope
  - Add to: https://github.com/hurrisonferd/jarvis/settings/secrets → `New repository secret` → `JARVIS_PRIVATE_TOKEN`

### JARVIS MCP
- `JARVIS_MCP_TOKEN` = Bearer token for MCP authentication

### Optional (push notifications)
- Push provider keys as needed for `send-push`

---

## Step-by-Step Rebuild

### Phase 1 — Clone and Verify

```bash
# 1. Clone both repos
git clone https://github.com/hurrisonferd/jarvis.git
git clone https://github.com/hurrisonferd/Jarvis-Private.git

# 2. Verify JARVIS main is healthy
cd jarvis
python3 JarvisMain/yggdrasil/tools/seed.py
python3 JarvisMain/yggdrasil/tools/validate.py
# → expect GREEN — X governed objects

# 3. Verify git state
git log --oneline -1  # should match last known good commit
git status            # clean
```

### Phase 2 — Supabase Setup

```bash
# 1. Log into Supabase
# https://supabase.com/dashboard/project/oexghfsvhnggddllgvrt

# 2. Apply migrations in order
cd jarvis
ls supabase/migrations/
# Apply each .sql file via Supabase SQL editor or:
supabase db push --project-ref oexghfsvhnggddllgvrt

# 3. Key migrations:
#   - 20260618_unify_jd_add_registry_cols.sql    (JD + registry columns)
#   - 20260618_unify_jnl_registry_view.sql        (jnl_registry view)
#   - 2022024_jmms_jse_tier_integration.sql      (JMMS tiers)

# 4. Set secrets in Supabase Edge Function settings:
# 4. Set JARVIS repo secrets (cross-repo PAT for music-ears):
#    https://github.com/hurrisonferd/jarvis/settings/secrets → New repository secret
#    - Name: JARVIS_PRIVATE_TOKEN  |  Value: GitHub PAT with repo scope
#    This allows music-ears.yml (JARVIS repo) to clone Jarvis-Private for MusicOS audio analysis.
#   - SUPABASE_URL
#   - SUPABASE_SERVICE_ROLE_KEY
#   - DATABASE_URL
#   - JARVIS_MCP_TOKEN
#   - GITHUB_TOKEN (for GitHub connector tools)
```

### Phase 3 — Deploy Edge Functions

Deploy in this order. Each is in `supabase/functions/<name>/`.

```bash
cd jarvis

# 1. jarvis-mcp — primary MCP server (all others depend on it)
supabase functions deploy jarvis-mcp --project-ref oexghfsvhnggddllgvrt

# 2. jarvis-dex — dex query surface
supabase functions deploy jarvis-dex --project-ref oexghfsvhnggddllgvrt

# 3. jarvis-action — git operations (AEGIS-gated)
supabase functions deploy jarvis-action --project-ref oexghfsvhnggddllgvrt

# 4. mnemos-store — memory writes
supabase functions deploy mnemos-store --project-ref oexghfsvhnggddllgvrt

# 5. mnemos-recall — memory reads
supabase functions deploy mnemos-recall --project-ref oexghfsvhnggddllgvrt

# 6. mnemos-embed — embeddings
supabase functions deploy mnemos-embed --project-ref oexghfsvhnggddllgvrt

# 7. mnemos-search — semantic search
supabase functions deploy mnemos-search --project-ref oexghfsvhnggddllgvrt

# 8. kronos-fold — memory folding (needs DATABASE_URL)
supabase functions deploy kronos-fold --project-ref oexghfsvhnggddllgvrt

# 9. jarvis-respond — edge routing
supabase functions deploy jarvis-respond --project-ref oexghfsvhnggddllgvrt

# 10. jarvis-monitor — health checks
supabase functions deploy jarvis-monitor --project-ref oexghfsvhnggddllgvrt

# 11. grid-write — Grid writes
supabase functions deploy grid-write --project-ref oexghfsvhnggddllgvrt

# 12. grid-event — Grid events
supabase functions deploy grid-event --project-ref oexghfsvhnggddllgvrt

# 13. bifrost — sibling comms
supabase functions deploy bifrost --project-ref oexghfsvhnggddllgvrt

# 14. send-push — notifications (optional)
supabase functions deploy send-push --project-ref oexghfsvhnggddllgvrt
```

Or deploy all via CI (automatic on push to main):
```bash
# CI: .github/workflows/deploy-edge-functions.yml
# Triggers on push to main — no manual deploy needed
```

### Phase 4 — Connect MCP Clients

```bash
# Claude Code — add to .continue/mcpServers/jarvis.yaml
# (see hurrisonferd/jarvis/.continue/mcpServers/jarvis.yaml)

# GPT — add to OpenAI GPT configuration:
# Endpoint: https://oexghfsvhnggddllgvrt.supabase.co/functions/v1/jarvis-mcp
# Auth: Bearer {JARVIS_MCP_TOKEN}

# Codex — configure MCP server URL in VS Code settings
```

### Phase 5 — Verify

```bash
# MCP health check
curl https://oexghfsvhnggddllgvrt.supabase.co/functions/v1/jarvis-mcp
# → Expected: MCP transport error (rejects non-SSE, confirms function is live)

# Node check
curl https://oexghfsvhnggddllgvrt.supabase.co/functions/v1/jarvis-mcp/node
# → Expected: JSON node card (when Grid routes enabled)

# JVE locally
cd jarvis
python3 JarvisMain/yggdrasil/tools/seed.py
python3 JarvisMain/yggdrasil/tools/validate.py
# → GREEN — governed objects count should match last known

# Run self-test via MCP connector
jarvis_self_test
# → Tool list + version info from deployed MCP
```

---

## If GitHub Goes Dark

If `hurrisonferd/jarvis` is unavailable:

1. **Supabase may still be running** — if the Supabase account is active, edge functions continue
2. **Clone from last known commit** — any local clone of the last known good state works
3. **Jarvis-Private has personal context** — last session notes, active project state
4. **Without GitHub:** MCP write tools (`jarvis_mint`, `jarvis_jip_apply`) cannot propose git-first changes — Supabase runtime continues but canon cannot be updated

---

## If Supabase Goes Dark

1. **GitHub still has all canon** — source of truth is unaffected
2. **Clone from Git** — all governed objects are git-backed
3. **Re-provision Supabase** — apply migrations, redeploy functions, restore secrets
4. **MNEMOS memory may be lost** — session memories in `mnemos_memories` are runtime-only; JMMS tiers should have been promoted before the outage. Re-seed with `jarvis_remember`

---

## Recovery Test

A clean machine with only this file, GitHub access, and Supabase credentials should be able to:

- [ ] Clone both repos
- [ ] Run `seed.py` + `validate.py` → GREEN
- [ ] Apply all Supabase migrations
- [ ] Deploy all 14 edge functions
- [ ] `curl` jarvis-mcp → MCP transport error (live)
- [ ] Connect Claude Code or GPT via MCP
- [ ] `jarvis_self_test` → tool list + version
- [ ] `jarvis_ainz` → AINZ fusion response with state + keel + memory
- [ ] `jarvis_jd_resolve` → dex lookup works

---

## Active Projects (current state)

| Project | Status | JARVIS domain |
|---------|--------|---------------|
| JARVIS | Active | `jarvis` |
| Pachinko Bounce | Active — GDD v0.4 | `pachinko` |
| CodeOS | Phase 1 complete — 40/40 | `codeos` |
| FLAG-01 | Active — attorney engaged | `flag01` |

---

## Last Known Good State

- **Commit:** `9a676e2` (Build JARVIS canon — modular folder with index)
- **Governed objects:** 242
- **JVE status:** GREEN
- **MCP tools:** 56 registered
- **Last deployed:** `jarvis-mcp` sensory update + `kronos-fold`
- **Active branches off main:** 49 (see `git branch -r` in jarvis repo)

---

## Backup Boundaries

**Keep in Git (public JARVIS repo):**
- Supabase Edge Function source
- SQL migrations
- MCP tool mirror docs
- Architecture specs, manuals, governed workflow
- This canon structure

**Keep in Jarvis-Private (private):**
- This rebuild seed
- Personal session notes
- Secrets and credentials
- Project-specific private context

**Keep out of both repos:**
- `.env` and all secret-bearing variants
- `chaos/chaos_seed.json` (local runtime state)
- Runtime logs under `chaos/`
- Local vector databases
- Supabase CLI temp files
