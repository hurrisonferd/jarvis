# MusicOS — Active Knowledge

This folder is the curated home for the currently active **MusicOS — The Wizard** knowledge pack.

```text
ACTIVE = CURRENT GPT KNOWLEDGE SURFACE
OUTSIDE ACTIVE = LINEAGE / LEGACY / OTHER SOURCE MATERIAL
MANIFEST = EXACT UPLOAD CONTRACT
```

## Current state

The mega atomic migration is complete.

- All 16 active cartridges live directly in `knowledge/Active/`.
- `README.md` documents the shelf and is not an upload cartridge.
- `../KNOWLEDGE-MANIFEST.json` is the exact ordered upload contract.
- Active cartridge content was moved byte-for-byte; migration changed location, not cartridge semantics.
- Material outside `Active/` is not automatically part of the current GPT knowledge surface.

## Change law

Do not move, add, retire, or rename active cartridges piecemeal.

A shelf change must update in the same bounded migration:

```text
FILES
+ KNOWLEDGE MANIFEST
+ BUILDER HANDOFF
+ TEST PATHS
+ RETRIEVAL CONSUMERS
```

> **Keep the active shelf obvious. Preserve lineage outside it.**
