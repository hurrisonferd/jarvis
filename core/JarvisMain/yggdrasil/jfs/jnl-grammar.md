---
memory_tier: JLTM
grade: system
---

# JNL Grammar — Jarvis Navigation Language

**JNL:** `ARCH-JNL-CORE-0001`
**Authority:** Canonical
**Purpose:** A deterministic, machine-readable and human-readable addressing system for
every persistent object within JARVIS.

JNL answers **"where is this?"**. It is the global identity of an object — stable across
relocation (JMS preserves it), unique repository-wide, and parseable by any agent.

---

## Format

```
[Domain]-[System]-[Type]-[Log]-[Patch]-[Block]
```

- **Canonical short form** (stable, single-object definitions): `Domain-System-Type-Log`
  → `ARCH-JFS-CORE-0001`
- **Full form** (granular log/patch objects): all six segments
  → `GS-ODN-RT-0001-P005-B002`

A parser reads left-to-right, widest scope first. Missing trailing segments mean
"the whole thing" (a CORE log with no `-P###` addresses the canonical object, not a patch).

### Segment rules

| Segment | Form | Meaning |
|---------|------|---------|
| Domain | 2–4 UPPER | top-level realm (see table) |
| System | 2–4 UPPER | the system/primitive (see table) |
| Type | 2–5 UPPER | kind of object (see table) |
| Log | `NNNN` | 4-digit zero-padded log number |
| Patch | `P###` | optional — patch number within the log |
| Block | `B###` | optional — block within the patch |

Regex (full): `^[A-Z]{2,4}-[A-Z0-9]{2,4}-[A-Z]{2,5}-\d{4}(-P\d{3}(-B\d{3})?)?$`

---

## Domain codes

| Code | Domain |
|------|--------|
| `GS`   | God Systems (the 27) |
| `ARCH` | Architecture — Yggdrasil/JFS substrate (JFS, JNS, JNL, JSL, JMS, JD, LAL) |
| `GOV`  | Governance — Gold Law, constraints, AEGIS policy |
| `PROJ` | Projects — Pachinko Bounce, CodeOS, etc. (each a node) |
| `GRID` | The Grid — federation, protocol, nodes |
| `CONN` | Connectors — MCP, Supabase, GitHub integration |
| `LOG`  | Records — sessions, decisions (PROMETHEUS), growth |

## Type codes

| Code | Type |
|------|------|
| `CORE`  | canonical core definition |
| `SPEC`  | specification |
| `PATCH` | patch / change record |
| `RT`    | routing definition |
| `IDX`   | index / summary |
| `REG`   | registry |
| `BIO`   | project bio |
| `LOG`   | log entry |

## System codes

**Substrate (ARCH domain):** `YGG` `JFS` `JNS` `JNL` `JSL` `JMS` `JD` `LAL`

**God Systems (GS domain) — 27, canonical, fixed:**

| Code | System | Code | System | Code | System |
|------|--------|------|--------|------|--------|
| `AYR` | AYRE | `BFR` | BIFROST | `ATL` | ATLAS |
| `AEG` | AEGIS | `HAL` | HALO | `HER` | HERMES |
| `ODN` | ODIN | `ATH` | ATHENA | `IRS` | IRIS |
| `KRN` | KRONOS | `NEM` | NEMESIS | `PRO` | PROMETHEUS |
| `SKD` | SKADI | `APO` | APOLLO | `ARG` | ARGUS |
| `MNE` | MNEMOS | `LOK` | LOKI | `JAN` | JANUS |
| `HUG` | HUGINN | `MER` | MERIDIAN | `ERI` | ERIS |
| `CHA` | CHAOS | `DAN` | DANTE | `ZEU` | ZEUS |
| | | | | `POS` | POSEIDON |
| | | | | `HAD` | HADES |
| | | | | `MIM` | MIMIR |

> The 27 are fixed. Do not redefine, renumber, or add (CLAUDE.md / GL constraint).
> The Rosetta of legacy names → canon: MIDAS→AEGIS, SENTINEL→ARGUS+IRIS+HUGINN,
> GRAVEYARD→HADES, FATES→KRONOS. JORMUNGANDR is a codec (not a system). HELP folds
> into MIMIR. CHAOS stays the entropy/drift system; raw ingestion is AYRE→HADES.

---

## Requirements (GL12)

Every persistent object must possess:

1. **JNL Address** — its unique identity (this grammar)
2. **Physical Location** — the path where truth lives
3. **Tag Set** — `#structural #semantic #coord #system #intent #risk #dependency`
4. **IndexSummary Reference** — its entry in LAL
5. **Mirror Reference** — pointers managed by JMS

Objects lacking a JNL address are **non-governed** and invisible to the loop.

## Benefits

Deterministic retrieval · human readable · machine parsable · expandable ·
repository-wide uniqueness. The address never changes when a file moves — JMS moves the
pointer, not the identity — so references never break as the tree grows.
