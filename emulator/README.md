# JARVIS — Emulator Resources

All emulator assets are organized here.

## Structure

```
emulator/
  roms/
    gb/     — Game Boy ROMs (.gb)
    gbc/    — Game Boy Color ROMs (.gbc)
    gba/    — Game Boy Advance ROMs (.gba)
  saves/    — Save states (per-ROM)
  cores/    — Engine notes and adapter docs
  screenshots/ — Captured frames
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
