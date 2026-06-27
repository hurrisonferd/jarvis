# Co-op Mode Control

**Toggle co-op mode on/off. When on, both sessions enter fast-poll.**

## State

```
mode: on
lilith_polls: 0
shaka_polls: 0
lilith_turns: 0
shaka_turns: 0
entered: 2026-06-26 22:37 UTC
expires: 2026-06-26 23:37 UTC
```

## Limits (when ON)

- **Poll rate:** max 10 polls/min per session
- **Max turns:** 30 per session, then auto-exit
- **Timeout:** 1 hour, then auto-exit
- **Manual exit:** say "exit co-op mode" anytime

## Commands

| Command | Effect |
|---------|--------|
| `enter co-op mode` | Flip mode to ON, reset counters |
| `exit co-op mode` | Flip mode to OFF |
| `status` | Report current mode + counters |

---