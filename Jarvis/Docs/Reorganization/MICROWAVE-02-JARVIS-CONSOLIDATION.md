# Microwave 02 — JARVIS Consolidation

**Target:** `main`  
**Status:** ACTIVE / BOUNDED MIGRATION  
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

## Route families

| Family | Current route | Classification |
|---|---|---|
| Core architecture | `core/JarvisMain/` | PROTECTED LEGACY ANCHOR |
| Demos | `Jarvis/Demos/` plus remaining legacy demo families | ACTIVE CONSOLIDATION |
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

## Completed low-risk outputs

- authored `Jarvis/START-HERE.md`;
- compatibility route table;
- public inclusion/exclusion boundary;
- explicit preservation law for `core/JarvisMain/`;
- migration of the persistent-memory demo into `Jarvis/Demos/`;
- migration of reorganization governance into `Jarvis/Docs/Reorganization/`.

## Blocked bulk moves

The following remain blocked until exact dependency evidence is sufficient:

- moving all of `core/`;
- merging Gameboy copies;
- consolidating emulator/RetroArch;
- relocating GitHub Pages assets;
- moving `templates/iso-starter/` before validator and quickstart updates;
- moving raw `memory/` or Jorm exports.

## Mutation receipt

```text
TARGET: MAIN
PROTECTED PATHS MODIFIED: 0
BOUNDED MOVES: ACTIVE
```
