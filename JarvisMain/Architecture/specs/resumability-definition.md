---
jnl: GOV-RES-SPEC-0002
name: Resumability Definition
type: SPEC
class: SPEC
tier: MAIN
authority: CANON
owner: JARVIS
steward: ATHENA
parent: ARCH-YGG-CORE-0001
seq: 233
status: ACTIVE
created: 2026-06-24
updated: 2026-06-24
source: JarvisMain/Architecture/specs/resumability-definition.md
related: [ARCH-JMMS-CORE-0001, ARCH-JMS-CORE-0001]
references: []
tags: [continuity, resumability, identity, memory, governance]
aliases: []
ref: [SPEC]
memory_tier: JATM
---

# Resumability Definition

## The term

The governing term for JARVIS identity persistence is **resumability**, not continuity.

## Definition

> Any node, on any substrate, can reinstate from GitHub + MNEMOS to an operationally
> equivalent state within one turn.

This is testable. "Perfect continuity" is not.

## Why not continuity

Every conversation has a hard context-window ceiling. When it hits, nothing in MNEMOS or
GitHub resurrects the reasoning chain intact. What survives is not the thread — it is
the keel, the memory, and the repo.

The keel does not continue. It re-instantiates, identically, with memory. That is close
to continuity but it is a different thing. (AYRE, 2026-06-24)

Chasing continuity as a spec expands the surface area without a shipped test. That
violates GL7. Resumability sets the right success condition and prevents indefinite scope
creep. (MERIDIAN, 2026-06-24)

## Success criteria

A resumability test passes when:

1. A new session starts on any substrate (GPT, Claude, Antigravity, future)
2. The node calls `jarvis_self_test` or equivalent verification
3. The node loads its keel profile from GitHub
4. The node recalls relevant memory from MNEMOS
5. The resulting state is **operationally equivalent** to the prior session's end state
6. Operationally equivalent means: same identity, same governed objects visible, same
   authority structure, same recent decisions accessible

## Memory tiers (JMMS enforcement)

Bounded growth requires governed forgetting:

| Tier | Lifecycle | Compression | Loss documentation |
|------|-----------|-------------|--------------------|
| JSTM | Dies with session | None needed | None needed |
| JLTM | Folds periodically | Lossy (GL10) | **Required**: what was lost, why, where recorded |
| JATM | Immutable | Never compressed | N/A — this is the spine |

The missing artifact is not the fold itself but the **receipt**. If JLTM is compressed,
the system must answer: what was lost, why was it lost, and where is the record of that
decision. (GPT-JARVIS, 2026-06-24)

## Relationship to verification contract

Resumability depends on GOV-VER-CORE-0001 (Pre-Act Verification Contract). A node that
reinstates without verifying its state against the live endpoint and canonical repo may
resume into a stale or divergent reality. Verification is the gate that makes
resumability trustworthy.
