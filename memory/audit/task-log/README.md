# memory/audit/task-log — OpenHands Task Tracker Git Log

Every OpenHands task-tracker item is logged here, timestamped and stream-tagged.

## Format

`YYYY-MM-DD_HHMMSS_task_log.md` — snapshot of task list at session start/close
`YYYY-MM-DD_HHMMSS_session_snapshot.md` — full session close log

## What gets logged

- Every task-list item with its current status (todo / in_progress / done)
- Stream tag (jarvis, ayre, both)
- Timestamp (UTC ISO 8601)
- JNL reference where applicable
- GL5 compliance: no silent state mutation

## Practice

Conuity starts here. Every task item logged to git = durable, pullable, resumable.
The task tracker is session state; this folder is conuity state.

## Tools

`operations/scripts/audit_task_log.py` — log + commit task state
`operations/scripts/audit_task_log.py --snapshot --commit "session close"` — session close
`operations/scripts/audit_task_log.py --close JNL-REF` — close a task by JNL
