---
name: Jarvis Dictionary Semantic Pokedex v2
type: SPEC
class: SPEC
tier: MAIN
authority: CANON
owner: JFS
steward: MIMIR
parent: ARCH-JD-CORE-0001
jnl: ARCH-JD-SPEC-0002
seq: 2
status: ACTIVE
created: 2026-07-28
updated: 2026-07-28
source: core/JarvisMain/yggdrasil/jd/JD-V2-SPEC.md
related: [ARCH-JD-CORE-0001, ARCH-JSE-SPEC-0001, ARCH-JNL-CORE-0001, ARCH-LAL-CORE-0001]
references: [core/JarvisMain/yggdrasil/jd/catalog/CATEGORY-REGISTRY.json, core/JarvisMain/yggdrasil/jd/catalog/RELATIONSHIP-ONTOLOGY.json, core/JarvisMain/yggdrasil/jd/tools/build_semantic_catalog.py]
tags: [dictionary, pokedex, semantics, catalog, provenance, graph, human-readable, machine-readable]
aliases: [JD v2, semantic pokedex, jarvis pokedex]
ref: [PRI, SPEC, IDX]
memory_tier: JLTM
---

# JD v2 — Semantic Pokédex

**Definition:** JD v2 is the richer human-and-machine-readable view of the Jarvis Dictionary: one permanent identity per governed concept, presented as a concise Pokédex card and indexed as a semantic graph.

**Purpose:** Make every project, person, ISO, AI system, OS, engine, module, law, protocol, artifact, event, and concept resolvable without repeatedly reconstructing its meaning from scattered files.

## Identity stack

```text
JID  → stable human numerical shelf key
JNL  → immutable semantic identity
JD   → meaning, classification, relationships, and routing
LAL  → current location
JORM → provenance, history, correction, and receipts
```

A display name may evolve. A route may move. The JID and JNL preserve continuity.

## Required entry layers

Every JD v2 entry has two synchronized faces.

### Machine face

- stable identifiers: JID when assigned, JNL always;
- canonical and alternate names;
- category and subcategory;
- system/domain/class/status;
- owner and steward;
- tags and search terms;
- typed relationships;
- canonical, source, public, memory, and evidence routes;
- field-level provenance and confidence;
- source digest and curation status.

### Human face

- Pokédex summary;
- what it is;
- why it matters;
- signature role or capability;
- relationships;
- lineage and aliases;
- routes and receipts;
- unresolved questions or collision warnings.

## Category law

Categories describe what an object is. Tags describe how it behaves, where it participates, and how it can be found. A category must not be used as a substitute for identity.

Canonical top-level categories are maintained in `catalog/CATEGORY-REGISTRY.json`.

## Relationship law

Relationships are directed typed edges, not prose-only implications.

```text
ATOM --AUDITS--> PRIDE
LILITH --COORDINATES_WITH--> AYRE
MusicOS --PART_OF--> SimOS
JORM --PRESERVES--> identity history
```

Canonical edge types are maintained in `catalog/RELATIONSHIP-ONTOLOGY.json`.

## Provenance law

Every semantic claim must say where it came from.

```text
CURATED       → explicitly authored or approved
EXTRACTED     → read directly from governed metadata or body text
INFERRED      → deterministic classification from names, tags, paths, or JNL
UNKNOWN       → unresolved; never silently filled
```

Inferred values remain revisable. Curated values override inference but never delete the inference receipt.

## Discovery law

The catalog builder may discover possible objects across the repository, but it must not silently mint JIDs, JNLs, canon status, relationships, or identity claims.

```text
repository evidence
→ candidate
→ duplicate/match inspection
→ Raven or governed approval
→ mint or link
→ JORM receipt
```

## Storage law

JD remains efficient by storing meaning and routes rather than copying entire source files. Richness comes from structured links, typed relationships, provenance, and compact human summaries—not uncontrolled duplication.

## ATOM audit requirements

A valid build reports:

- duplicate JNLs;
- alias collisions;
- missing required JSE fields;
- broken source routes;
- unknown categories;
- unresolved relationship targets;
- candidates not yet represented in JD;
- conflicting names or reused numerical JIDs;
- schema/documentation inconsistencies.

No failed invariant may be hidden merely to produce a clean score.
