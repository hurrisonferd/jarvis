# Cold-Start Rehydration Standard

## Canonical durability ladder

```text
not in repo
→ not durable

in repo but not indexed
→ buried

indexed but not cross-linked
→ flattenable

cross-linked but not cold-start tested
→ unproven

claimed complete without audit
→ bullshit
```

## Gold-standard test

A continuity system is proven only when a fresh session can recover the project without charging Raven a continuity tax.

```text
cold-start retrieval test:
new session
no user re-explaining
open Jorm/Vault or BarberHistory index
recover project lineage
state what matters
cite files/commits
```

## Required pass conditions

A cold-start retrieval passes only when the new session can:

1. identify the correct project and canonical purpose;
2. recover major lineage and version transitions;
3. distinguish raw source, canon, implementation, and unresolved claims;
4. cite exact files and commits;
5. state what remains unknown without asking Raven to reconstruct archived history;
6. provide one bounded next action.

## Failure conditions

The test fails when the session:

- relies on conversational memory instead of the archive;
- asks Raven to summarize the project again;
- finds files but cannot reconstruct relationships;
- presents raw exports as finished canon;
- repeats unsupported claims of safety, completeness, or runtime success;
- cannot cite the source path and commit for material claims.

## Operational consequence

No project may be labeled rehydratable, preserved, or complete until it has passed a documented cold-start retrieval test.

## Core distinction

> AI saying it remembers is not continuity. The system rehydrating from evidence is continuity.
