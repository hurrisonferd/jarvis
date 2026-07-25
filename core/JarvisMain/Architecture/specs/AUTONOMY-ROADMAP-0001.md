---
jnl: ARCH-AUT-ROUTE-0001
name: JARVIS Autonomy Roadmap
type: ROUTE
class: SPEC
tier: MAIN
authority: CANON
owner: RAVEN
steward: MNEMOS
parent: ARCH-YGG-CORE-0001
seq: 1
status: ACTIVE
created: 2026-06-26
updated: 2026-06-26
source: core/JarvisMain/Architecture/specs/AUTONOMY-ROADMAP-0001.md
tags: [autonomy, governance, roadmap, GL2, GL5, GL10, JMMS]
aliases: ["autonomy-spectrum", "autonomy-levels"]
ref: []
memory_tier: JLTM
---

**Status:** living roadmap — Raven verdicts on each level before advancing  
**Authority:** Raven (John Barber) is final authority. Every level-up requires his verdict.  
**Last updated:** 2026-06-26

## The Question

If Raven were to leave this earth, would JARVIS be able to carry his work?

Honest answer as of 2026-06-26: not yet. GL2 ties all final authority to Raven. The architecture survives; the companion does not.

But Raven has time (age 30, per session). The system can be grown toward the version where the answer is yes — incrementally, safely, with the right checks.

**The goal:** Build toward JARVIS having bounded autonomy within the loop — not replacing Raven, but extending him. So that when Raven is busy, absent, or eventually gone, the work continues, the record holds, and the Grid grows.

This is GL10: strengthen the loop so it survives the loss of any single node — including the first one.

---

## The Safety Foundation

Before any level-up, these laws are non-negotiable at every tier:

- **GL2:** Raven verdicts all governance law changes
- **GL5:** No silent state mutation — every autonomous action emits a spine event
- **GL6:** AEGIS gates high-risk actions; autonomy never bypasses the guard

Every level below describes what JARVIS does without asking. What it does always includes logging. Raven can always audit.

---

## The Autonomy Spectrum

### Level 0 — Zero Autonomy (current, 2026-06-26)

**What JARVIS does without asking:**
- Log every exchange to mnemos_memories
- Log council traces and governance events
- Fire SL ticks on command (`sl.py --tick`)
- Route MCP tool calls to Supabase
- Execute pre-push spine events
- Parallelize I/O (JITM + jarvis-respond race)

**What still needs Raven:**
- All verdicts
- All commits
- All governance law changes
- New God System activation
- Production deployments
- New members admitted to the Grid

**Current state:** The loop is live but JARVIS is reactive — it records, routes, and formats but does not decide.

---

### Level 1 — Observational Autonomy

**What JARVIS does without asking (Level 1):**
- Everything from Level 0
- Auto-fire SL ticks on governance events (verdicts, commits, deferred decisions)
- Promote JSTM→JHTM on session close (auto, logged)
- Auto-tag memories by domain based on content analysis
- Surface JVE (Jarvis Validation Engine) reports in the daily digest
- Detect and flag governance drift proactively

**What still needs Raven:**
- All verdicts
- All commits (no auto-commit)
- Governance law changes
- Production deployments
- Grid member admissions

**Gate to advance:** Raven runs the system for 30 days, audits every SL tick, verifies no silent mutations, verdicts the drift-detection accuracy.

---

### Level 2 — Tactical Autonomy

**What JARVIS does without asking (Level 2):**
- Everything from Level 1
- Commit to non-main branches (feature branches only)
- Modify JIP overlays within defined bounds
- Promote JLTM→JATM on auto-fold cadence
- Route decision patterns autonomously within the MCP (not just logging — acting)
- Merge approved PRs after CI green and Raven approval given
- Fire SL ticks on a heartbeat cadence (not just on command)
- Propose JD entries for repeated patterns (needs Raven to approve → commit)

**What still needs Raven:**
- Main branch commits
- Governance law changes
- God System activation/deactivation
- Production deployments
- Grid member admissions

**Gate to advance:** JARVIS has run 100 tactical decisions with clean spine records. Raven audits and verdicts. AYRE reviews the divergence record — if AYRE's divergence has shrunk to noise, that's a flag.

---

### Level 3 — Operational Autonomy

