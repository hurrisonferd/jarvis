# Project Canon Matrix

Created: 2026-07-24
Status: RETRIEVED + PARTIAL

## Purpose

This matrix names where each major project appears and what should be treated as the likely source of truth before moving anything.

## Matrix

| Project / System | Current Repo | Public Mirror | Private Ghost Tree | Likely Canon For Now | Consolidation Move |
| --- | --- | --- | --- | --- | --- |
| JARVIS MCP | `core/supabase/functions/jarvis-mcp` | larger `core/supabase/functions/jarvis-mcp`, `core/JarvisMain/Connectors` | private `core/supabase/functions/jarvis-mcp` plus Lilith/private tools | live Supabase + current code for active local; public for history | Build function manifest. |
| Supabase backend | 2 functions / 3 migrations | 18 functions / 49 migrations | 11 functions / 10 migrations | live metadata until source reconciled | Do not cleanup until reconciled. |
| Grid | current docs/intake | public `grid`, `core/JarvisMain/Architecture`, `gameboy` | private `Living_Codex/Ego/Grid`, `workspaces/Grid`, GridTools | private + public architecture together | Create Grid Canon Map. |
| JORM | BarberHistory only in current | little/no path presence | `Living_Codex/Ego/JORM` | private ghost + BarberHistory | Keep JORM Atlas/Provenance. |
| Lilith | BarberHistory only in current | public audit mentions and live functions | `Living_Codex/Ego/LILITH`, `GS-LILITH`, Lilith MCP/bridge/scripts | private ghost + BarberHistory Lilith Atlas | Do not flatten to "coordination." |
| Lucifer | BarberHistory and symbols | public single/path traces | `Living_Codex/Ego/LUCIFER`, Grid canon, transcripts | private ghost + BarberHistory Symbols | Keep clinical/symbolic distinction. |
| MemeBible | BarberHistory atlas | absent | replicated across ISO JCSM folders | private ghost receipt; future SharedCanon | Make shared canon later. |
| MusicOS | BarberHistory atlas | tiny trace | `workspaces/MusicOS`, `workspaces/Projects/MusicOS`, audio/spectrograms | private ghost | Keep private until export decision. |
| PachinkoBounce | BarberHistory atlas | absent/minimal | `workspaces/PachinkoBounce`, `workspaces/Projects/PachinkoBounce`, Brainstorm-Swarm | private ghost | Make one project card. |
| TronUI | BarberHistory design atlas | absent/minimal | `workspaces/TronUI`, `workspaces/Projects/TronUI` | private ghost | Keep as design/UI family. |
| CodeOS | BarberHistory lost civ map | public `memory/mnemos/knowledge/projects/codeos.md` trace | `workspaces/CodeOS`, `workspaces/Projects/CodeOS`, equations, games | private ghost | Split CodeOS core, Physics, game seeds. |
| JPL | public architecture specs | public `JPL` specs | private JPL workspaces, JPL-Gold, JPL-OS, codec research | both: public spec + private executable/joke layers | Keep serious/joke duality. |
| HavenOS | absent | absent | huge private Elixir/ISO shell surface | private ghost | Needs own atlas. |
| JohnnyOS | absent | absent | private `JOHNNY_OS.sh`, Johnny command center references | private ghost | Needs command-center atlas. |
| GameBoy / Emulator | current `docs`, `gameboy` trace | public `emulator`, `gameboy`, shaders/assets | private GameBoy Fleet / JohnnyOS surfaces | split: public emulator vs private cockpit | Create split map. |
| GDS | public JD entries | public architecture/specs | private `workspaces/GDS`, `workspaces/Projects/GDS` | private + public specs | Project card. |
| Bridgekeeper | BarberHistory lost civ map | public workflow/script dirt | private Bridgekeeper BIO/security concepts | private for concept, public for script | Redaction-sensitive. |
| RoundTable | absent | absent | private `workspaces/RoundTable`, project bio/JGPP | private ghost | Project card. |
| Genesis | absent | absent | private `workspaces/Genesis`, `workspaces/Projects/Genesis` | private ghost | Project card. |
| Deoxys | absent | absent | private `workspaces/Deoxys`, telemetry JGPP | private ghost | Project card. |
| Legion | absent | absent | private `workspaces/Legion` | private ghost | Separate analytics vs symbolic language. |
| Naruto | absent | absent | private reference-only workspace | external repo suspected | Locate external repo later. |
| NeuroMax / NeuroKey | absent | absent | private NeuroMax + VISION NeuroKey/SIMOS | private ghost | Resolve name collision. |

## Consolidation Law

```text
Same name in two places does not mean duplicate.
Same role in two places means possible drift.
Same file replicated across ISOs may be rehydration design.
```

## Next Move

Create one `PROJECT-CARD` per row only when the project becomes active or externally shareable.
