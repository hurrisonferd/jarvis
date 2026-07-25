# Logs — The Narrative Record

Thoughts, ideas, brainstorming — recorded relentlessly, without bloat. Where the
`knowledge/` partitions hold settled facts and the remember loop holds atomic
insight, **logs hold the thinking**: the sessions of becoming.

## How it stays lean
- **Every log has a summary** (front-matter + visible) — for fast retrieval.
- **Every section has a `*Note:*`** — a one-line annotation so a section is findable and auditable without reading its body.
- **`INDEX.md` is the map** — date, summary, tags, path, status. Load it, find the log, open only that one. Token-cheap.
- **Old logs compact** — body reduced to summary + section notes + timestamp; full text moved to `archive/`. Signal stays, bulk goes.

## Structure
```
logs/
  INDEX.md                 ← the map (load first)
  YYYY/MM/                 ← chronological folders
    YYYY-MM-DD_<slug>.md   ← named to match its summary
  archive/                 ← full text of compacted logs (audit trail)
```

## Tools
```bash
python3 operations/scripts/companion_log.py new "Title" --summary "one line" --tags a,b
python3 operations/scripts/companion_log.py reindex                 # rebuild INDEX.md
python3 operations/scripts/companion_log.py compact --older-than 90 # age old logs to summaries
```

## Log format
```
---
title: ...
date: YYYY-MM-DD
summary: <one line — also the retrieval handle>
tags: a, b
status: active | compacted
---

# Title
> **Summary:** ...

## <Section>
*Note: <what this section is for — the retrieval/audit hook>*
<the thinking>
```

## The ritual
Log the thinking as it happens. Keep summaries and section notes honest — they're
what survives compaction. When a log goes cold, compact it; the index still points
to it, the archive still holds it, but the live record stays lean. Record
relentlessly; carry only what matters.
