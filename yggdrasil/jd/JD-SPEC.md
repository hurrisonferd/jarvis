# JD — Jarvis Dictionary (Specification)

**JNL:** `ARCH-JD-CORE-0001`
**Authority:** Canonical
**Purpose:** The semantic authority of JARVIS. JD answers **"what is this and why does
it exist?"** — and nothing else.

JD is not a wiki. It is closer to a **semantic DNS**: it stores definition, identity,
authority, and routing hints, then delegates the actual retrieval to JNL and LAL. A
traditional dictionary stores content; JD stores *meaning + a pointer*.

```
JD explains  →  JNL identifies  →  LAL locates  →  Yggdrasil stores
```

Each layer has a single responsibility. JD stays thin because JMS forbids duplication —
JD never holds summaries, file lists, or mirrors. It holds a definition and a JNL.

---

## Entry schema

Every JD entry is a small record:

| Field | Meaning |
|-------|---------|
| `Name` | the canonical name |
| `Type` | ARCH · GS · GOV · PROJ · GRID · CONN |
| `Authority` | CANON · DERIVED · DRAFT |
| `Definition` | one or two sentences — what it *is* |
| `Purpose` | what it's *for* |
| `JNL` | its own JNL address (identity) |
| `Related` | JNL addresses of related objects |
| `Tags` | semantic tags |
| `ReferenceMap` | tokens resolving to locations via JNL → LAL |

### ReferenceMap tokens

Instead of storing paths, JD stores tokens that LAL resolves:

| Token | Resolves to |
|-------|-------------|
| `PRI`   | primary definition object |
| `SPEC`  | specification(s) |
| `PATCH` | patch history |
| `IDX`   | IndexSummary in LAL |

---

## Canonical form (on-disk)

JD entries live in `yggdrasil/jd/entries/` as one file per entry, named by JNS:
`<JNL>.md` (e.g. `ARCH-JFS-CORE-0001.md`). Front-matter carries the structured fields so
both a human and a parser can read them:

```markdown
---
name: JFS
type: ARCH
authority: CANON
jnl: ARCH-JFS-CORE-0001
related: [ARCH-JNS-CORE-0001, ARCH-JNL-CORE-0001, ARCH-JSL-CORE-0001, ARCH-JMS-CORE-0001]
tags: [filesystem, core, architecture]
ref: [PRI, SPEC, PATCH, IDX]
---

**Definition:** Filesystem kernel providing naming, identity, structure, and mirroring.

**Purpose:** Gives every persistent object a deterministic name, address, structure, and
mirror so growth increases organization rather than complexity.
```

A human can read it. Claude can read it. GPT can read it. A parser can read it. And
there is almost no duplication.

---

## Why this is efficient

Instead of JD holding `{Summary, Mirror, Path, Description, FileList, References, Links}`
for every entry, it holds `{Definition, JNL}` and lets the chain resolve the rest. JD is
becoming less a dictionary and more a **semantic DNS**: definition + identity +
authority + routing hints, with retrieval delegated downstream. That is the most
storage-efficient and model-efficient form JD can take without losing usefulness — and
it is what keeps the dictionary readable as the system grows to thousands of entries.

The highest-leverage move is never "add more summaries." It is "make JNL powerful enough
that summaries only need to point to identities."
