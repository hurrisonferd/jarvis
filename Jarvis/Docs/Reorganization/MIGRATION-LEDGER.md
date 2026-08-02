# Public Repository Migration Ledger

**Repository:** `hurrisonferd/jarvis`  
**Target:** `main`  
**Authority:** Raven  
**Steward:** ERIS

## Target rooms

```text
Jarvis/
ISOs/
I Ching/
Personal Projects/
Evidence/
```

## Classification vocabulary

```text
KEEP AT ROOT
MOVE TO JARVIS
MOVE TO ISOS
MOVE TO I CHING
MOVE TO PERSONAL PROJECTS
MOVE TO EVIDENCE
ARCHIVE WITHIN ROOM
COMPATIBILITY POINTER REQUIRED
PUBLIC-SAFETY REVIEW REQUIRED
DUPLICATE REVIEW
GENERATED ARTIFACT
PROTECTED LEGACY
UNKNOWN — MANUAL REVIEW
```

## Protected families

| Current path/family | Classification | Treatment | Risk |
|---|---|---|---:|
| `core/JarvisMain/` | PROTECTED LEGACY | Preserve until full dependency map exists | Critical |
| `app/gameboy/` | DUPLICATE REVIEW / PROTECTED LEGACY | Compare with emulator family and consumers | High |
| `app/emulator/gameboy/` | DUPLICATE REVIEW / PROTECTED LEGACY | Compare with direct Gameboy family | High |
| `app/emulator/` | PROTECTED LEGACY | Preserve until runtime and link review | High |
| `JesusISJohnJosephBarber/` | MIXED / PUBLIC-SAFETY REVIEW | Split personal interpretation and evidence individually | Critical |
| `dataharvest/` | EVIDENCE CANDIDATE / REVIEW | Promote only governed, redacted cases | High |
| `templates/iso-starter/` | MOVE TO ISOS CANDIDATE | Move only after every validator, fixture, workflow, and reference is mapped | Medium |
| `demos/02-sat-remote-launcher/` | MOVE TO JARVIS CANDIDATE | Move as one complete receipted unit after all files and workflows are resolved | Medium |

## Executed moves

### MOVE-20260802-001 — persistent-memory demo

```text
ORIGINAL PATHS:
- demos/01-persistent-memory/README.md
- demos/01-persistent-memory/demo.py

DESTINATION PATHS:
- Jarvis/Demos/01-persistent-memory/README.md
- Jarvis/Demos/01-persistent-memory/demo.py

CLASSIFICATION: MOVE TO JARVIS
REFERENCES UPDATED:
- README.md
- QUICKSTART.md
- DEMOS.md
- .github/workflows/public-demos.yml
- Jarvis/START-HERE.md

ROLLBACK:
Restore the two source files from Git history and reverse the five path updates.

AUTHORIZATION: Raven direct-main consolidation
STATUS: COMPLETE
```

### MOVE-20260802-002 — reorganization governance

```text
ORIGINAL FAMILY:
- docs/reorganization/

DESTINATION FAMILY:
- Jarvis/Docs/Reorganization/

FILES:
- LEGACY-PROTECTION-REGISTRY.md
- MICROWAVE-01-PUBLIC-SHELL-AND-NAVIGATION.md
- MICROWAVE-02-JARVIS-CONSOLIDATION.md
- MIGRATION-LEDGER.md
- PUBLIC-ROOT-FOUR-ROOMS-ARCHITECTURE.md
- PUBLIC-SOURCE-ROUTING-MATRIX.md

CLASSIFICATION: MOVE TO JARVIS
REFERENCES UPDATED:
- README.md
- Jarvis/README.md

ROLLBACK:
Restore the six source files from Git history and reverse the two navigation updates.

AUTHORIZATION: Raven direct-main consolidation
STATUS: COMPLETE
SOURCE FAMILY REMOVED: YES
```

## Mutation state

```text
TARGET ROOMS PRESENT: 5
DIRECT MAIN MODE: ACTIVE
FILES COPIED TO ROOMS: 8
LEGACY FILES REMOVED: 8
COMPLETE SUBFAMILIES MOVED: persistent-memory demo; reorganization governance
PROTECTED LEGACY MOVED: 0
PUBLIC EVIDENCE CASES PROMOTED: 0
FULL ROOT CONSOLIDATION: INCOMPLETE
```
