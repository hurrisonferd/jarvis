# Scripts

`scripts/` is the small local tooling cave.

## Current Scripts

| File | Purpose |
| --- | --- |
| `jarvis_heartbeat.py` | Observe-only repo/intake heartbeat watcher. |
| `cave_readme_audit.py` | Find folders missing README/INDEX cave signs. |
| `generate_vapid.py` | Generate VAPID key material locally. Treat output as sensitive. |
| `install_gbrain.ps1` | Install and initialize GBrain for Continue/local experiments. |

## Rule

Scripts here should be small, reviewable, and locally runnable.

Long-running daemons, tool registries, and historical scripts should be mapped before being moved here.
