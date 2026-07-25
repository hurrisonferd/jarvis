# Public Mirror Queue

Created: 2026-07-24
Status: RETRIEVED + NEEDS REVIEW

## Short Answer

`_work_public_main` is a large public mirror of the same GitHub remote as the current repo.

It has 7,861 tracked files and a dirty queue of 30 status lines.

## Current State

| Field | Value |
| --- | --- |
| Path | `C:\Users\JB\jarvis\_work_public_main` |
| Remote | `https://github.com/hurrisonferd/jarvis.git` |
| HEAD | `648dc91b` |
| Branch state | detached / no branch name reported |
| Tracked files | 7,861 |
| Dirty status lines | 30 |

## Largest Tracked Zones

| Zone | Files | Signal |
| --- | ---: | --- |
| `emulator` | 6,936 | Huge public emulator/game asset or code surface. |
| `JarvisMain` | 542 | Canon/audit/JORM/core public architecture. |
| `supabase` | 108 | Public Supabase functions/migrations. |
| `scripts` | 53 | Operational scripts. |
| `audit` | 47 | Audit outputs. |
| `mnemos` | 40 | Memory/knowledge records. |
| `intake` | 37 | Intake and clearance records. |
| `.github` | 28 | Workflows. |

## Dirty Queue Buckets

Current dirty status includes:

```text
modified workflow: .github/workflows/bridgekeeper.yml
modified script indexes: scripts/ACTIVE/README.md, scripts/INACTIVE/README.md
script move-looking pair: scripts/INACTIVE/eris_bridgekeeper.py deleted, scripts/ACTIVE/eris_bridgekeeper.py added
modified Supabase MCP: supabase/functions/jarvis-mcp/index.ts, resources.ts
new audit files under JarvisMain/Audit/
new JORM folder under JarvisMain/JORM/
new Lucifer timeline/count files
new Supabase migration: 20260724_cecil_slate_rls.sql
```

## Cleanup Buckets

| Bucket | Items | Suggested Action |
| --- | --- | --- |
| Audit burst | `JarvisMain/Audit/2026-07-24_*` | Keep together; make index before moving. |
| JORM public material | `JarvisMain/JORM/` | Keep; compare with BarberHistory JORM map. |
| Lucifer records | `LUCIFER-FRIEZACOUNT.md`, `LUCIFER-OSDD-DID-TIMELINE.md` | Keep; link from Symbols/Medical if needed. |
| Bridgekeeper script move | inactive delete + active add | Confirm intentional promotion. |
| Supabase changes | MCP files + RLS migration | Review as code/security change, not archive cleanup. |

## Rule

Do not auto-commit this mirror until the dirty queue is split into meaningful commits.

Suggested commit families:

```text
audit records
jorm/lucifer records
bridgekeeper activation
supabase rls/mcp changes
script index updates
```
