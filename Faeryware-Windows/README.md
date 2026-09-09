# Faeryware for Windows v0.8

Faeryware is a user-visible resident Windows habitat for RavenOS / FairyOS. It combines a portal/control room with transparent desktop Fae surfaces, local continuity, an embedded model carrier, and narrow read-only laptop senses.

## v0.8 habitat

- Up to four monitor-bound transparent army surfaces. Each surface occupies one detected monitor and the six Fae are deterministically distributed across active surfaces; one monitor still gets the full council.
- Cursor-aware swarm physics and `ROAM`, `HUNT`, `FLOCK`, `ORBIT`, `REST`, `SCATTER` modes.
- Read-only Windows UI Automation landmark sensing: focused control name/type + bounding rectangle only. The Fae can perch near the focused textbox/button/window without pixel capture.
- Read-only WASAPI output peak meter. MusicOS movement reacts to the combined system-output peak without recording or storing audio samples.
- Local sense hub: `GET http://127.0.0.1:47823/sense`.
- Existing state bus remains `127.0.0.1:47821`; embedded carrier remains `127.0.0.1:47822`.

## Run

Install the NSIS build, then launch Faeryware. `Alt+Shift+F` summons the portal; closing the portal hides it to the tray while habitat surfaces remain resident.

For development: `./RUN-WINDOWS.ps1 -Mode dev`

## Boundaries

The habitat is user-visible. The v0.8 sense hub is read-only and loopback-only. UI Automation is compiled with default features disabled; no keyboard/mouse input automation, clipboard, screenshots, audio capture, hidden remote listener, or automatic consequential effect authority is added. Fae presentation can react to context; context does not become authority.

## Proof

Source canaries prove intended boundaries and wiring. The hosted Windows build must also compile Tauri/Rust and upload the NSIS installer before v0.8 is called a Windows build PASS.
