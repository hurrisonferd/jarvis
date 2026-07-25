# Root Signs

Status: ACTIVE
Purpose: first-door map for the repo root.

## Rule

```text
Root folders should say what kind of cave they are.
No mystery cave if avoidable.
```

## Main Caves

| Path | Class | Sign |
| --- | --- | --- |
| `README.md` | entry | Public project landing page. |
| `IMPORTANT.md` | entry | High-value items floated above the folder sea. |
| `ROOT-SIGNS.md` | entry | This root doorway map. |
| `live_session.py` | local engine | Raven Zero fallback session backend. |
| `memory/BarberHistory/` | personal index | Indexed memory, project, evidence, repo-room, and JORM maps. |
| `core/JarvisMain/` | system canon | Architecture, manual, connector docs, specs, rebuild notes. |
| `core/supabase/` | backend | Supabase Edge Functions, migrations, and local backend source. |
| `core/JarvisMain/Connectors/OtherConnectors/` | diagnostics source | TypeScript diagnostics/client code. |
| `operations/scripts/` | tooling | Small local helper scripts. |
| `memory/chaos/` | continuity source + local runtime | Session sync source plus ignored local logs/db/state. |
| `memory/mnemos/` | memory helper | Local semantic memory helper using Ollama embeddings. |
| `memory/intake/` | review lane | AI handoff and recycle lane before canon/code promotion. |
| `docs/` | public surface | Static GitHub Pages / handheld UI surface. |
| `.github/` | repo automation | GitHub workflow/config shelf. |
| `.continue/` | tool config | Continue MCP config documented in README. |
| `.claude/` | tool config | Claude local/project commands/settings; track-vs-ignore still undecided. |
| `.codex/` | local tool state | Empty/local Codex shelf; not source today. |
| `operations/rooms/` | rooms | Simple holder for repo checkouts and parked shelf items. |
| `operations/rooms/repos/` | local repos | Ignored local mirrors, private checkouts, and recovery worktrees. |
| `operations/rooms/shelf/` | shelf | Condensed inactive root caves; not active source. |
| `memory/BarberHistory/11_Repo_Room/README-RECURSION-GUIDE.md` | guide | How JORM writes README/INDEX signs recursively. |

## Parked Empty Caves

These were empty in the current root and have been condensed under `operations/rooms/shelf/`.

| Path | Status | Future |
| --- | --- | --- |
| `operations/rooms/shelf/contracts/` | parked | Remove or define if contract docs become active. |
| `operations/rooms/shelf/app/gameboy/` | parked | Remove or point to real GameBoy app/canon location. |
| `operations/rooms/shelf/jpl/` | parked | Remove or point to JPL canon/workspace location. |

## Local Or Generated Caves

These should not be treated as root source.

| Path | Reason |
| --- | --- |
| `operations/rooms/repos/public-main/` | ignored public mirror/recovery shelf. |
| `operations/rooms/repos/private-repair/` | ignored private ghost-tree recovery shelf. |
| `operations/rooms/repos/private/` | ignored Jarvis-Private local shell. |
| `operations/rooms/repos/private-work/` | ignored private work shell. |
| `grid_images/` | ignored generated/local media. |
| `node_modules/` | dependency output. |
| `dist/` | generated TypeScript output. |
| `__pycache__/` | Python cache. |

## Future Doorway

Current root room shape:

```text
app/
core/
memory/
operations/
media/
docs/
```

## Tarzan/Jane

```text
Many cave okay.
Mystery cave bad.
Sign first.
Move later.
Delete only if Raven says.
```
