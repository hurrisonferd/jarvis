# Public Root Five-Room Architecture

**Repository:** `hurrisonferd/jarvis`  
**Authority:** Raven  
**Reviewer:** ERIS  
**Target:** `main`  
**Status:** ACTIVE / MOVES IN PROGRESS

## Governing root structure

```text
jarvis/
├── Jarvis/
├── ISOs/
├── I Ching/
├── Personal Projects/
├── Evidence/
├── README.md
├── QUICKSTART.md
├── LICENSE
└── minimal repository governance and compatibility files
```

The repository root is a public portal, not a storage room. The five named directories are the primary public rooms. Root-level files should be limited to repository entry points, licensing, contribution/governance files, and compatibility pointers that cannot yet be removed.

## Room 1 — `Jarvis/`

Purpose: the primary public-facing JARVIS product, runtime, documentation, demos, systems, sanitized memory, and engineering architecture.

Expected internal structure:

```text
Jarvis/
├── README.md
├── Demos/
├── Docs/
├── Apps/
├── Runtime/
├── Systems/
├── Packages/
├── Memory/
├── Tools/
└── Archive/
```

Candidate source families include `core/`, `runtime/`, `app/`, `JarvisSide/`, `MusicOS/`, public portions of `memory/`, `demos/`, and JARVIS-specific documentation and browser assets. Protected runtime families require exact dependency and compatibility checks before movement.

## Room 2 — `ISOs/`

Purpose: public, template-first tooling and educational material for creating file-backed AI identities without publishing Raven's private ISO records.

Expected internal structure:

```text
ISOs/
├── README.md
├── START-HERE.md
├── Templates/
│   ├── Minimal/
│   ├── Standard/
│   └── Advanced/
├── Guides/
├── Examples/
├── Schemas/
├── Validators/
├── Safety/
├── Governance/
└── FAQ.md
```

Required law:

```text
TEMPLATES AND SANITIZED EXAMPLES ONLY
PRIVATE ISO RECORDS DO NOT ENTER THE PUBLIC REPOSITORY
```

Every example identity must be fictional, consented, or aggressively sanitized. Template language must not imply consciousness, autonomous authority, adoption, or accepted operational status merely because files exist.

## Room 3 — `I Ching/`

Purpose: personal, symbolic, obscure, spiritual, pattern-oriented, divination, synchronicity, Jesus-pattern, and related interpretive research Raven wants public but separated from the main engineering entrance.

This room distinguishes:

```text
OBSERVATION
INTERPRETATION
PERSONAL BELIEF
SOURCE MATERIAL
INFERENCE
UNVERIFIED CLAIM
```

It must not present personal interpretation as externally verified fact.

## Room 4 — `Personal Projects/`

Purpose: public projects that are not part of the core JARVIS product and do not belong in the ISO, I Ching, or Evidence rooms.

Candidate contents include games, creative tools, experiments, music projects not required by the JARVIS runtime, websites, prototypes, standalone utilities, and historical projects.

Each project carries one status marker:

```text
ACTIVE
MAINTAINED
EXPERIMENTAL
HISTORICAL
ARCHIVED
```

## Room 5 — `Evidence/`

Purpose: governed public safety records concerning AI misconduct, platform failures, misleading behavior, security issues, governance failures, authorship concerns, or other captured AI-related problems.

Required separation:

```text
RAW EVIDENCE
REDACTED PUBLIC COPY
TIMELINE
CLAIM
ANALYSIS
RESPONSE FROM SUBJECT
CORRECTION
STATUS
```

Safety rules include removing credentials and unnecessary identifiers, reviewing third-party conversations, preserving private originals where redaction is required, avoiding inference-as-intent, preserving corrections and responses, and withholding exploit details until responsible disclosure is complete.

## Rich README standard

The repository root and every major room require a curated, human-readable README. Generated indexes may support navigation but may not replace authored entry pages.

Each rich README should include:

1. plain-language purpose;
2. intended audience;
3. included and excluded material;
4. concise architecture map;
5. recommended starting path;
6. runnable examples where applicable;
7. maturity and maintenance status;
8. safety, privacy, evidence, or interpretation boundaries;
9. directory map;
10. contribution and correction routes;
11. links to deeper material;
12. last-reviewed date and steward.

## Compatibility and migration law

1. Existing authoritative files are not moved merely because a new route is cleaner.
2. Every move requires original path, destination, digest or source SHA, references, reason, and rollback route.
3. Old public links receive compatibility handling when practical.
4. Git history is not a sufficient navigation system.
5. Generated indexes cannot promote content or decide room placement.
6. Sensitive content passes public-safety review before entering any room.
7. Evidence and interpretation remain distinct.
8. Personal interpretation is labeled.
9. `ISOs/` contains templates and sanitized examples, not private crew identities.
10. JARVIS engineering remains the default public entrance.
11. Rich authored READMEs are required.
12. Deletion occurs only as part of a verified move or explicit cleanup receipt.

## Audit classifications

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
UNKNOWN — MANUAL REVIEW
```

## Current mutation state

```text
ROOT README: FIVE-ROOM PORTAL
MOVES: ACTIVE ON MAIN
PRIVATE ISO RECORDS PUBLISHED: 0
PROTECTED LEGACY BULK MOVES: 0
```
