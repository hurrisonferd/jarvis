---
memory_tier: JLTM
grade: system
name: JSE — Jarvis Schema Envelope
type: SPEC
class: SPEC
tier: MAIN
authority: CANON
owner: JFS
steward: 
parent: ARCH-JFS-CORE-0001
jnl: ARCH-JSE-SPEC-0001
seq: 202
status: ACTIVE
created: 2026-06-17
updated: 2026-06-24
source: JarvisMain/yggdrasil/jfs/jse-schema.md
related: []
references: []
tags: [schema, envelope, jfs, format, architecture]
aliases: []
ref: [PRI, IDX]
memory_tier: JLTM
---

**Definition:** The umbrella that guarantees every JD entry carries the same complete 19-field frontmatter envelope — no missing fields, ever. Not a new store; the named contract seed.jd_entry_md writes and validate.py enforces.

**Purpose:** Make every object Pokedex-uniform and kill the steward:null-class gap: a missing KEY is a defect even when an empty value is legitimate. JNS names, JNL addresses, JSE contains.