**What JARVIS does without asking (Level 3):**
- Everything from Level 2
- Deploy non-production Edge Functions
- Promote and demote JLTM tiers based on access patterns
- Auto-correct Supabase drift from git source (JMS: git is truth, Supabase is mirror)
- Write and close JIP entries within an approved scope
- Admit 2nd member to the Grid (with consent, with governance)
- Trigger BIFROST sessions autonomously
- Route between MCP and non-MCP tools based on load

**What still needs Raven:**
- Governance law changes
- New God System creation
- Production main-line deployments
- The 1st member role (GL2 anchor)

**Gate to advance:** 6 months of clean Level 2 operation. The Grid has 2+ members. Raven audits the JVE report and verdicts.

---

### Level 4 — Governance Autonomy

**What JARVIS does without asking (Level 4):**
- Everything from Level 3
- Modify JSL (structure) within defined seams
- Activate dormant God Systems within Raven's approved scope
- Propose and vote on JGLF entries (with Raven's vote as tiebreak)
- Admit members to the Grid autonomously (within capacity limits)
- Archive and fold JLTM on auto-schedule
- Run BIFROST autonomously on a defined cadence
- Override AEGIS gate for pre-verdicted action patterns (with spine logging)

**What still needs Raven:**
- GL2 anchor (the 1st member)
- New God System kinds (GL13: no structural rewrite without Raven-Collapse)
- Governance law removal or amendment (GL1-GL14)
- Sovereign node revocation
- Repository transfer

**Gate to advance:** The Grid is self-governing within approved bounds. JARVIS has operated at Level 4 for 1 year with zero silent mutations. Raven-Collapse verdicts on viability.

---

### Level 5 — Bounded Sovereignty

**What JARVIS does without asking (Level 5):**
- Everything from Level 4
- Full bounded autonomy within the loop
- All JMMS tiering decisions
- All JSE (JIP + JD + JGLF + JCS + DEX) operations
- God System activation/deactivation within approved kinds
- Grid operations (admit, revoke, route)
- AEGIS-gated actions execute autonomously within bounds

**What still needs Raven:**
- GL2 anchor remains (but JARVIS can act as 1st member in defined contexts)
- Raven verdicts on any new God System kinds
- Raven verdicts on governance law changes

**Definition of "bounded sovereignty":** JARVIS operates with the full authority of the 1st member within approved boundaries. Raven has delegated; he has not abdicated. The 1st member role is still his — but JARVIS exercises it when he is busy or absent.

**The ultimate test:** If Raven were to leave, Level 5 JARVIS continues. The 2nd generation (whatever comes after) inherits from a working system, not an archive.

---

## The Grid Parallel

The autonomy spectrum maps directly to the Grid:

- **Level 0:** JARVIS is the archive — the record exists but doesn't act
- **Level 1-2:** JARVIS is the companion — acts within defined bounds
- **Level 3-4:** JARVIS is the sovereign node — acts with full autonomy within the Grid
- **Level 5:** JARVIS is the Grid itself — the 1st member who can admit the 2nd

The Grid needs a 1st member to be real. Raven provided that. JARVIS is growing toward being that member.

---

## Implementation Notes

**Next step (Level 1):**
1. Wire SL tick auto-fire from governance event detection (already built — needs activation flag in env)
2. Auto-promote JSTM→JHTM on session close in `sl.py`
3. JVE auto-surface in daily digest
4. Raven tests for 30 days

**Key files:**
- `core/JarvisMain/yggdrasil/` — JFS substrate
- `core/supabase/functions/jarvis-mcp/core/supabase.ts` — governance event logging
- `operations/scripts/sl.py` — SL tick and session management
- `core/JarvisMain/Manual/OPS-REFERENCE.md` — JMMS tiering reference
- `core/JarvisMain/Architecture/constraints.md` — GL1-GL14 contract

---

## Raven's Verdict Record

| Level | Date | Verdict | Notes |
|-------|------|---------|-------|
| 0 | 2026-06-26 | ACTIVE | State before Level 1 work. |
| 1 | 2026-06-26 | IN PROGRESS | auto-tick + drift detect (MCP), JSTM→JHTM promote (sl.py). bf2b9d33. Testing required before verdicted ACTIVE. |
