# Design System Scour - 2026-07-24

Status: RETRIEVED

## Finding

Raven's "insane complicated full fleshed design system" is not a single design-system file. It is distributed across multiple project and world-model documents.

Clean summary:

```text
The design system is a world interface:
GameBoy body + Tron/Grid light-law aesthetic + Oda/Dante world traversal + JARVIS governance + RGB physics + CNS-safe music constraints.
```

## Major Design Sources

| Source | Location | What It Contains |
| --- | --- | --- |
| Grid Mythic Design Bible | `C:\Users\JB\jarvis\intake\recycle\the-grid-mythic-design-bible.md` | Oda-scale regions, Dante traversal, Tron interface language, governance constraints, navigation grammar. |
| Public handheld | `C:\Users\JB\jarvis\docs\index.html` | GitHub Pages GameBoy/RetroArch/JARVIS shell, War Room, screens, Supabase hooks. |
| TronUI project | `C:\Users\JB\jarvis\_work_private_repair\workspaces\TronUI\README.md` | TRON web UI as JARVIS browser-facing shell. |
| TronUI manifest | `C:\Users\JB\jarvis\_work_private_repair\workspaces\TronUI\MANIFEST.md` | Private development workspace and spec lineage. |
| TronUI canonical BIO | `C:\Users\JB\jarvis\_work_private_repair\workspaces\Projects\TronUI\BIO\TRONUIBIO-061026-0001-TRONUI.md` | Defines shell/interface role and governance boundaries. |
| TronUI JGPP | `C:\Users\JB\jarvis\_work_private_repair\workspaces\Projects\TronUI\JGPP\TRONUIJGPP-061026-0001-UI-REWORK-OUTDATED-GAMEBOY-PAGE-AND-THE-CONTROL-SURFACE.md` | Control surface direction: dex browser, proposal queue, Allow/Deny, audit feed. |
| GameBoy controller spec | `C:\Users\JB\jarvis\_work_private_repair\workspaces\Projects\PROJ-GAMEBOY-JARVIS-0001.md` | Base44 Game Boy-styled JARVIS controller app. |
| GameBoy Grid master plan | `C:\Users\JB\jarvis\_work_private_repair\Living_Codex\canonical\GS-JARVIS-GRID-GAMEBOY-0001.md` | One installable handheld that is the Grid; War Room, screens, backend boundary model. |
| Pachinko visual style | `C:\Users\JB\jarvis\_work_private_repair\workspaces\Brainstorm-Swarm\PachinkoBounce\08-VISUAL-STYLE.md` | RGB palette, ball anatomy, UI/HUD, animation, haptics, collection gallery. |
| Pachinko GDD visuals | `C:\Users\JB\jarvis\_work_private_repair\workspaces\Brainstorm-Swarm\PachinkoBounce\GDD-06-VISUALS.md` | Consolidated game visuals and RGB system. |
| Pachinko design DNA | `C:\Users\JB\jarvis\_work_private_repair\workspaces\Projects\PachinkoBounce\DESIGN-DNA.md` | Cultural DNA, ball types, rarity, monetization ethics, TRON synthesis. |
| MusicOS style guide | `C:\Users\JB\jarvis\_work_private_repair\workspaces\MusicOS\BIO-MUSICOS-STYLE.md` | Sonic/physics vocabulary, RGB encoding, CNS-safe music constraints, JoJo encoding. |

## Design Grammar

Status: RETRIEVED

From the Grid Mythic Design Bible:

```text
Oda-scale worldbuilding
+ Dantean guided traversal
+ Tron interface language
+ JARVIS governance
= THE GRID
```

Core visual/interface principle:

```text
The visual layer must make structure legible.
Beauty serves navigation.
```

Grid regions include:

- Archive Sea
- Forge
- Signal Spire
- Rationale Hall
- Routing Gate
- Rollback Vault
- Treaty Market
- Mirror District
- Law Chamber
- Neon Frontier

## Public Handheld Tokens

Status: RETRIEVED

Current `docs/index.html` CSS tokens:

```css
--pixel: 'Press Start 2P', monospace;
--amber: #f5a623;
--green: #00ff88;
--blue: #0af;
--red: #ff3355;
--dim: #1e3a52;
--text: #4a7a99;
--bright: #a0c8e0;
--bg: #020408;
--surface: #080f18;
```

## Pachinko RGB Tokens

Status: RETRIEVED

```css
--r-primary: #FF3B3B;
--g-primary: #3BFF3B;
--b-primary: #3B8BFF;
--bg-primary: #0A0E1A;
--bg-secondary: #1A1F2E;
--surface: #252B3D;
--border: #4A90D9;
--text-primary: #F0EDE8;
--text-secondary: #8892A8;
```

## Design System Layers

Status: INFERRED FROM RETRIEVED SOURCES

| Layer | Role |
| --- | --- |
| Body | GameBoy handheld / PWA / controller shell. |
| Light | Tron visual language: dark space, luminous routes, portals, identity discs. |
| World | Oda regions with rules, memories, conflicts, and routes. |
| Guide | Dante/Virgil traversal: confusion becomes orientation. |
| Law | JARVIS governance, Gold Law, AEGIS, Raven final authority. |
| Play | PachinkoBounce toy-like RGB physics and collectible spectacle. |
| Sound | MusicOS physics made audible, CNS-safe loop constraints. |
| Memory | MNEMOS / evidence / continuity / archive paths. |

## Verdict

```text
The design system exists.
It is scattered because it is bigger than UI tokens.
It should be consolidated into a BarberHistory design atlas, not rewritten from scratch.
```
