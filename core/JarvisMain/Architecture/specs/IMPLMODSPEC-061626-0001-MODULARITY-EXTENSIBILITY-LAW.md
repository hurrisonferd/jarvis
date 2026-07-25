---
memory_tier: JLTM
grade: system
jnl: IMPL-MOD-SPEC-0001
name: Modularity & Extensibility — Field Plan + Gold Law Proposal
type: SPEC
status: TASK
tags: [modularity, extensibility, gold-law, yggdrasil, governance, roadmap, gl7, gl12, automation, routing, mirroring]
definition: The governed Field Plan for making JARVIS self-extending — adding a spell, a domain, a JID-card field, or a lens must cost one data row plus one reseed, never a structural rewrite. Carries (1) a proposed new Gold Law elevating modularity/extensibility to a hard constraint and part of Yggdrasil compliance, (2) the concrete compliance criteria Raven named (formatting, pointing, mirroring, data organization, automation, routing), (3) the best-order build roadmap, and (4) a Gold Law enforcement audit (which laws are mechanically vs manually enforced).
purpose: Persist the plan as canon so it survives session resets — no re-deriving the same arc across fragmented sessions. Raven directs (2026-06-16) that extensibility and modularity always apply and may become a Gold Law. GL2 holds — this TABLES the law for Raven's verdict; merging saves the plan, ratification into constraints.md is a separate explicit step.
---

# Modularity & Extensibility — Field Plan + Gold Law Proposal

> Raven, 2026-06-16: *"make sure extensibility and modularity always apply to the system and are
> a part of yggdrasil compliance, even potentially a gold law due to how we want formatting,
> pointing, mirroring, data organization, automation, and easy routing for me and jarvis and ayre."*
> The Shiroe principle: full control of the field — plan, save, execute — with a system that knows
> and tracks itself, where adding a thing is never a day-long endeavor.

## 1. Proposed Gold Law — **GL13 · The Law of Open Extension** (number pending Raven)

> **No structural rewrite to add a kind of thing.** Every extension of the system — a spell, a
> domain, a type, a JID-card field, a lens, a god-routing — must enter through a *modular,
> data-driven seam*: one new row / file / entry plus one reseed. Formatting, pointing, mirroring,
> data organization, automation, and routing stay uniform and auto-derived from that seam. If
> adding an instance of an existing kind costs more than its own data plus a single regeneration,
> that friction is a **defect to be removed**, not a cost to be paid. Extensibility is part of
> Yggdrasil compliance and is checked, not trusted.

Precedent: GL12 (Canonical Addressability) was added when addressability proved load-bearing. Open
Extension is the same tier — it governs *how the tree grows* so growth never outruns governance
(GL7's positive form: the system stays simple to extend, which is what keeps it simple at all).

## 2. Modularity-compliance criteria (Raven's six, made concrete + checkable)

| Pillar | What it means | Today | Mechanical check |
|---|---|---|---|
| **Formatting** | one canonical format per object kind (frontmatter grammar, FMT §3) | strong | JVE JNS/FMT |
| **Pointing** | every object has a JNL + LAL resolution (GL12) | strong | JVE GL12 closure |
| **Mirroring** | truth in git, projected to Supabase; never two authorities (Git-First Canon) | strong | Sync lens (drift) |
| **Data organization** | status-driven autosort, flat folders, tier/parent family tree | strong | JVE status/mirror |
| **Automation** | seed/validate/grimoire regenerate from data; CI enforces | strong | CI yggdrasil-validate |
| **Routing** | new tool → grimoire row → ODIN/wiring resolvable; JD resolve by name | partial | map-matches-ground |

The seam pattern proven by the spell mint (this session): a single data table → one reseed →
source doc + JD entry + grimoire row materialize together. That pattern is the law made real.

## 3. The Field Plan (best order)

- **P1 — Mint the full spell surface ✓ DONE** (CONN-MCP-RT-0019..0053; 155→190 governed). The
  arsenal is now visible to omnivision / dex / grimoire. Proof-of-pattern for the seam.
- **P2 — Trivial extensibility.** New *system* tokens are already free-form (IMPL-TLR, IMPL-MOD
  validate without table edits). Close the remaining friction: a `new-domain` / `new-type` helper
  that edits the jnl.py ↔ jfs.ts token tables in lockstep (JVE already fails on drift), and a
  JID-card field schema so extra identifiers are one declaration, not a code hunt. Outcome: adding
  a domain or a card field is one command.
- **P3 — The World Spell (Yggdrasil audit / GL7 engine).** 80% exists: `jarvis_eyes` already fuses
  live-state + wiring + vitality, and seed emits HEALTH / ORPHAN / TOPOLOGY lenses. Add the missing
  20%: GL7 bloat/overlap detection (overlap_score, reduces_complexity), git/freshness drift (mirror
  stamp vs HEAD commit), and outdated/stale-object flags. One fusion that pinches the tree and names
  what is missing, old, unmapped, or bloated — the GL5/GL7 enforcement engine.
- **P4 — Finish the forge.** index.ts → core/ + tools/ one-file-per-spell, so the *runtime* mirrors
  the modular grimoire the JD now describes. Then a spell is one file at every layer.

## 4. Gold Law enforcement audit (Raven's question, 2026-06-16)

**Half enforced — the structural half.**

| Law | Enforcement | Mechanical? |
|---|---|---|
| GL12 addressability | JVE GL12 closure in CI | **Yes** |
| GL2 no autonomous self-mod | PR → Raven verdict → merge | **Yes** (workflow is the gate) |
| GL6 AEGIS gates writes | token gate in core/auth.ts | **Yes** (connector writes) |
| GL5 no silent mutation | dex_events spine + convention | **Partial** — not every mutation provably emits |
| GL7 no expansion w/o simplification | review-time judgment | **No** — no overlap/complexity gate exists |

The **behavioral** laws (GL5 universal eventing, GL7 anti-bloat/overlap) ride on discipline, not
code. **P3 closes that gap** — the World Spell *is* the GL5/GL7 enforcement engine. GL13 (proposed)
would be born mechanically enforced via the same lens.

---

*Status TASK. GL2: the law is proposed, not enacted — Raven ratifies GL13 into
`core/JarvisMain/Architecture/constraints.md` + `CLAUDE.md` by explicit verdict. Merging this spec saves
the plan to canon.*
