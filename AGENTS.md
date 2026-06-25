# AGENTS.md — operating rules for any coding agent in this repo

JARVIS governance lives in `CLAUDE.md`. This file is the cross-agent **lean-code rule**
(Codex, OpenCode, Cursor, Copilot read `AGENTS.md`; Claude Code imports it via `CLAUDE.md`).

## Lean code — ponytail discipline (GL7 at the line level)

Before writing code, stop at the first rung that holds:

1. Does this need to exist? → no: skip it (YAGNI)
2. Stdlib does it? → use it
3. Native platform feature? → use it
4. Installed dependency? → use it
5. One line? → one line
6. Only then: the minimum that works

Lazy, not negligent: trust-boundary validation, data-loss handling, security, and
accessibility are **never** on the chopping block. Mark every deferred shortcut with a
`ponytail:` comment naming its upgrade path, so "later" doesn't become "never."

The best code is the code you never wrote. This is **GL7** (no expansion without
simplification) made concrete: it applies to every agent, every diff. Before a refactor or
a new subsystem, name the concrete capability it unblocks — "cleaner" is not a reason.

---

## JARVIS System State (2026-06-25)

### What's live
- **MNEMOS**: Partitioned by truth model.
  - **System** (JARVIS repo, public): `mnemos_vector.py`, `memories/`, `logs/`, `context/`, `knowledge/ml-ai.md`, `knowledge/techniques.md`, `knowledge/governance.md`
  - **Personal** (Jarvis-Private, private): `companion_core.md`, `knowledge/raven.md`, `knowledge/jarvis.md`, `knowledge/relationship.md`, `knowledge/mission.md`, `knowledge/projects/`
  - See `mnemos/README.md` for full truth model map.
  - 13 stores, ~500KB. Key: decisions.json (341 gov decisions), sessions.json, growth_archive (329KB JATM).
- **StarLogs**: `audit/starlogs/`, auto-generated via `scripts/sl.py --session-close`.
- **MusicOS**: 47 tracks, MID-0001–0047, 3 series. **Truth: Jarvis-Private/MusicOS/registry/**
  JARVIS repo: reference pointer only (`MusicOS/JD/MUSIC-REFERENCE.md`).
- **MonsterOS**: 26 monsters, MOS-0001–0026. **Truth: Jarvis-Private/MonsterOS/registry/**
  JARVIS repo: reference pointer only (`MonsterOS/JD/MONSTERS-REFERENCE.md`).
- **JVE validator**: `JarvisMain/yggdrasil/tools/jpl_validate.py` — run on any new JD entries.

### Top buried value
- `JarvisMain/Architecture/specs/throughput-posture.md` — HALO's boundary: production pressure
  may compress PRESENTATION but never PERSISTENCE or GOVERNANCE
- `JarvisMain/Architecture/specs/pre-act-verification-contract.md` — anti-hallucination contract
- `JarvisMain/Architecture/specs/IMPL-HON-SPEC-0001.md` — Honest Answering: name the gap, show
  the search, never fill with inference
- `JarvisMain/Architecture/CONTINUITY-THROUGH-THE-CONNECTOR.md` — resume-path documentation
- `JarvisMain/Architecture/specs/GOVKRSPEC-061326-0001-KNOWLEDGE-ROUTING-INDEX.md` — MIMIR
  routing table; available via `python3 scripts/sl.py --mimir`

### Naming conventions (for media cataloging)
- `4K_` prefix = high-res variant of base name
- `(plush)` suffix = plush toy variant (not a separate entity)
- `(N)` = duplicate marker — strip on ingest, keep in variants[]
- 4K filename typo: `Megalopotoise` → `Megaloptoise`
- Image canonical location: `JarvisSide/Media/images/`, audio: `JarvisSide/Media/audio/`
- DO NOT leave copies at repo root — always dedupe against Media/ before committing

### Active God Systems (29, all wired)
ORACLE → AEGIS → ODIN → KRONOS → SKADI → MNEMOS → HUGINN (primary pipeline)
T0: CHAOS, HADES, POSEIDON, ZEUS | T3: HALO, MIMIR | T5: ARGUS, ATHENA, LOKI,
NEMESIS, PROMETHEUS | T6: IRIS, MERIDIAN | T7: APOLLO, DANTE | T8: ATLAS | T9: HERMES

### Deferred / needs Raven
- `audit/required-checks-setup.md` — ✅ branch protection applied (2026-06-25), admin bypass enabled
- `Backups/cloud/` — manifest note only, no actual backup data
- JIP tracking logs (ActiveLog, IPLog, ISLog) — not wired, low urgency; GL12 audit confirmed container-level coverage works

### What was cleaned 2026-06-25
- 6 orphan PNGs (~21MB) removed from root (duplicates + unreferenced)
- `Implementation/task/` → merged into `Architecture/specs/` (9 specs surfaced)
- `Implementation/{Inactive,Implemented,active,tasks}/` — empty dirs deleted
- `intake/next-session-2026-06-25-late.md` → moved to processed/
