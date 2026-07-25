# Root Taxonomy

Created: 2026-07-24
Status: ACTIVE

## Short Answer

The top-level root feels too broad because it currently mixes five different kinds of things:

```text
active source
architecture/docs
runtime/local state
AI tool config
archive/recovery mirrors
personal history/indexing
```

Those should not all feel equal.

## Current Root Roles

| Root Item | Role | Keep At Root? | Notes |
| --- | --- | --- | --- |
| `README.md` | Public project entry | YES | Root landing page. |
| `package.json`, `package-lock.json`, `tsconfig.json` | Node/TypeScript build config | YES | Active diagnostics/build surface. |
| `requirements.txt` | Python helper deps | YES | Small active dependency pointer. |
| `.gitignore`, `.github/` | Git/GitHub config | YES | Repo infrastructure. |
| `.env.example` | Safe env example | YES | Keep; no secrets. |
| `.env` | Local secret/runtime config | ROOT LOCAL ONLY | Ignored, never commit. |
| `supabase/` | Active backend source | YES | Core deploy/source surface. |
| `src/` | Active TypeScript diagnostics | YES | Small active source. |
| `scripts/` | Active helper scripts | YES | Small active tooling. |
| `JarvisMain/` | Architecture/canon/manual/tool docs | YES FOR NOW | Large conceptual root; eventually could move under `system/` if doing a v2 layout. |
| `intake/` | AI handoff/review lane | YES | Active workflow lane. |
| `docs/` | Public/static docs app | YES | Published/static surface. |
| `chaos/` | Mixed active helper + ignored runtime logs/db | SPLIT LATER | `session_sync.py` is source; logs/db are local state. |
| `mnemos/` | Memory helper source | YES FOR NOW | One tracked helper; name is canonically meaningful. |
| `.continue/` | Continue MCP config | MAYBE | Project config if shared; local tool config if personal. |
| `.claude/` | Claude commands/settings | DECIDE | Untracked; likely project/tool config. |
| `.codex/` | Codex local/tool state | LOCAL | Keep local/ignored unless intentional. |
| `.venv/`, `node_modules/`, `dist/`, `__pycache__/` | generated/vendor/cache | NO | Ignore/generated. |
| `_work_public_main/` | Public mirror/archive | NO | Ignored local mirror. |
| `_work_private_repair/` | Private ghost tree/recovery archive | NO | Ignored local recovery shelf. |
| `rooms/repos/private/`, `rooms/repos/private-work/` | Private repo shells | NO | Ignored local `.git` shells; GitHub `hurrisonferd/Jarvis-Private` is source of truth. |
| `BarberHistory/` | Personal index/history scaffold | DECIDE | Active, but may belong private or separate repo. |
| `rooms/shelf/contracts/` | Shelved placeholder | NO | Condensed from root; no active source found. |
| `rooms/shelf/gameboy/` | Shelved placeholder | NO | Condensed from root; public/private repos have real GameBoy material. |
| `rooms/shelf/jpl/` | Shelved placeholder | NO | Condensed from root; JPL lives in public/private architecture and workspaces. |
| `grid_images/` | Generated/local media | NO | Ignored. |

## Narrow Root Target

A narrower current root should feel like:

```text
README.md
package.json
package-lock.json
tsconfig.json
requirements.txt
.gitignore
.env.example
.github/
.continue/              optional project config
supabase/               active backend
src/                    active TS diagnostics
scripts/                active helpers
JarvisMain/             architecture/canon/manual
intake/                 AI review lane
docs/                   static/public surface
chaos/                  split later
mnemos/                 memory helper
  BarberHistory/          pending privacy/repo decision
  rooms/shelf/            inactive placeholders
```

Everything else should be local-only, archive-only, or parked.

## Better Future Layout

If doing a deeper v2 reorganization later:

```text
apps/
  docs/
  diagnostics/

backend/
  supabase/

system/
  JarvisMain/
  intake/
  mnemos/
  chaos/

tools/
  scripts/

history/
  BarberHistory/        or private/separate repo

_archive/               local only, never public by accident
  _work_public_main/
  _work_private_repair/
  rooms/repos/private/
  rooms/repos/private-work/
```

Do not do this move yet. This is a target map, not an instruction.

## Immediate Non-Destructive Cleanup

1. Keep mirror folders ignored.
2. Label empty/placeholder roots.
3. Decide whether `.claude/` and `.continue/` are project config or local config.
4. Decide whether `BarberHistory/` belongs in public repo, private repo, or its own repo.
5. Split `chaos/` into source vs runtime later.

## Root Law

```text
Top-level means "important now."
Archive means "important but not active."
Ignored means "local, generated, private, or recoverable elsewhere."
```
