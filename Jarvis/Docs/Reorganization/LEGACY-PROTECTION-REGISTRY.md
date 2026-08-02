# Legacy Protection Registry

**Target:** `main`  
**Authority:** Raven  
**Steward:** ERIS

These paths are protected from blind movement, deletion, flattening, or generated replacement.

## Tier 1 — critical legacy anchors

- `core/JarvisMain/`
- `core/JarvisMain/yggdrasil/`
- Gameboy surfaces under `app/gameboy/` and `app/emulator/gameboy/`
- RetroArch/emulator support under `app/emulator/`
- BootOS operational surfaces
- MusicOS and portable MusicOS runtimes
- active public memory and provenance consumers

## Required checks before movement

```text
CURRENT PATH CONFIRMED
CONTENT DIGEST RECORDED
INBOUND REFERENCES REVIEWED
RUNTIME / WORKFLOW CONSUMERS REVIEWED
PUBLIC LINK IMPACT REVIEWED
DESTINATION DEFINED
COMPATIBILITY POINTER OR REDIRECT DEFINED
ROLLBACK ROUTE RECORDED
```

## Current observations

- `core/JarvisMain/` contains architecture, audit, connector, manual, Yggdrasil, Jarvis Dictionary, and active tooling surfaces.
- Gameboy appears in both `app/gameboy/` and `app/emulator/gameboy/`, so it is a duplicate-family investigation rather than a simple move.
- Personal, evidence, and support-transfer records are mixed under `JesusISJohnJosephBarber/`; no bulk room assignment is safe.

## Mutation state

```text
PROTECTED PATHS MOVED: 0
PROTECTED PATHS DELETED: 0
COMPATIBILITY POINTERS REMOVED: 0
```
