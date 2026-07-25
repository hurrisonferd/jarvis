---
memory_tier: JLTM
grade: system
---

# YGGDRASIL — The World Tree

**Authority:** Canonical. Raven (John Barber) is final authority. No autonomous self-modification (GL2).

Yggdrasil is the root architecture of JARVIS. It exists so that **repository growth
increases organization rather than complexity** (GL7). Every persistent object that
enters Yggdrasil gains structure, location, governance, and discoverability —
automatically. Growth no longer implies disorder.

This is the substrate beneath everything else. It is designed to be **portable**: any
node — JARVIS-core or a Project repo — can mount the same kernel and inherit the same
guarantees. That portability is the point. JARVIS is meant to be the standard for AI
system governance and autonomy growth: **stable, auditable, explainable**. The kernel
below is how a system stays all three as it grows.

```
Yggdrasil (truth / world-tree / memory architecture)
│
├── JFS — Jarvis File System (the filesystem kernel)
│   ├── JNS — Naming      → what something is called   (semantic filenames)
│   ├── JNL — Navigation  → what + where it is         (global address/identity)
│   ├── JSL — Structure   → how information is organized (folder/format invariants)
│   └── JMS — Mirror      → reflect, never duplicate    (move references, not truth)
│
├── JD  — Jarvis Dictionary   → explains   (semantic authority)
├── LAL — Library Authority   → locates    (the map of all maps / discovery)
└── GOD_SYSTEMS               → execute    (the 27 — cognition, routing, governance)
```

## The resolution chain

```
JD explains  →  JNL identifies  →  LAL locates  →  Yggdrasil stores
```

- **Tags** answer *what is this?*
- **JNL** answers *where is this?*
- **IndexSummary** answers *how do I get there?*

## Separation of authority

| Layer | Owns | Does NOT own |
|-------|------|--------------|
| Yggdrasil | truth (the files) | discovery, execution |
| JFS | naming, identity, structure, mirroring | meaning |
| JD | meaning (definition, purpose, authority) | location, content |
| LAL | discovery (registries, indexes) | truth — it points, never duplicates |
| GOD_SYSTEMS | execution (think/route/govern) | the substrate |

## GL12 — Canonical Addressability Law

> Every persistent object must have an **address, location, tags, anchors, and index
> references**. Objects lacking addressability are considered **non-governed entities**.

A non-governed object is invisible to the loop (GL10). It cannot be recalled,
compressed, governed, or reinjected. Addressability is the price of admission to
Yggdrasil.

## Mirror-first (JMS law)

> Move references. Never duplicate truth.

Truth lives exactly once — in the file, at its JNL address. Everything else (JD
entries, LAL registries, MCP tool maps, Supabase rows) is a **mirror**: pointers,
tags, and metadata only. No mirror may store original truth. This is what keeps JD
and LAL thin as the tree grows to thousands of objects.

## Where to start

Read `jfs/JFS-SPEC.md` first. Understand JFS, and everything else becomes predictable.
Then `jfs/jnl-grammar.md` for the address format, `jd/JD-SPEC.md` for the dictionary
model, and `lal/` for the live registries.
