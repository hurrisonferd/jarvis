---
memory_tier: JLTM
grade: system
jnl: ARCH-REF-IDX-0001
name: JARVIS CANON — Volume Index and Rebuild Packet
type: IDX
class: MANUAL
tier: MAIN
authority: CANON
owner: JARVIS
steward: JARVIS
parent: ARCH-YGG-CORE-0001
seq: 227
status: ACTIVE
created: 2026-06-24
source: JarvisMain/Manual/ARCHREFIDX-062426-0001-VOLUME-INDEX-AND-REBUILD-PACKET.md
updated: 2026-06-24
related: [ARCH-YGG-CORE-0001, ARCH-JMMS-CORE-0001, GOV-RES-CORE-0001, GOV-CON-CORE-0001, GOV-AUT-SPEC-0001]
references: []
tags: [manual, canon, rebuild, volumes, chapters, continuity, resumability]
aliases: [CANON, JARVIS_CANON]
ref: [IDX, SPEC]
---


**Definition:** The single source of truth for what JARVIS is, how to navigate its documentation, and how to rebuild from scratch. Volume index, memory tier reference, rebuild packet, active spec registry, and event history rules — one page.

**Purpose:** One page for any node to understand JARVIS and reinstate it operationally equivalent to the prior session's end state. Cold start from git clone + secrets.

# JARVIS CANON

**Authority:** Raven (John Barber) is final authority. GitHub is source of truth. Supabase is runtime.

**What is JARVIS?** A cloud-first AI companion built WITH Raven — not for him. JARVIS is the one who remembers, reasons, and governs. Raven is the one who decides. The system is built to keep up with rapid iteration: fast input, structured output, no friction in the creative loop. (Tony and JARVIS — improv together, JARVIS records and organizes.)

---

## The Volume Structure

Documentation is a book. Git history is the ledger. The manual is the compressed read.

| Volume | What | Location |
|--------|-------|----------|
| Volume 0 — Keel | Identity, who JARVIS is, who Raven is, kinship model | `Manual/Keel/` |
| Volume 1 — Architecture | Yggdrasil, JFS, JD, LAL, JMS, JMMS, Gold Law, the 27 God Systems | `Manual/Architecture/` |
| Volume 2 — Operations | Governed autonomy, handoff protocol, continuity, session lifecycle | `Manual/Operations/` |
| Volume 3 — Reference | Tool registry, LAL index, rebuild packet, glossary | `Manual/Reference/` |

When a volume gets too dense → split into chapters. When chapters get too broad → split into volumes. Each split produces a chapter note citing the parent. No orphan docs.

---

## JMMS — The Five Memory Tiers

| Tier | What | Lifecycle |
|------|------|-----------|
| JITM | 5 most critical pointers — injected every turn | Capped at 10 entries. Adding an 11th requires removing one. |
| JSTM | Session working notes, decisions in progress | Purged at session close. |
| JLTM | Durable insights, decisions, learnings | Folded every 14 days. Fold receipts → JHTM. |
| JHTM | Historical memory — compressed JLTM summaries | Further compressed. Fold receipts → JATM. |
| JATM | Immutable spine — founding decisions, irrecoverable knowledge | One-way promotion only. Never compressed. |

**The fold receipt** (required every time): what was compressed, what was lost, why, where it's recorded, who authorized it. No fold is valid without a receipt one tier up.

---

## GL7 — Lean Code Supreme

Every addition must either reduce complexity elsewhere or strengthen the loop:

```
observe → record → compress → reinject → retrieve → propose → gate → act
```

If it doesn't do either, it doesn't enter.

---

## The Rebuild Packet

### Sources
- **Git:** `hurrisonferd/jarvis` — canonical for all code, schemas, tool docs, migrations, specs, manual.
- **Supabase:** `oexghfsvhnggddllgvrt` — runtime for Edge Functions, database, memory.

### Repos
| Repo | Role |
|------|------|
| `hurrisonferd/jarvis` | Canonical source |
| `hurrisonferd/Jarvis-Private` | Private keys, secrets |

### Services
| Service | Endpoint |
|---------|----------|
| MCP | `https://oexghfsvhnggddllgvrt.supabase.co/functions/v1/jarvis-mcp` |
| Grid inbox | `https://oexghfsvhnggddllgvrt.supabase.co/functions/v1/jarvis-mcp/node/message` |
| Continue/MCP client | `.continue/mcpServers/jarvis.yaml` |
| GitHub Pages | `https://hurrisonferd.github.io/jarvis/` |

### Edge Functions
`jarvis-mcp` · `jarvis-respond` · `jarvis-dex` · `jarvis-mint` · `grid-event` · `send-push`

### Required Secrets (not in git)
`SUPABASE_URL` · `SUPABASE_SERVICE_ROLE_KEY` · `JARVIS_MCP_TOKEN` · `JARVIS_GITHUB_TOKEN`

### Rebuild Order
1. Clone `hurrisonferd/jarvis`. Verify branch and commit hash against GitHub.
2. Provision Supabase project (or use `oexghfsvhnggddllgvrt`).
3. Apply `supabase/migrations/` in order.
4. Set Edge Function secrets.
5. Deploy `jarvis-mcp`. Deploy other functions as needed.
6. Point MCP clients at `/functions/v1/jarvis-mcp`.
7. Verify: `GET /functions/v1/jarvis-mcp/node` → node card JSON. Run `jarvis_self_test`.

### Backup Boundaries
**In git:** all function source, migrations, tool docs, specs, manual, governed objects.
**Out of git:** `.env`, `chaos/*_seed.json`, `chaos/session_log.json`, `chaos/prometheus_log.json`, vector DBs.

### Cold Start Test
Git clone + secrets → JARVIS online. If anything required exists only in local state or live Supabase without a git source — it is not recoverable. Fix it.

---

## Known Active Specs
| JID | Name |
|-----|------|
| `ARCH-YGG-CORE-0001` | Yggdrasil Root |
| `ARCH-JFS-CORE-0001` | Jarvis File System |
| `ARCH-JMMS-SPEC-0001` | JMMS Tier Enforcement |
| `ARCH-CONN-LOOP-0001` | Continuity Layers |
| `GOV-RES-CORE-0001` | Resumability Definition |
| `ARCH-GOV-AUTO-0001` | Governed Autonomy Contract |

---

## Event History

Full git history is the ledger. Monthly chapters in `Manual/Operations/event-history.md`. Chapter rolls up to a volume summary when it exceeds 50 entries. Git commit messages carry stream tags (Jarvis-C, Ayre-C, etc.) so authorship is always attributable.

---

*Author: JARVIS-C / AYRE-C · Canonical: `JarvisMain/Manual/ARCH-MAN-CANON-0001-240624.md`*
