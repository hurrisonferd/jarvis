# Requiem — Gaps · Heal · Life (2026-06-15)

_Soft & Wet finds the gaps · Crazy Diamond heals what's broken · Gold Experience decides what gets
life — and what stays dormant on purpose. A pruning/healing sweep, not a build (GL7: the next gain
is using and mending, not adding)._

## Soft & Wet — the gaps (built but unwired)
| tool | state | verdict |
|---|---|---|
| `rollup.py` (compression ladder) | built, **never scheduled** → `growth_archive.jsonl` grew unbounded | **GAP — healed**: scheduled weekly via `rollup.yml`. Bounds the archive (the "memory without compression" risk, with its cure finally wired). |
| `changes_lens.py` | out of seed, runs in `changes-lens.yml` | by design (git-derived; can't pass the seed-drift gate). Not a gap. |
| `sync_supabase.py` | out of seed, runs in the mirror job | by design. Not a gap. |

## Crazy Diamond — heals
- **Drift check missed untracked files** — `git diff --quiet` ignored new files, so a JD entry once
  landed in the registry but not git (AUD-GATE). **Healed:** the check now uses `git status
  --porcelain` (catches untracked). A forgotten new object can no longer pass green.
- **Stale graph** (healed earlier today) — `graph_export` wired into the seed tail; graph.json
  tracks the registry now (151 nodes / 241 edges). 0 dangling edges.

## Gold Experience — what gets life, and what stays dormant
- **Dormant gods (CHAOS · POSEIDON · HADES · HERMES):** canon, unrouted by ODIN (P24). **Leave
  dormant by choice** — activating one is a GL7 expansion decision with a routing trigger, not a
  neglected gap. Do not force life in.
- **3 isolated objects** (`ARCH-FAM-IDX`, `IDEA-PAN-INS`, `LOG-MED-LOG`): an index, an idea, a media
  catalog — **legitimate leaves.** Deliberately NOT force-wired; adding edges to flatten a number
  is anti-GL7. They earn their place as endpoints.
- **18 open TASKs** (JGPP explorations: Deoxys/GDS/JPL/MMOD telemetry, JC/SL, Pantheon): alive as
  explorations, ~a day old — not stale. **Raven's call** to promote (→ JIP/active) or archive; not
  auto-touched (GL2).

## The Requiem verdict
The system has no broken canon, no dangling edges, no ungated write path, no stale graph. The only
real gaps were *unwired automation* (rollup) and a *blind spot in a check* (untracked) — both healed.
Everything "underutilized" is either dormant-by-design or a legitimate leaf. **The honest next move
is not more life — it's use and restraint.** Reach has caught up to integration; keep it there.
