---
memory_tier: JSTM
grade: system
---

# JIP-FMT-0001 — JFS Formatting Standard (IDs · tags · status · routing)

**JNL:** `IMPL-FMT-SPEC-0001` · **class:** SPEC · **tier:** MAIN · **status:** ACTIVE

The single source of truth for how every JFS object is identified, named, tagged, statused,
and routed — so the connector can upload JGPP/JIP/JD entries and the system auto-sorts,
mirrors, and serves them queryably. This reconciles the GPT formalization packets with the
system already built; where a packet reinvents something we have, the existing name wins.

## 1. One identity, not two

A persistent object has **exactly one identity: its JNL.** It is globally unique, stable
across relocation (JMS), and is the only valid cross-system reference key.

> **Rejected:** a separate "JD-ID" + "JNL-ID" split. Two parallel ID systems reintroduce the
> ambiguity JFS exists to remove. The JNL *is* the semantic identity; **tags** are the
> navigation layer; the **filename** is the human form. Don't merge them, don't duplicate them.

| Layer | Role | Mechanism |
|-------|------|-----------|
| Identity | what it *is* + where | **JNL** (`[Domain]-[System]-[Type]-[Log]-[Patch]-[Block]`) |
| Navigation | how it's *found* | **tags** + LAL tag-registry |
| Storage | how it's *stored* | **filename** (JNS) |
| Lifecycle | what *state* it's in | **JSS status** |
| History | what *happened* | event log (`dex_events`, JATM) |

## 2. The cognition-pipeline types (the new capability)

`JGPP` / `JIP` / `JD` are first-class **types**, usable on any object — especially per project:

```
PROJ-DEO-JGPP-0001   Deoxys exploration  (mutable hypothesis)   → class ENTITY
PROJ-DEO-JIP-0001    Deoxys commit       (validated change)     → class SPEC
PROJ-DEO-JD-0001     Deoxys truth        (canonical definition)  → class SPEC
PROJ-DEO-BIO-0001    Deoxys project bio                          → class SYSTEM
```

The governed transition is `JGPP → JIP → JD` (exploration → commit → truth), enforced by the
connector tiers (propose/draft/approve). `JGPP` can never become canon directly — only a
`JIP` promotes to `JD`. This is the JER/JCPRS flow, realized by the dex.

## 3. Filename (JNS)

`<Subject><Type>-<NNNN>-<MMDDYY>` for substrate/core; for **project artifacts** add the
project prefix: `<PROJECT><TYPE>-<MMDDYY>-<NNNN>-<SUBJECT>.md`
(e.g. `DEOXYSJIP-060926-0001-TELEMETRY-PIPELINE.md`). The filename's sequence matches the
JNL `Log`; JMS preserves both across moves. Filenames are human/JNS form — the JNL is the
machine identity, and they agree.

## 4. Headless — current state is a query

No HEAD pointers, no `CURRENT.md`. "Current" is **`status = ACTIVE`**, resolved by query
(`jd_list status=ACTIVE`). This is already how the dex works; the packets converge to it too.

## 5. Routing / mirroring / retrieval (already live)

| Packet concept | Realized by |
|---|---|
| Auto-routing by status | **JSS + `autosort.py`** (status decides the subfolder) |
| Mirroring | **JMS** (files=truth, Supabase + LAL = pointer mirrors) |
| Registry / index | **LAL** (`address-registry` / `master-index` / `tag-registry`) |
| Query engine (JQE) | dex **READ** tools + **JQL** (`IMPL-JQL-CORE-0001`) |
| Execution runtime (JER) | dex **PROPOSE/DRAFT/COMMIT/OVERRIDE** tiers (`IMPL-DEX-SPEC-0001`) |
| Graph (VERSION_GRAPH) | `lal/graph.json` (**YVG**) |

## 6. Connector usage (the goal)

```
jd_propose {name, domain:"PROJ", system:"DEO", type:"JGPP", definition, purpose, tags}
   → auto: JNL PROJ-DEO-JGPP-0001, class ENTITY, tier SIDE, status TASK, timestamps
   → staged in jd_proposals; Raven jd_approve → ACTIVE → reconciled to file
```

Upload meaning; the connector derives identity, class, tier, routing, and the file. That is
the whole point: **autonomy proposes in perfect JFS hygiene; Raven commits.**

## 7. Follow-ups — closed 2026-06-09
- Move `yggdrasil/` into `core/JarvisMain/` — **done** (`core/JarvisMain/yggdrasil/`; tool root-paths, CI, specs updated).
- Per-project folder scaffold under `JarvisSide/Projects/<P>/` (`JGPP/ JIP/ JD/ BIO/`) — **done**,
  plus the intake layer: `tools/new.py` mints JNL + formatted file in one command, and `seed.py`
  adopts any drop-in file that declares its own frontmatter (`jnl`/`name`/`type`/`status`/`tags`).
  Project codes live in `jfs/project-codes.json`. Flat folders; ARCHIVED/DEPRECATED auto-sort to
  `JarvisSide/Archive/<Project>/`.
