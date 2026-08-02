# Personal Projects Registry

This registry separates independent projects from the JARVIS product and from protected legacy systems.

## Status vocabulary

- `ACTIVE` — current development.
- `MAINTAINED` — supported but not under continuous development.
- `EXPERIMENTAL` — exploratory and unstable.
- `HISTORICAL` — preserved for lineage or reference.
- `ARCHIVED` — intentionally retired but retained.
- `PROTECTED-LEGACY` — no movement until dependency and parity review is complete.

## Protected families

| Family | Current surfaces | Status | Rule |
|---|---|---|---|
| Gameboy | `app/gameboy/`, `app/emulator/gameboy/`, operations shelf records | `PROTECTED-LEGACY` | Compare implementations and hosted links before selecting a canonical route. |
| RetroArch/emulator | `app/emulator/` | `PROTECTED-LEGACY` | Preserve manifests, cores, player paths, and public entry points. |
| MusicOS-related projects | `MusicOS/`, `runtime/MusicOSPortable/`, related memory atlases | `PROTECTED-LEGACY` | Separate runtime dependencies from independent creative tools before routing. |

## Intake table

| Project | Current path | Proposed room | Status | Dependency review | Public safety review | Action |
|---|---|---|---|---|---|---|
| Gameboy family | multiple | `Personal Projects/Gameboy/` or retained compatibility route | `PROTECTED-LEGACY` | required | required | frozen |
| Emulator family | `app/emulator/` | `Personal Projects/Emulation/` or retained route | `PROTECTED-LEGACY` | required | required | frozen |

New project classifications must record the original path, destination, references, digest, rollback route, and maintainer status before movement.
