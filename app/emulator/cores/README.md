# Emulator Cores

Documentation for each engine adapter.

## WasmBoyCore (GB/GBC)
- Package: `wasmboy@0.7.1`
- API: `WasmBoy.config(canvas, opts)` → `loadROM(buf)` → `play()`
- No SharedArrayBuffer required

## MGBACore (GBA)
- Package: `@thenick775/mgba-wasm@2.4.1`
- API: `mGBA({canvas, locateFile})` → `FSInit()` → `uploadRom(arr, cb)` → `loadGame(path)` → `resumeGame()`
- Requires `crossOriginIsolated = true` (SharedArrayBuffer)
- COI headers injected by `docs/gameboy-sw.js` service worker
