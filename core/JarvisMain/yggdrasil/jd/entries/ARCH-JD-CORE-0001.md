---
name: Jarvis Dictionary
type: CORE
class: SYSTEM
tier: MAIN
authority: CANON
owner: JFS
steward: MIMIR
parent: ARCH-YGG-CORE-0001
jnl: ARCH-JD-CORE-0001
seq: 7
status: ACTIVE
created: 2026-06-09
updated: 2026-06-26
source: core/JarvisMain/yggdrasil/jfs/JFS-SPEC.md
related: [ARCH-JNL-CORE-0001, ARCH-LAL-CORE-0001]
references: []
tags: [dictionary, semantic, core, architecture, dex]
aliases: [dex, jd, jarvis dictionary]
ref: [PRI, SPEC, IDX]
memory_tier: JLTM
---

**Definition:** THE one registry of every governed object (definition + JNL + tags + relationships) — a semantic DNS. Canonical name: JD (Jarvis Dictionary); 'the Dex' is its sanctioned nickname (the Pokedex-facing view). Same thing under every face: truth = core/JarvisMain/yggdrasil/jd/entries; discovery = LAL; query surface = the jarvis-dex function + jarvis_dex_*/jarvis_jd_resolve tools; live mirror = Supabase jd_entries (one table; jnl_registry is a view over it, unified 2026-06-18). One dictionary, one home, many faces — never a second registry.

**Purpose:** Be the single source of truth for what every object IS — centralized under Yggdrasil, mirrored (never duplicated) everywhere it is read.
