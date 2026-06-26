---
memory_tier: JLTM
grade: system
---

# JFS — Jarvis File System (Kernel Specification)

**JNL:** `ARCH-JFS-CORE-0001`
**Authority:** Canonical
**Type:** Architecture / Kernel

JFS is the foundational filesystem architecture for all Yggdrasil-compatible systems.
Everything else in the architecture builds on top of JFS. **JFS is the umbrella for the
whole family of `J*` systems** — name, address, structure, mirror, status, memory,
dictionary, discovery, and language.

The **kernel** is four components — not peers, but one filesystem kernel:

```
JNS → Naming      (what something is called)
JNL → Identity    (what something is and where it exists)
JSL → Structure   (how information is organized)
JMS → Mirroring   (how information is reflected without duplication)
```

## The JFS family

| System | JNL | Role |
|--------|-----|------|
| **JNS** | `ARCH-JNS-CORE-0001` | naming — what it's called |
| **JNL** | `ARCH-JNL-CORE-0001` | identity/address — what + where |
| **JSL** | `ARCH-JSL-CORE-0001` | structure — how it's organized |
| **JMS** | `ARCH-JMS-CORE-0001` | mirroring — reflect, never duplicate |
| **JSS** | `ARCH-JSS-CORE-0001` | status — lifecycle state (drives auto-sort) → `jss/JSS-SPEC.md` |
| **JMMS** | `ARCH-JMMS-CORE-0001` | memory tiers (JSTM/JLTM/JATM) → `jmms/JMMS-SPEC.md` |
| **JD** | `ARCH-JD-CORE-0001` | dictionary — what it means |
| **LAL** | `ARCH-LAL-CORE-0001` | discovery — how to get there |
| **JPL** | `PROJ-JPL-BIO-0001` | language — the JARVIS programming/encoding layer |
| **YGG** | `ARCH-YGG-CORE-0001` | root — the world tree that holds it all |

The **kernel** (JNS/JNL/JSL/JMS) gives every object a name, address, place, and mirror.
**JSS** gives it a lifecycle. **JMMS** gives memory a time-horizon. **JD/LAL** explain and
locate it. **JPL** is the language the system is expressed in. All of it is JFS.

---

## JNS — Jarvis Naming System

**Defines:** what something is called.

**Responsibilities:** semantic file naming, log naming, system naming, version naming.

**Rule:** filenames are *specific and semantic*, never generic. A name states the
subject, the kind of object, its sequence, and its date. As the tree grows, a name alone
tells you what a file is — and when it landed — before you open it.

### Canonical filename convention

```
<Subject><Type>-<NNNN>-<MMDDYY>
```

- **`<Subject>`** — the specific folder/system/topic the object belongs to (never generic).
- **`<Type>`** — the kind: `Patch`, `Idea`, `Review`, `Log`, `Bio`, `Spec`, …
- **`<NNNN>`** — 4-digit zero-padded sequence within that subject+type.
- **`<MMDDYY>`** — the date the object was created.

```
PatchesPatch-0001-060826        # patch #1 in Patches, created 06/08/26
IdeasIdea-0025-112027           # idea #25 in Ideas, created 11/20/27
AuditReview-0003-060926         # audit review #3, created 06/09/26
```

Every dated artifact also carries a **JNL address** (its formal identity) and a **JD
entry**. The filename is the human/JNS form; the JNL is the machine identity. They agree:
the JNL's `Log` number matches `NNNN`, and JMS preserves both across moves.

**Forbidden:** `notes.md`, `final.md`, `untitled.md`, `Placeholder`, `Patch 1`, bare
numbers, or any name missing subject/type/sequence. (Stable canonical specs like
`JFS-SPEC.md` keep their established names; the convention governs new dated artifacts.)

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

## JSS — Jarvis Status System

**Defines:** the lifecycle state of every object — `TASK · EXPANSION · ACTIVE · INACTIVE ·
ARCHIVED · DEPRECATED`.

**Responsibilities:** carry one governed `status` per object; gate growth through
`EXPANSION` (GL7); drive physical location via auto-sort. Status changes emit to the record
(GL5). Full spec: **`jss/JSS-SPEC.md`**.

**Principle:** *Structure follows state.* Change the status, and JMS relocates the file to
the matching status subfolder — JNL preserved.

---

## JMMS — Jarvis MultiMemory System

**Defines:** how memory is tiered across time — **JSTM** (working) · **JLTM** (consolidated)
· **JATM** (ancestral, immutable).

**Responsibilities:** address memory by horizon; promote one-way JSTM → JLTM → JATM; keep
JATM append-only. Sits beside MNEMOS (meaning) as the *structure* of memory. Full spec:
**`jmms/JMMS-SPEC.md`**.

**Principle:** *JMMS is to time what JNL is to space* — it makes memory navigable across
horizons.

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
├── JFS  (umbrella)
│   ├── JNS    naming
│   ├── JNL    identity / address
│   ├── JSL    structure
│   ├── JMS    mirror
│   ├── JSS    status / lifecycle
│   └── JMMS   memory tiers
│       ├── JSTM   working
│       ├── JLTM   consolidated
│       └── JATM   ancestral
├── JD          dictionary (meaning)
├── LAL         discovery (location)
├── JPL         language
└── GOD_SYSTEMS execution (the 27)
```

**Design rule:** all persistent information entering Yggdrasil must conform to JFS —
names through JNS, identities through JNL, structure validated by JSL, mirrors managed
by JMS, **status assigned by JSS, memory tiered by JMMS**.

**Mental model:** Yggdrasil = World Tree (memory). JFS = Root System (filesystem).
Everything else grows from it. Understand JFS, then everything else becomes
predictable — for humans and for Claude, GPT, Codex, and every future agent.
