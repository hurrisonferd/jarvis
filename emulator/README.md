# JARVIS — Emulator Infrastructure

P06+P08+P09. GitHub = structure. Supabase = behavior. WASM = execution.

## Architecture
```
User ROM → FileReader API
         → ROMLoader.detect() → 'gb' | 'gba'
         → getCore(type) → WasmBoyCore | MGBACore
         → core.init(canvas) → core.loadROM(buf) → core.play()
         → emulator_state (Supabase)
         → save_states (Supabase, P09)
```

## Folder Structure
```
emulator/
  catalog/
    index.json        — ROM catalog metadata (P08)
    README.md         — catalog format spec
  roms/
    gb/               — Game Boy ROMs (.gb)
    gbc/              — Game Boy Color ROMs (.gbc)
    gba/              — Game Boy Advance ROMs (.gba)
  saves/
    README.md         — save states architecture (P09)
  cores/
    README.md         — engine adapter docs
  screenshots/        — captured frames
```

## Supported Engines (P06)
| Console | Engine | CDN |
|---------|--------|-----|
| GB/GBC | WasmBoy v0.7.1 | jsDelivr |
| GBA | @thenick775/mgba-wasm v2.4.1 | jsDelivr |

## COI Requirement
GBA (mGBA WASM) requires `crossOriginIsolated = true`.
The service worker (`docs/gameboy-sw.js`) injects COOP + COEP headers on first reload.

## ROM Detection (P02)
- ARM reset vector `0x2E 0x00 0x00 0xEA` → GBA
- Otherwise → GB/GBC

## Supabase Tables (P06/P08/P09)
| Table | Purpose |
|-------|--------|
| `emulator_state` | Per-session active core + ROM + status |
| `rom_library` | Catalog of known ROMs (P08) |
| `save_states` | Snapshot blobs per ROM/slot (P09) |

## Execution Frame Model
```
for each frame:
    input = pollController()
    state = core.run(input)
    render(state.framebuffer)
    if (save_enabled) writeSupabase(state)  ← P09
```
