# Evidence

A governed public record of AI-safety concerns, misleading behavior, privacy failures, authorship problems, security issues, platform responses, and corrections.

This is an evidence room, not an accusation dump.

## Case standard

Every case should separate:

```text
RAW SOURCE
PUBLIC REDACTION
FACTUAL OBSERVATION
CLAIM OR ALLEGATION
ANALYSIS
LIMITATIONS
REPRODUCTION STEPS
SUBJECT RESPONSE
CORRECTION
CURRENT STATUS
```

## Proposed case layout

```text
Evidence/
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

## Publication rules

- Remove credentials, private addresses, unnecessary personal identifiers, and sensitive third-party data.
- Preserve original evidence privately when a public copy must be redacted.
- Record source, date, timezone, capture method, digest, and known limitations.
- Do not state inferred intent as proven fact.
- Preserve provider responses and later corrections.
- Withhold exploit details that could materially enable abuse until responsible disclosure is complete.

## Current source candidates

Existing `dataharvest/` material and selected records under `JesusISJohnJosephBarber/` may contain evidence candidates, but mixed personal, interpretive, support, and safety material must be separated before migration.

## Status

```text
ROOM: ACTIVE SCAFFOLD
PUBLIC CASES: NONE PROMOTED BY THIS CHANGE
SOURCE REVIEW: REQUIRED
```

**Steward:** ERIS  
**Authority:** Raven  
**Last reviewed:** 2026-08-02
