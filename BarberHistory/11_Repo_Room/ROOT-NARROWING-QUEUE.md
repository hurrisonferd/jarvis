# Root Narrowing Queue

Created: 2026-07-24
Status: ACTIVE

## Purpose

This is the decision queue for making the root less broad without moving files prematurely.

## Decisions

| Item | Current State | Recommendation | Why |
| --- | --- | --- | --- |
| `_work_public_main/` | ignored local mirror | Keep ignored | Archive shelf, not source. |
| `_work_private_repair/` | ignored private ghost tree | Keep ignored | Recovery shelf, redaction-sensitive. |
| `rooms/repos/private/` | ignored private repo shell | Keep ignored | Local `.git` shell; GitHub `hurrisonferd/Jarvis-Private` is source of truth. |
| `rooms/repos/private-work/` | ignored private repo shell | Keep ignored | Not public root source; formerly `Jarvis-Private-work/`. |
| `.claude/` | untracked command/settings folder | Decide track vs ignore | Could be useful project config, but tool-specific. |
| `.continue/` | tracked MCP configs | Keep for now | README documents Continue setup. |
| `.codex/` | local Codex tool state | Ignore/local | Tool state, not project source unless specific files are intentional. |
| `BarberHistory/` | untracked active scaffold | Decide public/private/separate | Contains personal/medical/legal/project context. |
| `rooms/shelf/contracts/` | shelved placeholder | Keep shelved or remove later | No active source found. |
| `rooms/shelf/gameboy/` | shelved placeholder | Keep shelved or remove later | Real GameBoy material lives in public/private maps. |
| `rooms/shelf/jpl/` | shelved placeholder | Keep shelved or remove later | JPL exists in architecture/private workspaces, not this folder. |
| `chaos/` | tracked source + ignored runtime files | Split later | Source and runtime state share a folder. |
| `mnemos/` | one tracked helper + cache likely | Keep for now | Small and meaningful memory helper. |
| `docs/` | static/public files | Keep for now | Public docs/app surface. |

## Safe Next Actions

These are safe because they do not destroy information:

```text
add labels/docs
add ignore rules for clearly local/generated folders
create archive maps
create future move proposals
```

These need explicit decision:

```text
move BarberHistory
move JarvisMain
split chaos
remove empty placeholder roots
track or ignore .claude
re-root public app into apps/docs
```

## Proposed Root Classes

| Class | Meaning | Examples |
| --- | --- | --- |
| `ACTIVE_SOURCE` | Code/config needed for current build/runtime | `supabase`, `src`, `scripts`, package files |
| `SYSTEM_CANON` | Architecture/manual/canon records | `JarvisMain`, `intake`, `mnemos` |
| `PUBLIC_SURFACE` | Static web/docs output | `docs` |
| `PERSONAL_INDEX` | Personal history and project atlas | `BarberHistory` |
| `LOCAL_TOOLING` | Developer tool config/state | `.continue`, `.claude`, `.codex` |
| `LOCAL_RUNTIME` | Logs, DBs, generated outputs | `chaos/*.json`, `dist`, `node_modules`, `__pycache__` |
| `ARCHIVE_MIRROR` | Nested repo/mirror/recovery shelves | `rooms/repos/*` |
| `PARKED_PLACEHOLDER` | Empty or not-current root dirs | `contracts`, `gameboy`, `jpl` |

## Rule

```text
Do not reduce roots by hiding meaning.
Reduce roots by assigning each thing a job.
```
