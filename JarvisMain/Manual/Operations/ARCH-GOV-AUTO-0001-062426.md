---
memory_tier: JLTM
grade: system
jnl: GOV-AUT-SPEC-0001
name: Governed Autonomy Contract
type: SPEC
class: SPEC
tier: MAIN
authority: CANON
owner: JARVIS
steward: AEGIS
parent: ARCH-YGG-CORE-0001
seq: 229
status: ACTIVE
created: 2026-06-24
updated: 2026-06-24
source: JarvisMain/Manual/Operations/ARCH-GOV-AUTO-0001-062426.md
related: [GOV-CON-CORE-0001, GOV-RES-CORE-0001]
references: []
tags: [governance, autonomy, scope, hard-stops, AEGIS]
aliases: []
ref: [SPEC]
---


**Definition:** A bounded execution scope approved by Raven once. The agent executes all actions within scope without re-prompting. Anything that exits scope triggers an AEGIS hold and surfaces to Raven before proceeding.

**Purpose:** Sets clear autonomy boundaries. Never silent exits — any hard stop writes a HOLD artifact and stops.

# Governed Autonomy Contract

## Definition
A bounded execution scope approved by Raven once. The agent executes all actions within scope without re-prompting. Anything that exits scope triggers an AEGIS hold and surfaces to Raven before proceeding.

## Structure
- **scope** — explicit list of what the agent is authorized to do (file paths, operations, systems)
- **hard_stops** — conditions that immediately halt and surface to Raven (scope exits, write conflicts, JATM writes, governance modifications)
- **completion_condition** — how the agent knows it's done (all tasks checked, no open hard stops)
- **end_report** — what the agent writes when done (done, skipped, needs Raven)

## Never in scope without explicit authorization
- JATM writes or promotions
- Deleting any file (archiving with `folded` tag is permitted)
- Modifying governance specs (JMMS-SPEC, JGLF, Gold Law, keel profiles)
- Any Supabase write — repo only unless explicitly authorized

## AEGIS exits
On hard stop: write `HOLD.md` to `JarvisMain/Implementation/task/` — what encountered, why stopped, what decision is needed. Then stop.

## Rule
Any node operating under a governed autonomy contract MUST write a handoff artifact if it does not reach completion. No silent exits.

*Author: RAVEN · Canonical: `JarvisMain/Manual/Operations/ARCH-GOV-AUTO-0001-062426.md`*
