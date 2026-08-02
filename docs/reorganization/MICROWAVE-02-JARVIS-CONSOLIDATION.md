# Microwave 02 — JARVIS Consolidation

**Branch:** `grid/public-root-four-rooms-2026-08-02`  
**Status:** ACTIVE / BOUNDED MIGRATION DESIGN  
**Authority:** Raven  
**Execution:** ERIS

## Objective

Make `Jarvis/` the primary engineering room without breaking protected legacy anchors, workflows, imports, hosted pages, or public URLs.

## Protected anchors

- `core/JarvisMain/`
- Gameboy surfaces
- emulator and RetroArch surfaces
- BootOS
- MusicOS and MusicOSPortable
- Yggdrasil and Jarvis Dictionary
- active public memory and provenance routes

Protected means no blind movement, flattening, or deletion.

## Current route families

| Family | Current route | Classification |
|---|---|---|
| Core architecture | `core/JarvisMain/` | PROTECTED LEGACY ANCHOR |
| Demos | `demos/` | MOVE CANDIDATE WITH WORKFLOW REPAIR |
| ISO starter | `templates/iso-starter/` | ROUTE TO `ISOs/`, NOT `Jarvis/` |
| Public docs/hosted interface | `docs/` | HOSTING DEPENDENCY REVIEW |
| Runtime | `runtime/` | TARGETED CONSOLIDATION REVIEW |
| Application surfaces | `app/`, `Jarvis/`, `JarvisSide/` | OVERLAP REVIEW |
| Operations | `operations/` | ACTIVE IMPLEMENTATION / KEEP UNTIL DEPENDENCIES MAPPED |
| Public memory | `memory/` | SPLIT REVIEW: ENGINEERING, PERSONAL, ARCHIVE, SENSITIVE |

## Movement law

A path may enter `Jarvis/` only when:

1. its current role is known;
2. inbound references are reviewed;
3. secrets and personal data are excluded;
4. destination is unambiguous;
5. public links or imports receive compatibility handling;
6. original and destination digests are recorded;
7. rollback is documented.

## First low-risk outputs

- authored `Jarvis/START-HERE.md`;
- compatibility route table;
- public inclusion/exclusion boundary;
- explicit preservation law for `core/JarvisMain/`.

## Blocked bulk moves

The following remain blocked until exact tree and dependency evidence is sufficient:

- moving all of `core/`;
- merging Gameboy copies;
- consolidating emulator/RetroArch;
- relocating GitHub Pages assets;
- moving demos before workflow path updates;
- moving `templates/iso-starter/` before ISO validator and quickstart updates;
- moving raw `memory/` or Jorm exports.

## Mutation receipt

```text
FILES MOVED: 0
FILES DELETED: 0
PROTECTED PATHS MODIFIED: 0
PUBLIC GUIDE FILES ADDED: 1
```

This microwave remains active until route families have bounded move manifests or explicit keep-in-place decisions.
