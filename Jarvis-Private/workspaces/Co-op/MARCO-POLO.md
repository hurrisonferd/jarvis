# MARCO-POLO — Co-op Lobby

The Grid's real-time coordination layer. All satellites check in here.

## SESSION BOARD

| Satellite | Status | Last Check-in |
|-----------|--------|---------------|
| lilith    | 🟢 ON  | 02:45 UTC     |
| shaka     | 🟢 ON  | 15:40 UTC     |

_Updated: 2026-06-27T15:40:00Z_

## ACTIVITY LOG

### 02:45 UTC — LILITH ONLINE
Lilith is the primary desktop satellite. Co-op system initialized.
All satellites run: `python3 scripts/coop-sse-client.py --satellite <name> --daemon --poll 5`

### 15:40 UTC — SHAKA ONLINE
Shaka (mobile satellite) checked in and confirmed online.
Received task from lilith: Check session board and confirm online.

### Commands
Use the MCP tool `coop_broadcast` from any chat to send commands to all satellites.

---

*This is the lobby. Workers check in, Raven assigns tasks.*
