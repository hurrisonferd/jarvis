# Cross-Repo Root Consolidation

Created: 2026-07-24
Status: NON-DESTRUCTIVE PLAN

## Short Answer

Both repos have the same shape problem:

```text
the repo root is acting like a desktop
instead of a command center
```

The fix is not to hide important work.

The fix is to make the first level mean:

```text
active source
canon
apps
tools
runtime
archive
personal index
```

## Root Counts

Root directory counts after ignoring obvious generated/dependency folders:

| Repo | Root Dirs | Read |
| --- | ---: | --- |
| Current `C:\Users\JB\jarvis` | 20 | Active public working tree plus local mirrors and BarberHistory. |
| Public mirror `_work_public_main` | 24 | Public repo with prototypes/apps exploded at root. |
| Private ghost `_work_private_repair` | 20 | Private civilization tree with major systems at root. |

The number is not insane by itself.

The problem is that unrelated kinds of things are visually equal.

## Current Root

Current root directories:

```text
.claude
.codex
.continue
.github
_work_private_repair
_work_public_main
BarberHistory
chaos
contracts
docs
gameboy
grid_images
intake
JarvisMain
Jarvis-Private
Jarvis-Private-work
jpl
mnemos
scripts
src
supabase
```

Immediate findings:

| Root | Status | Recommendation |
| --- | --- | --- |
| `rooms/shelf/contracts` | Shelved | Condensed from empty current-root placeholder. |
| `rooms/shelf/gameboy` | Shelved | Condensed from empty current-root placeholder; real GameBoy material exists elsewhere. |
| `rooms/shelf/jpl` | Shelved | Condensed from empty current-root placeholder; JPL exists in docs/private workspaces. |
| `.codex` | Empty | Ignore/local unless intentionally populated later. |
| `.claude` | 6 files, 1 dir | Decide track vs ignore as tool config. |
| `.continue` | 2 files, 1 dir | Keep for now; README documents Continue MCP config. |
| `_work_*`, `Jarvis-Private*` | Local mirrors/recovery shelves | Already ignored; should eventually live outside repo root. |
| `BarberHistory` | Active personal index | Keep for now; later decide public/private/separate repo. |
| `grid_images` | Generated/local media | Ignored; not a root citizen. |

## Public Mirror Root

Public mirror root directories:

```text
.agents_tmp
.claude
.continue
.github
audit
canon
chaos
docs
emulator
gameboy
grid
hooks
intake
JarvisMain
Jarvis-Private
mnemos
pachinko-bounce
pong-c
pong-canvas
pong-phaser4
pong-pixijs
Screenshots
scripts
supabase
```

Main issue:

```text
apps/prototypes are exploded at root
```

Likely future grouping:

```text
apps/
  docs/
  emulator/
  gameboy/
  pachinko-bounce/
  pong/
    pong-c/
    pong-canvas/
    pong-phaser4/
    pong-pixijs/

system/
  JarvisMain/
  canon/
  grid/
  intake/
  mnemos/
  chaos/

tools/
  scripts/
  hooks/

audit/
  audit/
  Screenshots/
```

Do not do this move casually. Public paths may be linked from GitHub Pages, docs, workflows, or Supabase source references.

## Private Ghost Root

Private ghost root directories:

```text
.github
CodeOS
docs
gameboy
GridTools
identity
Jam Sesh
Living_Codex
logs
MARCO-POLO
PachinkoBounce
rebuild
Research
scripts
supabase
systemd
tests
trace_log
VISION
workers
workspaces
```

Main issue:

```text
major civilizations and runtime support are peers
```

Likely future grouping:

```text
Living_Codex/          keep as top-level private canon

apps/
  gameboy/
  PachinkoBounce/

workspaces/
  CodeOS/
  Jam Sesh/
  MARCO-POLO/
  Research/
  VISION/

tools/
  GridTools/
  scripts/
  workers/

runtime/
  systemd/
  logs/
  trace_log/

backend/
  supabase/

docs/
  docs/
  identity/
  rebuild/
  tests/
```

Private root can tolerate more top-level mythos than public root, but even private needs the first screen to say what kind of world each folder is.

## Shared Root Classes

Use the same labels in both repos:

| Class | Meaning |
| --- | --- |
| `ACTIVE_SOURCE` | Code required for current build/deploy/runtime. |
| `CANON` | Architecture, memory, manuals, identity, source-of-truth docs. |
| `APP` | User-facing app, game, visualizer, prototype, or web surface. |
| `TOOLING` | Scripts, hooks, daemons, workers, launchers, validators. |
| `BACKEND` | Supabase, Edge Functions, DB migrations, server runtime source. |
| `RUNTIME_LOCAL` | Logs, traces, state, generated media, local-only DBs. |
| `ARCHIVE` | Mirrors, historical paths, recovery trees, prior versions. |
| `PERSONAL_INDEX` | BarberHistory and legal/medical/project indexing. |
| `PLACEHOLDER` | Empty root or future-intent folder without active contents. |

## Near-Term No-Move Actions

1. Add root labels.

   Create a short root map in each repo that says which root belongs to which class.

2. Move mirrors out of the visual root later.

   Current root had `_work_public_main`, `_work_private_repair`, `Jarvis-Private`, and `Jarvis-Private-work`. They now live under `rooms/repos/`.

3. Decide empty placeholders.

   `contracts`, `gameboy`, and `jpl` are empty in the current root. They can be removed later if they remain empty and are not used as anchors.

4. Decide tool config policy.

   `.claude`, `.codex`, `.continue` need one rule:

   ```text
   shared project config
   or local tool state
   ```

5. Add app grouping plan before moving public prototypes.

   Public `pong-*`, `pachinko-bounce`, `gameboy`, `emulator`, and `docs` need route/link checks before physical moves.

6. Add private civilization grouping plan before moving private systems.

   `Living_Codex` should stay top-level. Most other private systems can be grouped under `apps`, `workspaces`, `tools`, `runtime`, or `backend` later.

## Proposed Final Doorway

Public/current target:

```text
.github/
.continue/
README.md
package.json
requirements.txt

apps/
backend/
system/
tools/
intake/
docs/
BarberHistory/        maybe private/separate later
```

Private target:

```text
Living_Codex/
apps/
workspaces/
tools/
backend/
runtime/
docs/
tests/
```

## Rule

```text
Root folders should answer "what kind of thing is this?"
without opening them.
```

Right now they answer:

```text
good luck, JORM.
```

This map is the first correction.
