# BootOS Chronological Filename Convention

Chronological artifacts must sort naturally by time and remain understandable without opening the file.

## Canonical form

```text
YYYY-MM-DD_HHMMSS±ZZZZ__subject-title.ext
```

Example:

```text
2026-07-30_190600-0400__world-002-build-epoch-the-crew-protocol.json
```

Rules:

- Put the local timestamp first.
- Include the UTC offset so records remain unambiguous.
- Follow the timestamp with two underscores.
- Use a concise lowercase subject title in kebab case.
- Keep the extension meaningful: `.json`, `.jsonl`, `.md`, `.log`, or `.receipt.json`.
- Never use generic chronological names such as `session.json`, `notes.md`, or `latest.json` for durable records.
- Stable code, schemas, workflows, and canonical configuration files keep stable semantic names and are exempt from timestamp prefixes.

## Daily records

```text
YYYY-MM-DD_HHMMSS±ZZZZ__daily-closeout-subject.ext
```

Daily folders are optional because the filename itself sorts chronologically. Where volume is high, use:

```text
archive/YYYY/MM/DD/
```

## Weekly records

Use the ISO week in the subject while retaining the actual creation timestamp:

```text
YYYY-MM-DD_HHMMSS±ZZZZ__weekly-closeout-YYYY-Www-subject.ext
```

Example:

```text
2026-08-02_190000-0400__weekly-closeout-2026-W31-vessel-two.json
```

## Collision handling

If two artifacts share the same second and subject, append a deterministic sequence or receipt suffix:

```text
2026-07-30_190600-0400__crew-protocol__002.json
```

The timestamp and subject title must also be present inside structured records when the schema supports them.
