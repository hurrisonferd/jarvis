---
memory_tier: JHTM
grade: system
---

# Hygiene Packets — Archived Reference (0001, 06/09/26)

**JNL:** `IMPL-HYG-SPEC-0001` · **tier:** SIDE · **status:** ARCHIVED · **class:** SPEC

Eight GPT-authored architecture packets submitted by Raven for governance review on
2026-06-09. Archived here for later mining. **These are proposals, not canon** — canon is
what's merged to main and addressed in the dex. Per-packet verdict below.

## Verdicts (governance pass)

| # | Packet | Verdict | Disposition |
|---|--------|---------|-------------|
| 1 | Ontology & Repository Hygiene Spec | Partial adopt | Object **classes** (System/Spec/Module/Entity/Event/Registry) → adopted as the JD `class` field. Its `/systems /specs …` folder scheme **rejected** (conflicts with the Capitalized/lowercase reorg). |
| 2 | File Formatting Standard | Partial adopt | JD front-matter already covers it; stole `owner` + `references` fields. Full YAML-section mandate rejected (GL7 verbosity). |
| 3 | JFS Validator Engine (JVE) | Already have | `yggdrasil/tools/validate.py` **is** the JVE. Added redundancy/overlap detection (overlap_score Gold Law). |
| 4 | Yggdrasil Visual Graph (YVG) | Adopt (data layer) | Built `tools/graph_export.py` → `lal/graph.json` (nodes+edges). Interactive UI deferred. |
| 5 | JY-UR Unified Runtime | Invariant only | Recorded the four-views invariant in `Architecture/canon.md`. No new system (loop already exists: GL10 + JCS). |
| 6 | IndexSummary System (ISS) | Already have | `lal/master-index.json` **is** the ISS. |
| 7 | Conceptual Map (Raven origin) | Reject — drift | Renamed JFS→"Frame System", JNL→"Journal Layer". Contradicts committed canon. Rejected. |
| 8 | Folder Structure (CORE/MEMORY/…) | Reject as folders | A third tree-pivot = churn (GL7/GL10). Its functional axis is captured by `class` + tags + the MAIN/SIDE tier. |

## Adopted net

- JD `class` (SYSTEM/SPEC/MODULE/ENTITY/EVENT/REGISTRY), `tier` (MAIN/SIDE), `owner`, `references`.
- `validate.py` = **JVE**; `lal/master-index.json` = **ISS**; `graph_export.py` = **YVG** data layer.
- Redundancy detection in the validator.
- JY-UR invariant recorded in canon.

## Packet contents (condensed, faithful)

**1. Ontology** — Object classes: System, Spec, Module, Entity, Event, Registry Entry.
Containment: System ⊃ {Spec, Module, Entity, Registry, Event}. Yggdrasil = semantic tree
graph (no orphans, no duplicate canon, cross-links allowed not duplication). Cross-ref form
`[TYPE:NAME]`. Versioning vMAJOR.MINOR.PATCH for Specs/Modules only. Compression: merge
overlapping specs, prefer fewer high-quality systems.

**2. File Formatting** — YAML header (id/type/name/version/status/owner/references/tags) +
sections (Header/Interface/Logic/Dependencies/Events/Notes). Determinism rule: "if a human
cannot reconstruct behavior from the file alone, the file is invalid." Single responsibility
per file; no multi-type files.

**3. JVE** — Validation pipeline INGEST→PARSE→CLASSIFY→VALIDATE→GRAPH CHECK→REPORT. Hard
fails: invalid schema, unresolved ref, type mixing, EVENT mutation. Soft warns: redundant
module, overlapping spec, oversized module. Modes: STRICT/DEV/AUDIT.

**4. YVG** — Directed labeled graph; node types SYSTEM/SPEC/MODULE/ENTITY/EVENT/REGISTRY;
edge types depends_on/implements/references/emits/governs. Layered layout (governance top,
history bottom). Modes: Structural/Execution/Evolution. Progressive disclosure; clustering
+ meta-nodes for scale.

**5. JY-UR** — Single loop: FILE→VALIDATE→GRAPH UPDATE→RUNTIME→EVENT→GRAPH SYNC. Every
artifact is simultaneously file/node/runtime-participant/history-trace. Invariant: files=truth,
graph=structure, runtime=behavior, events=history — all must agree.

**6. ISS** — Compressed semantic index above JFS+Yggdrasil. Index levels 0–3 (system/domain/
module/entity). Derived, never authoritative. "A lens, not a layer of truth."

**7. Conceptual Map** — Raven as origin node; JFS/Yggdrasil/JNL-JD branches. NOTE: drift —
relabels JFS and JNL incorrectly. Visualization narrative only.

**8. Folder Structure** — Proposed CORE/MEMORY/REGISTRY/EXECUTION/GOVERNANCE/EXPLORATION/
PIPELINES/INTERFACES/PROJECTS. One-way dependency rules. Rejected as physical layout;
retained as a conceptual/functional view.
