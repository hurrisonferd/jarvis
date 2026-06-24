---
name: Identity & Serial Standard — JID / JIDD / JNL / name
type: JIP
class: SPEC
tier: MAIN
authority: CANON
owner: JFS
steward: 
parent: ARCH-JD-CORE-0001
jnl: ARCH-JD-JIP-0001
seq: 124
status: ACTIVE
created: 2026-06-11
updated: 2026-06-24
source: JarvisMain/Implementation/active/ARCHJDJIP-061126-0001-JD-SERIAL-FORMAT-ALIAS-STANDARD.md
related: []
references: []
tags: [jid, jidd, jnl, identity, serial, format, standard, dex]
aliases: []
ref: [PRI, IDX]
memory_tier: JLTM
---

**Definition:** Disambiguates the four ways to identify a governed object and how each resolves. JID = the global mint serial (creation order), rendered jid-1, jid 1, jid #1, or jid <name>. JIDD = the domain-scoped mint serial (local order within a domain/system). JNL = the structural address (ARCH-YGG-CORE-0001). name = the semantic handle. JID and JIDD are NEVER embedded inside a JNL address — they are reserved mint serials kept separate so a serial lookup can never be confused with an address parse, and so "JD" is freed to mean the Dictionary, not a serial.

**Purpose:** Eliminate the JD-dictionary / JD-serial / JNL-address confusion (the boundary leak GPT repeatedly hit). One object, four identifiers, zero collision.
