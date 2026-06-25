---
jnl: ARCH-ARCH-IDX-0001
name: JARVIS Canon Index
type: IDX
class: REGISTRY
tier: MAIN
authority: CANON
owner: JARVIS
steward: MNEMOS
parent: ARCH-FAM-IDX-0001
seq: 001
status: ACTIVE
created: 2026-06-25
updated: 2026-06-25
tags: [canon, architecture, rebuild, recovery, index]
related: [ARCH-YGG-CORE-0001, ARCH-ARCH-SPEC-0003, ARCH-ARCH-SPEC-0004, ARCH-ARCH-SPEC-0005, ARCH-ARCH-SPEC-0006]
ref: [ARCHITECTURE, CANON]
---

# JARVIS Canon — Modular Index

**JNL:** `ARCH-ARCH-IDX-0001` · **Authority:** CANON · **Source:** GitHub main

JARVIS is rebuilt from this canon alone. Each section is self-contained. Changes to any
section update this index. The rebuild reference lives in Jarvis-Private — this repo
holds the public-facing canon structure.

---

## Sections

| Section | JNL | What it covers |
|---------|-----|----------------|
| [What is JARVIS](JARVIS-0001.md) | `ARCH-ARCH-JRV-0001` | Identity, purpose, the two dreams |
| [Services](services/SERVICES-0001.md) | `ARCH-ARCH-SPEC-0003` | All 14 edge functions + their endpoints |
| [Memory](memory/MEMORY-0001.md) | `ARCH-ARCH-SPEC-0004` | MNEMOS, JMMS tiers, Supabase tables |
| [Projects](projects/PROJECTS-0001.md) | `ARCH-ARCH-SPEC-0005` | Active projects, status, owned repos |
| [Rebuild](rebuild/REBUILD-0001.md) | `ARCH-ARCH-SPEC-0006` | Bring-up order, secrets, verification |

---

## How to use this canon

**Rebuild from scratch:**
1. Read `REBUILD-0001.md` → points to Jarvis-Private for the full rebuild seed
2. Read `SERVICES-0001.md` → know what you're deploying
3. Read `MEMORY-0001.md` → know what you're restoring
4. Read `PROJECTS-0001.md` → know what projects are live

**Verify an existing JARVIS:**
1. Compare `SERVICES-0001.md` against live endpoints
2. Compare `MEMORY-0001.md` against Supabase schema
3. Run `jarvis_self_test` via MCP

**Update this canon:**
- Edit the relevant section file
- Update `updated:` in frontmatter
- JVE passes — regenerate LAL
- Commit to main → Supabase mirror syncs

---

## Known repos

| Repo | Role |
|------|------|
| `hurrisonferd/jarvis` (this) | Canon, MCP source, governed record |
| `hurrisonferd/Jarvis-Private` | Secrets, private rebuild seed, personal context |

---

## Cloud topology

```
GitHub (hurrisonferd/jarvis)
  └── Canon (JARVIS main)
  └── MCP source (supabase/functions/jarvis-mcp/)
  └── Edge Functions (14 functions)
        └── Supabase (oexghfsvhnggddllgvrt)
              └── jarvis-mcp endpoint
              └── jarvis-dex
              └── jarvis-action
              └── kronos-fold
              └── mnemos-*
              └── grid-*
              └── send-push

Claude Code / GPT / Codex
  └── MCP connector → jarvis-mcp endpoint
```

---

## Version

- **Last full audit:** 2026-06-25
- **Governed objects:** 236
- **JVE status:** GREEN
