# Chaos

`memory/chaos/` is the local continuity and session-sync cave.

## Source

| File | Purpose |
| --- | --- |
| `session_sync.py` | Session start/end helpers, mission state, and continuity wrapper logic. |
| `chaos_seed.example.json` | Safe sample seed for local setup. |

## Local Runtime

This folder may also contain ignored local state:

```text
chaos_seed.json
session_log.json
prometheus_log.json
live_log.json
tunnel_*.txt
*.db
*.sqlite
```

Do not promote runtime files into git without explicit review.
