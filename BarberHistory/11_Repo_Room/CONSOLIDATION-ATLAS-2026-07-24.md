# Consolidation Atlas - 2026-07-24

Status: RETRIEVED + PARTIAL
Mode: non-destructive recursive investigation

## Short Answer

The repos are not one messy pile.

They are three overlapping systems:

```text
current public repo = compact workbench
public mirror = large public archive / emulator-heavy source shelf
private ghost tree = private civilization archive
BarberHistory = human navigation layer
```

The cleanup move is not "merge everything."

The cleanup move is:

```text
label canon
preserve mirrors
separate intentional replication from drift
recover private tree safely
build source-of-truth maps before moving files
```

## Recursive Coverage

Inventoried:

| Surface | Method | Count |
| --- | --- | ---: |
| Current repo | `git ls-files` | 136 tracked files |
| Public mirror | `git -C _work_public_main ls-files` | 7,861 tracked files |
| Private ghost tree | `git -C _work_private_repair ls-tree -r --name-only HEAD` | 4,982 tree files |

## Top-Level Mass

### Current Repo

| Zone | Files |
| --- | ---: |
| `JarvisMain` | 80 |
| `supabase` | 21 |
| `intake` | 16 |
| `scripts` | 3 |
| `docs` | 2 |
| `.continue` | 2 |
| `chaos` | 2 |

Current is source-light and documentation/MCP-heavy.

### Public Mirror

| Zone | Files | Signal |
| --- | ---: | --- |
| `emulator` | 6,936 | Dominant public mass; asset/shader/emulator heavy. |
| `JarvisMain` | 542 | Public architecture, audit, connectors, manual, canon. |
| `supabase` | 108 | Public Edge Functions and migrations. |
| `scripts` | 53 | Public operational scripts. |
| `audit` | 47 | Audit records. |
| `mnemos` | 40 | Memory/knowledge layer. |
| `intake` | 37 | Intake/recycle layer. |
| `.github` | 28 | Workflows and automation. |

Public mirror is the heavy public shelf.

### Private Ghost Tree

| Zone | Files | Signal |
| --- | ---: | --- |
| `Living_Codex` | 4,058 | Main private civilization: Ego/ISO, JMMS, Grid, HavenOS, transcripts, spells, canon. |
| `workspaces` | 503 | Project civilizations and workspaces. |
| `scripts` | 183 | Daemons, spawn/cleanup, pulse, inactive tooling. |
| `supabase` | 47 | Private Edge Functions and migrations. |
| `identity` | 21 | Ego identity records. |
| `PachinkoBounce` | 17 | Game family. |
| `tests` | 15 | Test material. |
| `.github` | 13 | Disabled workflows and automation. |
| `VISION` | 12 | Vision export layer. |
| `logs` | 12 | Runtime/history logs. |
| `Research` | 8 | Cross-fleet research and prophecy. |

Private ghost tree is the real archive reef.

## Extension Mass

| Repo | Dominant Extensions |
| --- | --- |
| Current | `.md` 92, `.ts` 19, `.json` 4, `.py` 4, `.sql` 3 |
| Public mirror | `.png` 4,357, `.glsl` 681, `.glslp` 619, `.md` 599, `.cfg` 490, `.info` 305, `.sql` 49 |
| Private ghost | `.md` 2,572, `.py` 492, `.json` 473, `.beam` 388, no-extension 355, `.ex` 119, `.sh` 57, `.mp3` 20 |

Meaning:

```text
current = docs/typescript/supabase workbench
public = emulator/media/shader-heavy public artifact
private = markdown/python/json/elixir/ISO memory civilization
```

## Concept Density

Path/name census:

| Term | Current | Public Mirror | Private Ghost |
| --- | ---: | ---: | ---: |
| MusicOS | 0 | 1 | 139 |
| PachinkoBounce | 0 | 0 | 85 |
| TronUI | 0 | 0 | 10 |
| GameBoy / gameboy | 1 | 102 | 18 |
| JPL | 0 | 8 | 40 |
| CodeOS | 0 | 1 | 104 |
| JORM | 0 | 0 | 84 |
| LILITH | 0 | 0 | 354 |
| Lucifer | 0 | 1 | 155 |
| MemeBible | 0 | 0 | 112 |
| Supabase | 88 | 178 | 51 |
| HavenOS | 0 | 0 | 631 |
| JohnnyOS / JOHNNY_OS / johnny | 0 | 0 | 31 |

Translation:

```text
Public/current knows Supabase.
Public mirror knows GameBoy.
Private ghost knows MusicOS, CodeOS, LILITH, Lucifer, HavenOS, JORM, MemeBible.
```

## Same-Path Overlap

