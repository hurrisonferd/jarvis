# JARVIS Execution Model

## Pipeline (canonical)
```
INTENT → ROUTE → EXECUTE → RESULT → RECONCILE → LOG
```

| Stage | System | Supabase Action |
|-------|--------|-----------------|
| INTENT | AYRE | intake row |
| ROUTE | ODIN | tool_id selected |
| EXECUTE | SKADI | mcp_calls insert |
| RESULT | — | mcp_results insert |
| RECONCILE | HUGINN | drift_log check |
| LOG | — | execution_trace insert |

## KRONOS Time Modes (P28)
| Mode | Behavior |
|------|----------|
| frozen | No tick, GRID static |
| real | Auto-tick every 900ms |
| stepped | Manual tick on A button |

## AEGIS Gate Rules
- Block `emu_start` for GBA when `crossOriginIsolated=false` (GL4)
- All BUS events pass through AEGIS before dispatch

## Cartridge Standard (P22)
All modules implement: `{id, version, load, stop, snapshot, restore}`
