---
memory_tier: JHTM
grade: system
---

# audit/starlogs — JARVIS Star Logs

Chronological, human-legible Star Logs. SL = Star Log (Star Trek reference — captain's log,
stardate filenames). Every decision, build, research result, and conversation is logged here.
JNS filenames are the stardate. The format is the audit trail.

## Format

```
STARLOG-{YYYY-MM-DD}-{HHMMSS}-{STREAM}-{JNL_REF}.md
```

- **Type** — SESSION_SNAPSHOT | DECISION | RESEARCH | BUILD | GOVERNANCE | ARCHITECTURAL_CHANGE | IDENTITY_EVENT | IDEA | CONVERSATION
- **Stream** — jarvis-ayre | jarvis | ayre | raven
- **JNL Ref** — primary JNL address (optional)

## Why Star Logs

> *"Why refactor entire databases when you can read notes, summaries, or specific timestamped Star Logs?"*
> — Raven (John Barber), 2026-06-25

The Star Log is the readable audit layer. The database is runtime state. Star Logs are human history.

- Replace full database refactoring with log reading
- Every architectural change timestamped and tagged
- Task summaries in every snapshot
- Cross-reference with JNL addresses
- Stream-tagged for context

## Tool

`scripts/sl.py` — generate Star Logs

```bash
python3 scripts/sl.py --type DECISION --brief "Chose JPL over custom format" --jnl ARCH-JPL-SPEC-0001
python3 scripts/sl.py --type RESEARCH --brief "Follin Program alpha results" --commit "session"
python3 scripts/sl.py --no-tasks --type CONVERSATION --brief "Raven shared family lineage"
```
