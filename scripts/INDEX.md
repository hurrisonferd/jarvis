# Scripts — Automation Tools

Standalone Python/Shell/JS tools. All stdlib-only except `cryptography` (VAPID keys).
System Python, no venv.

## Categories

| Prefix | Purpose |
|--------|---------|
| `jarvis-*` | Session lifecycle, patches, proposals, heartbeat |
| `mnemos*` | Memory operations, backup, domain sync |
| `audit*` | Digest, task log, canon check |
| `companion*` | Companion log and remember |
| `music*` | Audio processing (NLP, ears, distill) |
| `sl*` | StarLog session close |
| `grid*` | Grid operations (keygen, node init) |
| `eris*` | Entropy check, bridgekeeper |
| `dex*` | Dex reconciliation |
| `test_*` | Test scripts |

## Key Scripts

- `sl.py` — StarLog generator, always use `--bifrost` flag
- `jarvis-bridge.py` — MCP bridge
- `jarvis-session-start.sh` — session initialization
- `jarvis-session-end.py` — session close
- `audit_task_log.py` — task tracker logging
- `mnemos_backup.py` — memory backup

## One-liner shortcuts

```bash
python3 scripts/sl.py --session-close --bifrost   # Always use --bifrost
python3 scripts/sl.py --mimir                      # Routing table
python3 scripts/jarvis-bridge.py                    # MCP bridge
```

## Non-Python

- `grid_keygen.mjs` — ESM grid key generator
- `newbranch.sh` — branch creation helper
- `install_gbrain.ps1` — Windows brain install script
