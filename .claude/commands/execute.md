Run this command in bash and display the results to Raven:

```bash
python3 scripts/jarvis-bridge.py "$ARGUMENTS"
```

This submits an event through the GRID Execution Bridge (AEGIS gate).

Usage:
- `/execute submit speak "Raven asked about P07"` — log a speak event
- `/execute submit execute "Run domain sync" P05` — log an execute event with patch ref
- `/execute submit propose "Add MERIDIAN alignment tracking"` — log a proposal event
- `/execute list` — show recent execution trace
- `/execute list 20` — show last 20 trace entries
- `/execute trace <id>` — inspect a specific trace record

All events are validated by AEGIS and stored in execution_trace. Rejected events are logged too — the audit trail is complete.
