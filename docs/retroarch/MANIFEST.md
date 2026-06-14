# RetroArch host — vendoring manifest (P06)

The GameBoy page (`docs/index.html`) launches RetroArch in a full-window overlay
that loads `docs/retroarch/index.html`. That launcher is committed and works
today; it grants cross-origin isolation (via `coi-serviceworker.js`) and then
hands off to the **official RetroArch web player** — which is the only piece that
must be vendored in by hand, because the WASM/binaries are multi-MB and the build
sandbox cannot fetch them.

## What's already here (committed)
- `index.html` — COI bootstrap + launcher + install panel (this is the iframe target).
- `coi-serviceworker.js` — injects COOP/COEP/CORP so SharedArrayBuffer works on GitHub Pages.
- `player/` — empty slot (`.gitkeep`) where the official bundle goes.

## The one manual step (needs a browser + network)
1. Get the RetroArch web player:
   - Full frontend (XMB menu, core selector, save states): download from
     <https://web.libretro.com/> (it's a static site — grab the whole bundle), **or**
   - Individual cores (lighter): <https://buildbot.libretro.com/web/>
     (e.g. `gambatte_libretro.js` + `.wasm` for GB/GBC, `mgba_libretro.js` + `.wasm` for GBA).
2. Put the bundle in `docs/retroarch/player/` so that
   `docs/retroarch/player/index.html` exists.
3. Commit + push. GitHub Pages serves `docs/`; the launcher detects the bundle
   (`HEAD ./player/index.html`) and redirects to it automatically. No code change needed.

## Why this shape
- **ROMs stay local.** RetroArch loads ROMs through its own file menu into Emscripten's
  IDBFS (an IndexedDB-backed filesystem). The ROM lives in *this browser's* storage and is
  never uploaded or committed. This is why P08 (GitHub ROM Indexer — ROMs in the repo) was
  deprecated: Raven's call, 2026-06-14 — "the roms i would hold locally not store online."
- **No CDN at runtime.** The previous path pulled WasmBoy/mGBA from jsDelivr/esm.sh on every
  boot — the fragility Raven hit. Vendoring the player in-repo removes the runtime CDN.
- **COI on a static host.** GitHub Pages can't set COOP/COEP headers, so `coi-serviceworker.js`
  injects them. First load registers the SW and reloads once; after that the frame is
  cross-origin isolated and SharedArrayBuffer is available.

## Verifying (browser, after vendoring)
- Open `https://hurrisonferd.github.io/jarvis/retroarch/` directly.
- Expect: one auto-reload, then the RetroArch UI (not the install panel).
- In the GameBoy page, press **A** on the EMULATOR view → the overlay opens the same frame.
- Load a ROM via RetroArch's menu; confirm a save state persists across a page reload (IDBFS).
