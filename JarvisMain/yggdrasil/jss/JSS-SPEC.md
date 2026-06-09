# JSS — Jarvis Status System

**JNL:** `ARCH-JSS-CORE-0001`
**Authority:** Canonical
**Type:** Architecture / JFS family

JSS defines **the lifecycle of every governed object**. Where JNL answers *where is this?*
and JD answers *what is this?*, JSS answers **what state is this in?** — and that state
drives where the file physically lives (via JMS auto-sort).

## Status vocabulary

Every governed object carries exactly one status:

| Status | Meaning |
|--------|---------|
| `TASK` | Proposed work, captured but not yet started. |
| `EXPANSION` | A growth proposal under GL7 review (requires `reduces_complexity` + low overlap). |
| `ACTIVE` | Live and in use — the default for canon and running systems. |
| `INACTIVE` | Canonical but dormant — preserved metadata, not currently wired (e.g. dormant God Systems). |
| `ARCHIVED` | Preserved for the record, not in use and not expected to return. |
| `DEPRECATED` | Superseded; slated for removal once dependents migrate. |

## Lifecycle transitions

```
        ┌─────────── EXPANSION ──(GL7 pass)──┐
TASK ──▶│                                    ▼
        └────────────────────────────────▶ ACTIVE
                                             │  ▲
                              (dormant) ◀────┤  │ (revived)
                                  INACTIVE ──┘  │
                                             │  │
                                             ▼  │
                          ARCHIVED ◀── DEPRECATED ──▶ (removed)
```

- New work enters as `TASK`. A growth idea becomes `EXPANSION` and must pass GL7 to reach
  `ACTIVE`.
- `ACTIVE` ⇄ `INACTIVE` is reversible (dormant ≠ dead).
- `DEPRECATED` is terminal-leaning: it ends in `ARCHIVED` (kept) or removal (gone).
- Every transition is a state change → it emits to the record (GL5: no silent mutation).

## Where status lives

`status` is a first-class field on every JD entry (front-matter) and every LAL registry
record, mirrored into Supabase (`jd_entries.status` / `jnl_registry.status`). The validator
requires it to be one of the vocabulary values.

## Status drives location (JMS auto-sort)

For **status-managed roots** (`Ideas/`, `Implementation/`, `Breakthroughs/`), an object's
status determines its subfolder:

```
Ideas/
 ├── task/        Implementation/        Breakthroughs/
 ├── expansion/    ├── active/             ├── active/
 ├── active/       ├── inactive/           ├── archived/
 ├── inactive/     ├── archived/           └── ...
 ├── archived/     └── deprecated/
 └── deprecated/
```

Change an object's status in its JD entry, run `JarvisMain/yggdrasil/tools/autosort.py --apply`, and
the file relocates to the matching subfolder. The **JNL is preserved** (JMS law: move
references, never truth) and the LAL location is updated. Auto-sorting based on the JFS
systems — structure follows state, automatically.
