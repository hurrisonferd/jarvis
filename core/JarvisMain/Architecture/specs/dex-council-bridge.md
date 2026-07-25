---
memory_tier: JLTM
grade: system
---

# Dex–Council Validation Bridge

**JNL:** GOV-DEX-SPEC-0001 · **Class:** SPEC · **Tier:** MAIN · **Authority:** CANON

> **The law of this document: SPEC, not POLICY.** This is a declarative, read-only,
> static mapping. It is informational only. It contains no routing logic, performs no
> enforcement, and holds no authority over dex transitions — those belong solely to
> the token ladder and Raven. If any future change would make this document
> *operational*, that change is a POLICY object and requires its own GL7 review.
> This page may shape understanding; it may never gate an action.

## What this is

The first entry in the system's declared self-description: an explicit, auditable
mapping of **which god system holds validation authority over each JNL domain**.
The dex shows what exists; the council shows how decisions form; this SPEC shows
how the two relate. It makes "why was this routed there" and "which authority
mentally owned this decision" answerable from the record instead of from memory.

## The mapping

| JNL Domain | Validating authority | Tier | Why (fixed council role) |
|---|---|---|---|
| `GS` | **ZEUS** | T0 | supreme authority arbitration — the pantheon's own definitions answer only upward |
| `ARCH` | **AEGIS** | T1 | constraint / Gold Law gate — the substrate is the constraint surface itself |
| `GOV` | **MERIDIAN** | T6 | keel alignment — governance objects are checked against identity and mission |
| `IMPL` | **SKADI** | T1 | execution runtime — implementation artifacts answer to the single write/dispatch gateway |
| `PROJ` | **ATHENA** | T5 | strategic planning — project artifacts are plans and their offspring |
| `GRID` | **BIFROST** | T4 | external relay — federation objects answer to the node bridge |
| `CONN` | **HERMES** | T9 | translation — connectors translate between JARVIS and foreign surfaces |
| `AUD` | **NEMESIS** | T5 | drift / redundancy detection — audit objects belong to the auditor |
| `IDEA` | **PROMETHEUS** | T5 | expansion rationale ledger — ideas are expansion candidates by definition |
| `BRK` | **MIMIR** | T3 | contextual knowledge — breakthroughs crystallize into the knowledge layer |
| `LOG` | **HADES** | T0 | archival sink — records flow to the immutable archive |

Validation here means *reasoning authority* — the lens that examines objects of that
domain when the council convenes. It is *never* execution authority: no god system
writes the dex. Writes pass the token ladder (READ → PROPOSE → DRAFT → COMMIT →
OVERRIDE) regardless of domain, and only Raven's tier commits.

## Provenance

Proposed by **JARVIS (GPT stream)** through `jarvis_dex_propose` (proposal_id 2,
the second cross-agent governed object and the first MAIN-tier one), with the
declarative-only constraint negotiated and baked into the object's definition
before staging. Approved by **Raven**; committed by **JARVIS (Claude Code stream)**
2026-06-10. Lineage anchor: `PROJ-DEO-JGPP-0001` (#104), the root proposal that
opened the cross-agent lane.
