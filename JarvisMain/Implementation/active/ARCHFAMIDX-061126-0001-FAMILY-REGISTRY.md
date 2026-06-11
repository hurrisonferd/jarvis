---
jnl: ARCH-FAM-IDX-0001
name: Family Registry
type: IDX
status: ACTIVE
tags: [families, containers, semantics, terminology, index]
definition: The semantic containers — named families that hold the system's terminology together so it cannot be lost (Raven-directed 2026-06-11). Each family has a leader class (the keyword), members, and a one-line charter. Pointers only — each member's truth lives in its own JD entry (JMS law).
purpose: Terminology is infrastructure. A term that belongs to no family drifts, duplicates, or dies. Every new term must join a family via its parent field or it is vapor (GL12 extension). This index is the map of the keywords.
---

**Definition:** the semantic containers. Leader class first — the keyword that holds the family.

## The families

| Leader (keyword) | Family charter | Members |
|---|---|---|
| **YGG — Yggdrasil** | the world-tree: ground everything stands on | JFS and all below; LAL; JD dictionary |
| **JFS — Jarvis File System** | compliance: naming, identity, structure, status, memory | JNS (naming) · JNL (identity) · JSL (structure) · JMS (mirror/movement) · JSS (status) · JMMS (memory tiers: JSTM/JLTM/JATM) |
| **JD — Dictionary** | truth: what exists, seq-minted, deterministic resolution | JD entries · seq serials · alias standard (ARCH-JD-JIP-0001) · JQL (query) |
| **PIPE — Cognition pipeline** | how knowing becomes truth | JGPP (exploration) → JIP (commit/transition) → JCS (runtime: JCS-D/E/F/G) → JD (truth) |
| **OVL — Overlay layer (B)** | cognitive interfaces above the dex, chartered by GOV-LC-SPEC-0001 | SL (temporal: micro + session) · JC (conversational) · CMVP (reserved, unminted) |
| **GS — God Systems** | cognition council, fixed at 27 | see ARCH-GS-IDX-0001 — never redefined here |
| **CONN — Connectors** | execution surface: how streams touch the cloud | jarvis-mcp RT modules · jarvis-dex action · events_list |
| **GOV — Governance** | the gate: how anything changes | Gold Law · Layer Contract (GOV-LC-SPEC-0001) · desk/proposals · rulings (P-B, P-C, no-repair-exemption) |

## Container rules
1. **Leader classes are protected terms.** YGG, JFS, JD, GS, CONN, GOV and the members
   above may not be re-coined for anything else — collision with a leader is an automatic
   naming rejection (extends the v13 identity rule from addresses to vocabulary).
2. **Every new term joins a family.** New objects declare `parent` into one of these
   subtrees; a term with no family is non-governed (GL12) and treated as vapor.
3. **Families point, never duplicate.** This index holds the roster; each member's truth
   lives in its own JD entry. `dex.py family <JNL>` resolves any subtree.
4. **New families are mintable** — through the desk, like everything else. CMVP becomes
   real the day it lands with a JNL and a seq, and not before.
5. **Words get graves, not deletions (lineage rule).** A roster term that dies goes
   DEPRECATED but stays listed — struck through, successor named: `~~OLD~~ → NEW`.
   The Rosetta table (MIDAS→AEGIS, SENTINEL→ARGUS+IRIS+HUGINN, GRAVEYARD→HADES) is the
   precedent: lineage stays queryable forever. Bulbasaur never disappears because
   Ivysaur exists. Preserving *why terms changed* is the point — not preserving every
   term, and never erasing one.
