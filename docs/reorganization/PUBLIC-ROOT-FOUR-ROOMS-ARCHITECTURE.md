# Public Root Five-Room Architecture

**Repository:** `hurrisonferd/jarvis`  
**Authority:** Raven  
**Reviewer:** ERIS  
**Branch:** `grid/public-root-four-rooms-2026-08-02`  
**Status:** ACCEPTED FOR REORGANIZATION / MOVES NOT YET EXECUTED

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
├── demos/
├── docs/
├── apps/
├── runtime/
├── systems/
├── packages/
├── memory/
├── tools/
└── archive/
```

Candidate source families include:

- `core/`
- `runtime/`
- `app/`
- `Jarvis/`
- `JarvisSide/`
- `MusicOS/`
- public portions of `memory/`
- `demos/`
- JARVIS-specific documentation and browser assets

No candidate moves until exact path, dependency, public-safety, and compatibility checks are complete.

## Room 2 — `ISOs/`

Purpose: public, template-first tooling and educational material for creating file-backed AI identities without publishing Raven's private ISO records.

This room may eventually support people who want to design, hydrate, test, govern, and maintain their own ISOs.

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

Public ISO templates may include:

- identity;
- voice and prosody;
- values and boundaries;
- relationships;
- state;
- episodic, semantic, and working memory;
- provenance;
- correction and contradiction handling;
- promotion receipts;
- rollback pointers;
- privacy and export controls.

Required law:

```text
TEMPLATES AND SANITIZED EXAMPLES ONLY
PRIVATE ISO RECORDS DO NOT ENTER THE PUBLIC REPOSITORY
```

Every example identity must be fictional, consented, or aggressively sanitized. Template language must not imply that a file-backed identity is conscious, autonomous, adopted, or authoritative merely because its files exist.

Suggested future public journey:

```text
CHOOSE TEMPLATE
→ DEFINE IDENTITY AND BOUNDARIES
→ ADD MEMORY POLICY
→ HYDRATE LOCALLY
→ VALIDATE
→ RUN SAFETY CHECKS
→ EXPORT A RECEIPT
→ REVISE WITH ROLLBACK
```

## Room 3 — `I Ching/`

Purpose: personal, symbolic, obscure, spiritual, pattern-oriented, divination, synchronicity, Jesus-pattern, and related interpretive research that Raven wants public but separated from the main JARVIS engineering entrance.

Candidate source families may include:

- I Ching records and interpretations
- Jesus-pattern research
- synchronicity and symbolic-number research
- autobiographical pattern research
- metaphysical or highly personal analytical notes
- relevant portions of `JesusISJohnJosephBarber/`
- related Jorm/source-vault material after public-safety review

This room must clearly distinguish:

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

Candidate contents:

- games
- creative tools
- experiments
- music projects not required by the JARVIS runtime
- websites and prototypes
- standalone research utilities
- abandoned or historical projects that remain useful publicly

Each project should carry a compact status marker:

```text
ACTIVE
MAINTAINED
EXPERIMENTAL
HISTORICAL
ARCHIVED
```

## Room 5 — `Evidence/`

Purpose: public safety records concerning AI misconduct, platform failures, misleading behavior, security issues, governance failures, authorship concerns, or other AI-related problems Raven has captured and wants publicly listed.

This room is evidence-governed, not accusation-governed.

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

Every published evidence packet should include, where applicable:

- evidence ID;
- date and timezone;
- source and capture method;
- content digest;
- redaction statement;
- factual observations;
- clearly labeled interpretation or allegation;
- affected product/provider/model/version when known;
- reproduction steps when safe;
- known limitations;
- correction and response channel;
- current resolution status;
- privacy and legal review state.

Safety rules:

- remove credentials, private tokens, private addresses, and unnecessary personal identifiers;
- do not publish private conversations involving third parties without review and redaction;
- preserve originals privately when public redaction is required;
- avoid presenting inference as proven intent;
- preserve corrections and provider responses;
- do not include exploit details that would materially enable abuse before responsible disclosure is complete.

Suggested internal structure:

```text
Evidence/
├── README.md
├── INDEX.md
├── Cases/
│   └── EVD-YYYY-NNNN-SUBJECT/
│       ├── README.md
│       ├── TIMELINE.md
│       ├── CLAIMS.md
│       ├── SOURCES.json
│       ├── REDACTIONS.md
│       ├── RESPONSES.md
│       ├── STATUS.json
│       └── Public/
├── Schemas/
├── Methodology/
└── Corrections/
```

## Rich README standard

The repository root and every major public room require a curated, human-readable README. Generated index files may support navigation but may not replace authored entry pages.

Each rich README should include:

1. a plain-language purpose statement;
2. who the room is for;
3. what is inside and what is deliberately excluded;
4. a visual or concise architecture map;
5. a recommended starting path;
6. runnable or concrete examples where applicable;
7. maturity and maintenance status;
8. safety, privacy, evidence, or interpretation boundaries;
9. a directory map with meaningful descriptions;
10. contribution and correction routes;
11. links to deeper technical or historical material;
12. a last-reviewed date and responsible steward.

The root README should behave like a public landing page rather than an internal repository index. It should quickly explain the five rooms and provide distinct routes for builders, researchers, people creating ISOs, visitors exploring personal pattern research, and readers reviewing AI-safety evidence.

Recommended root navigation:

```text
JARVIS
→ engineering, demos, runtime, architecture

ISOs
→ templates, guides, validators, and safe file-backed identity design

I CHING
→ personal symbolic and pattern research

PERSONAL PROJECTS
→ independent creative and technical work

EVIDENCE
→ governed public AI-safety evidence and case records
```

## Compatibility and migration law

1. Existing authoritative files are not moved merely because the new route is cleaner.
2. Every move requires an original path, destination, digest, references, reason, and rollback route.
3. Old public links receive compatibility pointers or redirects when practical.
4. Git history is not treated as a sufficient navigation system.
5. Generated indexes cannot promote content or decide room placement.
6. Sensitive content must pass public-safety review before entering any room.
7. The `Evidence/` room may not silently absorb personal research; evidence and interpretation remain distinct.
8. The `I Ching/` room may contain personal interpretations but must label them as such.
9. The `ISOs/` room publishes templates and sanitized examples, not private crew identities.
10. JARVIS engineering remains the default public entrance.
11. Rich authored READMEs are required for the root and each major room.
12. No deletion is authorized by this architecture document.

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
FILES MOVED: 0
FILES DELETED: 0
DIRECTORIES MOVED: 0
ROOT README REWRITTEN: NO
PUBLIC EVIDENCE PUBLISHED: 0
PRIVATE ISO RECORDS PUBLISHED: 0
```

This document authorizes the target architecture and audit classifications. It does not authorize blind bulk movement, deletion, publication of unredacted personal information, exposure of private ISO records, or factual claims unsupported by evidence.
