# JFS — Jarvis File System (Kernel Specification)

**JNL:** `ARCH-JFS-CORE-0001`
**Authority:** Canonical
**Type:** Architecture / Kernel

JFS is the foundational filesystem architecture for all Yggdrasil-compatible systems.
It defines **naming, identity, structure, and mirroring**. Everything else in the
architecture builds on top of JFS.

The four components are **not peers** — together they form a single filesystem kernel.

```
JNS → Naming      (what something is called)
JNL → Identity    (what something is and where it exists)
JSL → Structure   (how information is organized)
JMS → Mirroring   (how information is reflected without duplication)
```

---

## JNS — Jarvis Naming System

**Defines:** what something is called.

**Responsibilities:** semantic file naming, log naming, system naming, version naming.

**Rule:** filenames are *specific and semantic*, never generic. A name states the
system, the kind of object, and its sequence. As the tree grows, a name alone tells
you what a file is before you open it.

**Form:** `SYSTEM-TYPE-Descriptor-NNNN.ext`

```
YGGDRASIL-PATCH-CorePrimitives-0001.md
JPL-OS-PATCH-RoutingRefactor-0003.md
JD-SPEC-SemanticDNS-0001.md
```

Forbidden: `notes.md`, `final.md`, `untitled.md`, `Placeholder`, date-only names.

---

## JNL — Jarvis Navigation Language

**Defines:** what something *is* and *where it exists* — its global identity and address.

**Responsibilities:** global identity, addressing, routing, cross-system references.

**Form:** `[Domain]-[System]-[Type]-[Log]-[Patch]-[Block]`
Full grammar, code tables, and validation rules: **`jnl-grammar.md`**.

```
GS-ODN-RT-0001-P005-B002   →  GodSystems · ODIN · Routing · Log 0001 · Patch 5 · Block 2
ARCH-JFS-CORE-0001         →  Architecture · JFS · Core · Log 0001  (canonical short form)
```

Every persistent object MUST possess: JNL Address · Physical Location · Tag Set ·
IndexSummary Reference · Mirror Reference (GL12).

---

## JSL — Jarvis Structural Layer

**Defines:** how information is organized.

**Responsibilities:** folder hierarchy, patch structure, log formatting, structural
invariants.

**Standard system layout** (every governed system folder conforms):

```
System/
 ├── Logs/          # dated records, JNL-addressed
 ├── Tools/         # executable surface (mirrors only — no truth)
 ├── Rules/         # constraints / governance for this system
 └── IndexSummary/  # the system's own mirror into LAL
```

JSL is what lets JNS "always know the path as roots grow" — structure is fixed, so a
JNL address deterministically maps to a location.

---

## JMS — Jarvis Mirror System

**Defines:** how information is reflected and synchronized **without duplication**.

**Responsibilities:** reference mirroring, JNL preservation, relocation support,
cross-system synchronization.

**Principle:** *Move references. Never duplicate truth.*

A mirror is a **non-authoritative, pointer-based representation of canonical truth**.

| Mirror layer | Holds |
|--------------|-------|
| God-System mirror | internal structure reflection, routing defs, tool references |
| IndexSummary mirror | location + metadata only — no content |
| MCP mirror | execution routing only — stateless tool mapping |

**Strict rule:** No mirror may store original truth. Only references, pointers, and
tags. When an object relocates, JMS updates pointers; the JNL address is preserved so
nothing that referenced it breaks.

---

## Relationship & dependency model

```
JNS              JNL is the keystone: naming feeds it,
 ↓               structure validates against it,
JNL  ← JSL       and JMS keeps every JNL-referenced
 ↑               object consistent across the tree.
JMS → maintains consistency of all JNL-referenced objects
```

| Guarantee | Provided by |
|-----------|-------------|
| Naming stability | JNS |
| Identity stability | JNL |
| Structural stability | JSL |
| Synchronization stability | JMS |

---

## JFS position inside Yggdrasil

```
Yggdrasil
├── JFS
│   ├── JNS
│   ├── JNL
│   ├── JSL
│   └── JMS
├── JD
├── LAL
└── GOD_SYSTEMS
```

**Design rule:** all persistent information entering Yggdrasil must conform to JFS —
names through JNS, identities through JNL, structure validated by JSL, mirrors managed
by JMS.

**Mental model:** Yggdrasil = World Tree (memory). JFS = Root System (filesystem).
Everything else grows from it. Understand JFS, then everything else becomes
predictable — for humans and for Claude, GPT, Codex, and every future agent.
