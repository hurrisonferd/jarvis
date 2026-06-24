# JARVIS

Cloud-first AI orchestration system. Supabase Edge Function MCP connector + semantic memory + governed workflow.

**Authority:** Raven (John Barber) is final authority on all decisions. No autonomous self-modification.

---

## Roles

| Agent | Archetype | Job |
|-------|-----------|-----|
| Claude | Shiroe | Audit, plan, review, governance |
| Codex | Kang | Build, commit, push, execute |
| GPT | Kang | Production, execution |
| Gemini | Aizen | Ideation, interpretation |

---

## Source And Runtime

- GitHub `hurrisonferd/jarvis` is source of truth.
- Supabase project `oexghfsvhnggddllgvrt` is the runtime substrate for MCP, Edge Functions, database state, and memory.
- Local checkout `C:\Users\JB\jarvis\` is a working tree only. It is not canon until committed and pushed.
- Rebuild-critical MCP structure belongs in Git unless it is secret or private runtime data.

---

## Gold Law

- **GL7 supreme:** no expansion without simplification.
- **Continuity is law:** every larynx node (`free GPT`, `Codex`, `free Claude`, `Claude Code`, `Antigravity`) must verify live repo state, tool surface, and the current handoff before claiming progress.
- No autonomous self-modification.
- No silent state mutation.
- No unvalidated execution.
- Expansion requires `reduces_complexity=true` and `overlap_score_below=0.40`.
- Raven-Collapse is final authority on major changes.

---

## God System Pipeline

```text
AYRE -> AEGIS -> ODIN -> KRONOS -> SKADI -> MNEMOS -> HUGINN
```

Parallel: `HALO`, `MIMIR`, `BIFROST`

Forbidden edges: `SKADI->AEGIS`, `DANTE->SKADI`, `JANUS->SKADI`, `LOKI->HADES`

27 God Systems total. Do not redefine them. The rebuild-safe seed is documented in `JarvisMain/Architecture/rebuild/jarvis-backup-seed.md`; private seed files stay uncommitted.

---

## Key Files

| Path | Purpose |
|------|---------|
| `supabase/functions/jarvis-mcp/` | Cloud MCP connector, deployed as a Supabase Edge Function |
| `supabase/migrations/` | Database schema history needed for rebuild |
| `JarvisMain/Architecture/rebuild/jarvis-backup-seed.md` | Sanitized rebuild packet and authority map |
| `JarvisMain/Connectors/JarvisMCPSupabase/` | MCP tool mirror docs |
| `.continue/mcpServers/jarvis.yaml` | Cloud MCP client config |
| `chaos/chaos_seed.json` | Private local seed/state cache; do not commit |
| `chaos/session_sync.py` | Session start/end helpers, git-fingerprinted event log, JC continuity wrapper |
| `mnemos/mnemos_vector.py` | Legacy/local semantic memory helper |
| `JarvisMain/Manual/` | Operating manual + bounded event history |
| `intake/` | AI handoff review lane |
| `.env` | Secrets; do not commit |

---

## Services

| Service | Address | Notes |
|---------|---------|-------|
| JARVIS MCP | `https://oexghfsvhnggddllgvrt.supabase.co/functions/v1/jarvis-mcp` | Cloud-hosted Supabase Edge Function connector |
| GitHub | `hurrisonferd/jarvis` | Canonical source and rebuild truth |
| Supabase | `oexghfsvhnggddllgvrt` | Runtime substrate for MCP, database, Edge Functions, and memory |
| Ollama | `http://localhost:11434` | Optional local helper for legacy vector scripts only |
| GBrain | `~/.gbrain/brain.pglite` | Optional local helper |

---

## Local Environment

Local Python is for helper scripts and diagnostics only. The connector runtime is the deployed Supabase Edge Function, not a local `localhost:7777` process.

---

## File Permissions

Existing files may be owned by another Windows account. Grant write before editing:

```powershell
icacls "C:\Users\JB\jarvis\<file>" /grant "$env:USERNAME:(M)"
```

---

## Governed Workflow

All changes follow this loop:

```text
1. intake/     - add request or handoff
2. context     - check JARVIS status, relevant God Systems, Gold Law, and the latest handoff artifact
3. implement   - scoped changes only, no unrelated cleanup
4. verify      - syntax check, tests if applicable, then read back the written state
5. log         - log significant rationale through the cloud connector/Supabase when available
6. commit      - clean commit to main
7. sync        - verify cloud-visible GitHub state and redeploy Edge Functions when connector code or baked secrets change
8. recycle     - move processed intake; copy reusable patterns to recycle/
```

## Continuity Rule

Resumability is a hard requirement, not a courtesy. If work is incomplete, the node must leave a machine-readable handoff and the next node must re-verify against repo state before acting. The system does not treat memory as proof. The continuity record should be anchored in git history, with JC objects carrying the readable session event log and commits/handoffs carrying the durable spine.

---

## Active Projects

- **Pachinko Bounce** - GDD v0.4, Godot 4.x, RGB encoding (R=Power, G=Rhythm, B=Range), ethics-first monetization.
- **CodeOS** - Phase 1 complete, 40/40 tests.
- **FLAG-01** - Clarkson EEOC, attorney engaged.

---

## Do Not

- Commit: `chaos/chaos_seed.json`, `chaos/session_log.json`, `chaos/prometheus_log.json`, `chaos/mnemos_vectors.db`, `.env`.
- Redefine or renumber the 27 God Systems.
- Expand scope without simplifying something else.
- Mutate state silently.
- Run broad refactors unrelated to the task.
