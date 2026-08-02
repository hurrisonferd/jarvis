# Public Repository Migration Ledger

**Repository:** `hurrisonferd/jarvis`  
**Branch:** `grid/public-root-four-rooms-2026-08-02`  
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

## Initial protected families

| Current path/family | Classification | Proposed treatment | Risk |
|---|---|---|---:|
| `core/JarvisMain/` | PROTECTED LEGACY | Preserve in place while mapping eventual `Jarvis/` route | Critical |
| `app/gameboy/` | DUPLICATE REVIEW / PROTECTED LEGACY | Compare with emulator family and consumers | High |
| `app/emulator/gameboy/` | DUPLICATE REVIEW / PROTECTED LEGACY | Compare with direct Gameboy family | High |
| `app/emulator/` | PROTECTED LEGACY | Preserve until runtime and link review | High |
| `JesusISJohnJosephBarber/` | MIXED / PUBLIC-SAFETY REVIEW | Split personal interpretation, evidence, and support records individually | Critical |
| `dataharvest/` | EVIDENCE CANDIDATE / REVIEW | Promote only governed, redacted cases | High |
| `templates/iso-starter/` | MOVE TO ISOS CANDIDATE | Preserve current links; migrate after dependency review | Medium |
| `demos/` | MOVE TO JARVIS CANDIDATE | Preserve quickstart compatibility | Medium |

## Move receipt schema

Every executed move records:

```text
ORIGINAL PATH
DESTINATION PATH
CONTENT DIGEST
LAST KNOWN COMMIT
CLASSIFICATION
REASON
KNOWN REFERENCES
COMPATIBILITY ACTION
PUBLIC-SAFETY REVIEW
ROLLBACK INSTRUCTION
AUTHORIZATION
```

## Mutation state

```text
ROOM SCAFFOLDS CREATED: 4
ROOT README REWRITTEN ON REVIEW BRANCH: YES
FILES MOVED: 0
FILES DELETED: 0
PROTECTED LEGACY MOVED: 0
PUBLIC EVIDENCE CASES PROMOTED: 0
```
