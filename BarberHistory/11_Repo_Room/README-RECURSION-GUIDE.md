# README Recursion Guide

Created: 2026-07-24
Status: ACTIVE

## Purpose

This guide tells JORM how to write cave signs recursively.

Every useful folder should answer:

```text
what is this cave?
what lives here?
what does not belong here?
where do I go next?
what is the source of truth?
```

## Yggdrasil Rule

Apply the Yggdrasil stack to folder signs:

| Layer | Folder Sign Equivalent |
| --- | --- |
| `JD` | Define what this folder means. |
| `JNL` | Name the path/address. |
| `LAL` | List child folders/files and where to go next. |
| `JFS` | State organization rules and boundaries. |
| `JMS` | Point to truth instead of duplicating truth. |
| `JSS` | State lifecycle: active, parked, archived, deprecated, generated. |

Simple version:

```text
README = meaning + map + boundary
INDEX  = larger registry when a folder has many entries
```

## When To Add A README

Add a README when a folder is:

```text
root-level
second-level under a major root
contains source code
contains system/canon docs
contains migrations/functions/tools
contains private/public boundary material
contains parked/archive/recovery material
has a name that is not self-explanatory
```

Do not add a README to:

```text
node_modules
dist
__pycache__
.venv
.git
generated build folders
runtime log folders
ignored repo mirrors unless intentionally local
```

## README Shape

Default shape:

```markdown
# Folder Name

One sentence: what this cave is.

## Main Areas

| Path | Purpose |
| --- | --- |
| `child/` | What child does. |

## Boundary

What belongs here.
What does not belong here.

## Next

Where to go next if this is not enough.
```

For source folders:

```markdown
## Source

| File | Purpose |
| --- | --- |

## Run / Verify

Commands if safe and relevant.
```

For canon/history folders:

```markdown
## Current Files

| File | Purpose |
| --- | --- |

## Evidence Rule

State retrieved/account/inferred/unresolved boundaries.
```

For parked/archive folders:

```markdown
## Status

Parked / archived / deprecated.

## Rule

Not active does not mean delete.
```

## INDEX Rule

Use `INDEX.md` when the folder has many records or registries.

```text
README = what this room is
INDEX  = what all the objects are
```

## Recursion Algorithm

For each folder:

1. Read existing `README.md` or `INDEX.md`.
2. If absent, inspect immediate files and child folders.
3. Classify folder:

   ```text
   ACTIVE_SOURCE
   CANON
   APP
   TOOLING
   BACKEND
   RUNTIME_LOCAL
   ARCHIVE
   PERSONAL_INDEX
   SHELF
   GENERATED
   UNKNOWN
   ```

4. Add or update a concise README.
5. Do not copy secrets or long private content.
6. Link to source-of-truth maps instead of duplicating them.
7. Recurse only into child folders that are source/canon/tooling/backend/personal-index.
8. Stop at generated/runtime/vendor folders.

## JORM Self-Check

Before adding a cave sign:

```text
Am I explaining the folder or summarizing every file?
Am I pointing to truth instead of copying truth?
Am I preserving privacy boundaries?
Am I making the next scan easier?
Am I using simple words when simple words work?
```

If yes, add the sign.

If no, make the sign smaller.

## Tarzan/Jane

```text
README say cave.
INDEX count shiny.
Map point truth.
No copy whole mountain.
No secret in sign.
Simple word good.
```
