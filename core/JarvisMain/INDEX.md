# JarvisMain — Canonical Core

**Truth lives here.** Git-first, cloud-mirrored. Every governed object has a JNL address.

## Subdirectories

| Directory | Purpose |
|-----------|---------|
| `Architecture/` | System design, specs, constraints, governance |
| `god_systems/` | 29 god systems — cognition layer |
| `yggdrasil/` | JFS addressing substrate — JNL, JMS, JSS, JMMS |
| `Connectors/` | MCP, Dex, GPT connectors and diagnostics |
| `Manual/` | Operations reference, rebuild packet |
| `Patches/` | Patch ledger and process |
| `Audit/` | System audits and reviews |
| `Implementation/` | Active specs, archived JIPs, index summaries |
| `Backups/` | Backup manifests (no actual data) |

## Key Files

- `Architecture/JARVIS-SYSTEM-MANUAL.md` — full system manual
- `Architecture/CONTINUITY-THROUGH-THE-CONNECTOR.md` — resume-path documentation
- `Architecture/constraints.md` — GL1–GL9 contract
- `yggdrasil/jd/entries/` — JD dictionary (canonical, live in Supabase)
- `god_systems/README.md` — god system registry

## Legibility (GL14)

Every directory has an INDEX.md or equivalent. Every god system has a README.md. Every
decision is timestamped and attributable. The scaffold IS the intelligence.

## Navigate

```
core/JarvisMain/
├── Architecture/        → system design + specs
│   ├── specs/          → governance specs
│   ├── canon/          → canonical contracts
│   └── rebuild/        → rebuild packet
├── god_systems/         → 29 god systems (T0–T9)
├── yggdrasil/           → JFS addressing kernel
├── Connectors/          → MCP, Dex, GPT
├── Manual/              → OPS-REFERENCE.md, rebuild packet
├── Patches/             → patch ledger
├── Audit/               → system audits
├── Implementation/      → active specs, archived JIPs
└── Backups/             → manifest only
```
