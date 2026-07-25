# Unresolved

Status: UNRESOLVED
Created: 2026-07-24

## Live Supabase

Local `.env` contains Supabase-related values and VAPID values. They were not copied here.

Update: live Supabase metadata was later retrieved through the connector and summarized in `C:\Users\JB\jarvis\BarberHistory\05_AI_Grid_JORM\SUPABASE-FULL-DIVE-2026-07-24.md`.

First-pass live table checks did not retrieve table data:

| Table / Surface | Result |
| --- | --- |
| `gameboy_snapshot` | 404 via anon-style REST path |
| `live_log` | 404 via anon-style REST path |
| `god_system_stats` | 404 via anon-style REST path |
| `push_subscriptions` | 404 via anon-style REST path |
| `mnemos_memories` | 404 via anon-style REST path |
| `dex_events` | 404 via anon-style REST path |
| service-role REST census | 401 |

Status: first-pass REST access issue is superseded for metadata discovery, but live row extraction and exact function-manifest recapture remain unresolved.

## Secret-Bearing Zones

Do not quote or publish:

```text
Living_Codex/Ego/GRID/GridVault/SECRETS/
Living_Codex/JMMS/SYS/JOHNNY-OS-GUIDE.md
.env
```

These may contain API-key-like values, tokens, conversation IDs, or deployment coordinates.

## Not Fully Digested Yet

| Source | Reason |
| --- | --- |
| 68 Claude/JORM event files | Counted and sampled; not fully extracted line-by-line. |
| RAW transcripts | High evidence value; require careful quoting and correction logs. |
| Public audit burst | Found; needs timeline/evidence cards. |
| Mnemos memory JSON/JSONL | Found; needs parser and dedupe. |
| Git history media/assets | Found by log; need targeted extraction. |
| Jarvis-Private-work packed repo | Visible as packed/shallow; not normal tree-indexed in first pass. |
| Jarvis-Private broken worktree | Needs repair/reclone decision before indexing. |

## Next Best Pass

1. Parse mnemos JSON/JSONL into a searchable local summary.
2. Extract JORM/Claude RAW event titles, dates, and direct evidence claims.
3. Build one project card per project family.
4. Recover history-only MonsterOS/MusicOS artifacts by commit.
5. Resolve Supabase access with secure credential handling.
