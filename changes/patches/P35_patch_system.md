# P35 — Consistent Patch Register

**Status:** open (built it with itself)
**Priority:** highest
**Authority:** Raven (John Barber)

## The problem

Patches (P00…P34) were the unit of traceability, but tracking had drifted:

- **Four overlapping surfaces** — `audit/patch_ledger.json` (canonical),
  `logs/patch-log.json` (mirror), `mnemos/context/patches.json` (empty daily
  file), `changes/patches/*.md` (sparse). No single writer. (GL7 violation —
  overlapping state.)
- **Chronological drift** — the array held `… P32, P34, P33`; `intake_max_patch`
  said P32 while P34/P33 existed.
- **No "building" state** — a patch was `pending` or `done`. There was no way to
  *open* a patch and keep *accumulating* changes into it before execution, with a
  dated trail.

## The system

One register. One writer. A lifecycle that matches how work actually happens.

**Source of truth:** `audit/patch_ledger.json`. Sole writer:
`scripts/jarvis-patch.py`. `logs/patch-log.json` is regenerated from it as a
derived cache (the one writer keeps it consistent).

**Lifecycle (the `status` field):**

| state | meaning |
|---|---|
| `open` | building — accumulating dated entries before execution |
| `executed` | shipped / deployed (terminal success) |
| `partial` | executed but carrying `remaining` items |
| `pending` | reserved, not started |
| `deferred` | held by decision, not rejected |
| `reference` | read-only advisory, never executed |

**Accumulation:** while a patch is `open`, every change appends an entry
`{ts, note, commit?}` to its `entries[]`. The patch keeps building until you
`exec` it. The entry trail *is* the audit record — open → entries → execute,
all dated, all chronological.

## Surfaces

- `scripts/jarvis-patch.py open|add|exec|defer|show|list` — the writer.
- `/patch` slash command — same, from chat.
- Session brief shows **OPEN PATCHES (building)** with entry count + last note, so
  a building patch is never lost between sessions.

## Traceability guarantees

- IDs are monotonic and chronological — `next_patch` reserves the next number;
  the tool refuses to let an out-of-order id slip in.
- Compact one-line-per-patch serialization → each change is a one-line diff.
- Every build entry is timestamped; commits attach to entries and to the patch.

## Dogfood

This patch was opened, built, and (on commit) executed *through the tool it
defines*. Entries 1–N on P35 are the real build log of P35.
