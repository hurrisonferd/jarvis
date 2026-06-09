# Event Contract v1.0

## Canonical Event Schema
```json
{
  "type": "string",
  "source": "jarvis",
  "patch_id": "Pxx",
  "stage": "AYRE|AEGIS|ODIN|KRONOS|SKADI|MNEMOS|HUGINN|LOG",
  "payload": {},
  "correlation_id": "uuid",
  "git_commit_ref": "sha",
  "intent": "human-readable intent",
  "timestamp": "ISO-8601"
}
```

## Hard Rules
- No event without `patch_id`
- No GRID mutation without Supabase event
- No orphan events (every event links to a session)
- `correlation_id` chains related events across systems

## Event Tables
| Table | Purpose |
|-------|----------|
| `execution_trace` | Primary event spine — all system events |
| `events` | Legacy session events (session_id scoped) |
| `session_events` | Granular per-session event log |
| `mcp_calls` | Tool invocation requests |
| `mcp_results` | Tool execution results |
| `drift_log` | HUGINN reconciliation failures |
| `validation_log` | HALO + AEGIS rule checks |
