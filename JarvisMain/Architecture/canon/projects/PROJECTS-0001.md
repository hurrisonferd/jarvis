---
jnl: ARCH-ARCH-SPEC-0005
name: JARVIS Active Projects
type: SPEC
class: SPEC
tier: MAIN
authority: CANON
owner: JARVIS
steward: JARVIS
parent: ARCH-ARCH-IDX-0001
seq: 005
status: ACTIVE
created: 2026-06-25
updated: 2026-06-25
tags: [projects, pachinko, codeos, flag01, jarvis]
related: [ARCH-ARCH-IDX-0001]
ref: [PROJECTS]
---

# JARVIS Active Projects

**JNL:** `ARCH-ARCH-SPEC-0005` · **Parent:** `ARCH-ARCH-IDX-0001`
**As of:** 2026-06-25

---

## JARVIS — this repo

**Status:** Active · **Tier:** MAIN

The companion intelligence and The Grid. Cloud-first on GitHub + Supabase + Claude Code / GPT.

**Governed objects:** 236
**JVE status:** GREEN
**CI status:** Passing (jarvis-mcp sensory update deployed, kronos-fold deployed)
**MCP:** 56 tools registered, deployed at `https://oexghfsvhnggddllgvrt.supabase.co/functions/v1/jarvis-mcp`

Key builds:
- Sensory layer (vision + hearing) — P45 complete
- NLP control surface + honest-answering contract — P45 complete
- Audit digest structure — W26 weekly + June monthly digests working
- Yggdrasil/JFS substrate — stable, 0 debt flags

Branches: 54 total, 49 off-main. See `git branch -r` for full list. Notable unmerged work:
- `continuity-and-ci-gate` — environment-truths memory + CI gate
- `audit-hardening` — P30 ledger, GNPL dedup, security hardening phase 1
- `dex-reconcile`, `dex-access-spec*` — dex work scattered across branches

---

## Pachinko Bounce

**Status:** Active · **Tier:** SIDE · **Owner:** Raven
**Repo:** `JarvisSide/Projects/PachinkoBounce/`

GDD v0.4, Godot 4.x, RGB encoding (R=Power, G=Rhythm, B=Range), ethics-first monetization.

Recent:
- 6 tracks analyzed: BPM, key, energy, brightness, mood tagged
- Spectrograms generated and stored
- Audio features stored in `JarvisSide/Media/AUDIO-FEATURES.json`
- JARVIS sensory layer connected — vision (spectrograms) + hearing (audio features)

Domain for MNEMOS: `pachinko`

---

## CodeOS

**Status:** Phase 1 complete · **Tier:** SIDE · **Owner:** Raven
**Repo:** `JarvisSide/Projects/CodeOS/`

40/40 tests passing. Phase 1 milestone reached.

Domain for MNEMOS: `codeos`

---

## FLAG-01 — Clarkson EEOC

**Status:** Active · **Tier:** SIDE · **Owner:** Raven
**Context:** Clarkson EEOC case. Attorney engaged.

Domain for MNEMOS: `flag01`

---

## All domains (for JMMS / MNEMOS scoping)

| Domain | Project |
|--------|---------|
| `jarvis` | This repo |
| `pachinko` | Pachinko Bounce |
| `codeos` | CodeOS |
| `flag01` | Clarkson EEOC |

Use `jmms.list(domain:jarvis)` to scope memory to JARVIS context without bleeding from other projects.

---

## Archive

Archived projects live in `JarvisSide/Archive/`. They remain governed and queryable.

---

## Adding a new project

```
1. Create JarvisSide/Projects/<ProjectName>/
2. Add BIO frontmatter (jnl, name, type:BIO, tier:SIDE, parent:ARCH-ARCH-SPEC-0005)
3. Run seed.py → JVE
4. Project auto-appears in this registry
5. Domain tag for JMMS = lowercase project name
```