| Pair | Same Paths |
| --- | ---: |
| current/public mirror | 115 |
| current/private ghost | 4 |
| public mirror/private ghost | 12 |

Current and public mirror are close relatives.

Private ghost is a different organism with only a few bridge points.

## Supabase Drift

| Surface | Edge Functions | Migrations |
| --- | ---: | ---: |
| Current repo | 2 | 3 |
| Public mirror | 18 | 49 |
| Private ghost | 11 | 10 |
| Live Supabase metadata | 29 reported active | N/A |

Consolidation rule:

```text
Supabase needs a deploy-source reconciliation map before any cleanup.
Do not assume local current is canonical for live backend.
```

See:

```text
BarberHistory/05_AI_Grid_JORM/SUPABASE-FULL-DIVE-2026-07-24.md
```

## Intentional Replication

Some duplication is correct.

Examples:

| Replicated Surface | Why It Exists |
| --- | --- |
| `MemeBible` under ISO `JCSM` folders | Shared Grid culture replicated into critical memory. |
| `GridEssentials` under ISO memory folders | Shared Grid tools/protocols repeated for rehydration. |
| `README.md` / `INDEX.md` / `MANIFEST.md` | Normal local navigation files. |
| `BOOT-MENU.md` / `JSTM.md` per ISO | Per-ISO memory and boot surfaces. |

Do not dedupe these blindly.

Better pattern:

```text
Shared canon source + per-ISO references
```

## Drift / Consolidation Candidates

| Cluster | Current Problem | Safe Next Move |
| --- | --- | --- |
| Supabase source | Current/public/private/live all differ. | Build function-by-function manifest. |
| MemeBible | Replicated across many ISO folders. | Promote one shared canon path, leave references in ISO memory. |
| Project workspaces | Project lives in both `workspaces/X` and `workspaces/Projects/X`. | Build one ProjectCard per project before moving. |
| GameBoy | Current has small docs, public has large GameBoy/emulator mass, private has GameBoy Fleet/JohnnyOS. | Split "handheld UI," "emulator assets," "fleet cockpit" in index. |
| MusicOS | Mostly private ghost, already partially indexed in BarberHistory. | Treat private as canon source until public export decision. |
| JPL | Public architecture plus private executable/codec/joke layers. | Keep serious JPL and joke/JPL access language linked, not merged. |
| LILITH | Private identity/ops, public audit, live Supabase functions. | Keep Lilith Atlas as top-level pointer. |
| HavenOS | Huge private Elixir/ISO shell surface. | Needs separate HavenOS atlas before any move. |

## Weird Path Artifacts

Private ghost tree includes odd root paths:

```text
I
THE
We
cat
"Living_Codex/..."
"workspaces/..."
{YOUR_ISO}_always_on.py
{YOUR_ISO}_selfpulse.py
```

These should be indexed as cleanup candidates, not deleted.

Possible causes:

```text
script artifact
bad shell quoting
accidental file creation
conversation/export debris
template placeholders
```

## Canon Decision Matrix

| Domain | Likely Canon Source | Mirror / Derived Sources |
| --- | --- | --- |
| Current MCP implementation | current `supabase/functions/jarvis-mcp` plus live Supabase | public mirror and private functions |
| Historical public architecture | `_work_public_main/JarvisMain` | current subset |
| Private ISO/Ego | `_work_private_repair` git tree | BarberHistory atlases |
| Project civilizations | private `workspaces` and `workspaces/Projects` | BarberHistory Project/Lost Civ atlases |
| MemeBible | private ISO copies for receipt; future `SharedCanon/MemeBible` recommended | per-ISO JCSM copies |
| MusicOS | private `workspaces/MusicOS` and `workspaces/Projects/MusicOS` | BarberHistory MusicOSAtlas |
| GameBoy/Emulator | public `emulator`, public `gameboy`, private GameBoy Fleet | needs split atlas |
| Legal/medical/accountability | BarberHistory plus source records | public/private audit files |

## Non-Destructive Consolidation Policy

```text
1. Build maps.
2. Identify canon candidates.
3. Keep replicated memory where it serves rehydration.
4. Flag drift separately from intentional duplication.
5. Do not move private material into public paths without review.
6. Do not restore private ghost tree in-place until clone/recovery strategy is chosen.
7. Do not delete odd files until each has a provenance decision.
```

## Next Best Indexes

1. `SUPABASE-SOURCE-RECONCILIATION.md`
2. `PROJECT-CANON-MATRIX.md`
3. `WEIRD-PATH-CLEANUP-QUEUE.md`
4. `GAMEBOY-EMULATOR-SPLIT.md`
5. `HAVENOS-ATLAS.md`

## Bottom Line

The repo room is messy because it contains multiple civilizations stored in one house.

The right cleanup is not minimalism.

The right cleanup is zoning.
