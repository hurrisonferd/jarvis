---
name: Identity & Serial Standard — JID / JIDD / JNL / name
type: JIP
jnl: ARCH-JD-JIP-0001
status: ACTIVE
created: 2026-06-11
updated: 2026-06-13
tags: [jid, jidd, jnl, identity, serial, format, standard, dex]
definition: Disambiguates the four ways to identify a governed object and how each resolves. JID = the global mint serial (creation order), rendered jid-1, jid 1, jid #1, or jid <name>. JIDD = the domain-scoped mint serial (local order within a domain/system). JNL = the structural address (ARCH-YGG-CORE-0001). name = the semantic handle. JID and JIDD are NEVER embedded inside a JNL address — they are reserved mint serials kept separate so a serial lookup can never be confused with an address parse, and so "JD" is freed to mean the Dictionary, not a serial.
purpose: Eliminate the JD-dictionary / JD-serial / JNL-address confusion (the boundary leak GPT repeatedly hit). One object, four identifiers, zero collision.
---

# ARCH-JD-JIP-0001 — Identity & Serial Standard (JID / JIDD / JNL / name)

One object, four identifiers — each answering a different question, none colliding.

| Identifier | Question | Form | Example |
|---|---|---|---|
| **JID** | *which mint serial, globally?* | `jid-1` · `jid 1` · `jid #1` · `jid <name>` | `jid 1` → Yggdrasil |
| **JIDD** | *which serial within its domain?* | `jidd <domain> <n>` | `jidd gs 14` → AYRE (god-system #14) |
| **JNL** | *where in the structure?* | `[Domain]-[System]-[Type]-[Log]` | `ARCH-YGG-CORE-0001` |
| **name** | *what is it called?* | the semantic handle | `yggdrasil` · `jd yggdrasil` |

## The rules (Raven-directed 2026-06-13)

1. **JID is the mint serial.** What used to be written `JD-1` ("JD id") is now **`jid 1`**
   — because "JD" must mean the **Dictionary**, not a serial. `jd yggdrasil` is a *name*
   lookup in the dictionary; `jid 1` is a *serial* lookup. The two never overlap again.
2. **JID and JIDD are NEVER stored inside a JNL.** The structural address carries no mint
   serial. This is what lets a loader try "is this a JID?" and "is this a JNL?" as cleanly
   separate paths — no ambiguity between `jid 1` and `ARCH-…-0001`.
3. **Valid lookups:** by **JID** (`jid 1`, `jid-1`, `jid yggdrasil`), by **name**
   (`yggdrasil`, `jd yggdrasil`), or by **JNL** (`ARCH-YGG-CORE-0001`). Removed: `jd 1`
   as a *serial* key (the confusing form).
4. **Immutable after mint.** A JID/JIDD, once assigned, never changes (graves discipline:
   superseded objects keep their serial; successors get new ones).

## Back-compat (graves, not breakage)

Existing `JD-1` / `#1` references in the record still resolve (deprecated alias → the same
seq), so nothing already written breaks. But **`jid` is canonical going forward**; `jd`+number
is a deprecated rendering retained only so the past stays readable.

> Proposed by the GPT stream (proposal 8) as the serial-format standard 2026-06-11;
> broadened to the full identity model at Raven's direction 2026-06-13 to end the
> JD/JID/JNL confusion the streams kept hitting.
