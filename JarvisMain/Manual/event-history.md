# Event History

This file records the bounded history of notable manual and operating changes.

## Current window

Only the most recent events stay here. Older events should be summarized and folded out into higher-level docs or archived notes when this grows too large.

## Entries

### 2026-06-24

- Added continuity layers and bounded autonomy as an explicit spec surface.
- Restored resumability as the governing term for identity persistence.
- Added `jarvis_session_open` and `jarvis_session_close` to the MCP connector surface.
- Added resumability receipts with `source_basis`, `repo_head`, and `verified_at`.
- Added the session-open bootstrap mirror and call-order note.
- Added session-close JSTM purge/promote behavior.
- Reconciled mirror counts against live GitHub and Supabase state.

