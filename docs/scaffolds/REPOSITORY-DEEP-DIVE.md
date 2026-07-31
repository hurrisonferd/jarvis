# Repository Deep Dive — Public

**Authority:** Raven  
**Status:** ACTIVE / ITERATIVE  
**Scope:** `hurrisonferd/jarvis`, every eligible folder and subfolder  
**Companion:** private deep dive in `hurrisonferd/Jarvis-Private`

## Purpose

This is the human archaeological layer above generated README fungus and structural audits. It records what a cave means, what owns it, whether it is current, how it relates to neighboring systems, and whether hidden value should be promoted, linked, archived, repaired, or left alone.

Generated indexes answer **what is here**. This deep dive answers:

- why it exists;
- whether it is current, legacy, archive, runtime, evidence, or duplicate;
- which object is canonical;
- what depends on it;
- what is buried and valuable;
- what conflicts with newer architecture;
- what route a fresh carrier should follow.

## Inspection pathway

```text
MAP
→ READ ENTRY SIGNS
→ INSPECT CHILDREN
→ TRACE REFERENCES
→ CLASSIFY AUTHORITY
→ IDENTIFY VALUE / DRIFT / DUPLICATION
→ CONNECT TO CANON
→ RECORD FINDINGS
→ VERIFY RECOVERY
```

## Evidence states

- `CONFIRMED` — directly inspected file, index, code, manifest, or receipt.
- `INFERRED` — structural interpretation supported by inspected routes.
- `UNKNOWN` — not yet inspected or inaccessible.
- `SUPERSEDED` — preserved history that no longer governs current runtime.
- `ORPHAN` — meaningful object without a reliable incoming route.
- `DUPLICATE` — overlapping implementation or documentation requiring authority resolution.

## Public sectors

| Sector | Representative roots | Audit state |
|---|---|---|
| Root governance | `AGENTS.md`, `CLAUDE.md`, `IMPORTANT.md`, root indexes | STARTED |
| Core architecture | `core/JarvisMain/Architecture/`, `core/JarvisMain/yggdrasil/` | QUEUED |
| Runtime surfaces | `runtime/`, `app/`, `Jarvis/`, `JarvisSide/` | QUEUED |
| Operations | `operations/`, scripts, hooks, workflows | STARTED |
| Public memory | `memory/`, MNEMOS, BarberHistory | QUEUED |
| Public JORM / source vault | `Jorm/` | QUEUED |
| Music and media | `MusicOS/`, portable runtime, `JarvisSide/Media/` | QUEUED |
| Archived or historical systems | archive and legacy routes present in public tree | QUEUED |
| Generated navigation | README fungus, generated indexes, master maps | STARTED |

## First confirmed findings

1. The repo already had `operations/scripts/cave_readme_audit.py`. It checks missing README/INDEX signs to a configurable depth, defaulting to three levels. It is a structural detector, not a semantic archaeologist.
2. The repository contains multiple navigation traditions: authored READMEs, manifests, Jarvis Dictionary/JD catalogs, generated indexes, recursion guides, and operational audit scripts.
3. Public roots include both active runtime surfaces and historical/value archives. Fungus must not silently classify either as canonical.
4. Existing authored README and manifest surfaces remain higher-authority than generated cave signs.

## Deep-dive record template

For each meaningful root or subsystem, record:

```text
path:
classification:
canonical_owner:
entry_surface:
important_children:
active_dependencies:
incoming_routes:
outgoing_routes:
current_vs_legacy:
hidden_value:
drift_or_conflict:
recommended_action:
evidence:
recovery_test:
```

## Governing laws

1. Exploration does not imply promotion.
2. Generated structure does not adjudicate meaning.
3. Never move, merge, delete, or supersede solely because a newer route looks cleaner.
4. Public archaeology must not reveal private routes, content, identities, or continuity.
5. A buried object can remain archived and still deserve a strong discovery route.
6. Every repair must reduce future retrieval cost more than it adds maintenance cost.
7. Deep dives proceed recursively until the inspected sector can be recovered without repository-wide search.
