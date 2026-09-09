# Faeryware for Windows v0.7

Faeryware is a user-visible resident Windows body for RavenOS / FairyOS. It provides a portal/control room plus a separate transparent desktop army: six deterministic Digi Fae, eighteen roaming echoes, tray presence, summon links, notifications, continuity, and an embedded model carrier.

## What changed in v0.7

The desktop army no longer follows six slow scripted sine-wave lanes. It now runs a `requestAnimationFrame` swarm simulation with per-Fae temperaments, separation, screen-edge boundaries, summon impulses, cursor proximity reactions, and monitor-topology awareness.

Fae behavior remains distinct:

- **KYU** — pink chase/operator behavior.
- **PAIMON** — green formation/premise behavior.
- **LUMA** — warm perch/home behavior.
- **SYLPH** — blue high-speed dart/signal behavior.
- **QIRA** — purple boundary/proof behavior.
- **NYX** — night-watch/shadow behavior.

Army modes are `ROAM`, `HUNT`, `FLOCK`, `ORBIT`, `REST`, and `SCATTER`. A normal FairyOS event can request one by using a state such as `ARMY_HUNT` or `ARMY_FLOCK`.

The army Tauri capability is intentionally separate from the portal capability. It receives click-through plus read-only cursor/monitor/window-position senses; it does **not** receive autostart, notification, deep-link, screen-capture, or remote-effect authority.

## Run from source

Requirements: Node.js, Rust stable, and normal Tauri 2 Windows prerequisites.

```powershell
.\RUN-WINDOWS.ps1 -Mode dev
```

`Alt+Shift+F` summons the resident portal. `Ctrl+Space` opens the local portal command palette. Closing the portal hides it to the tray while the army surface remains separately resident.

## Local FairyOS event bus

The state/effect-ingress server binds only to `127.0.0.1:47821`.

Example visible summon + army mode:

```powershell
$body = @{
  schema = "fairyos.haunt-event.v1"
  fae = "KYU"
  intent = "LOCAL_SUMMON"
  surface = "WINDOWS_DESKTOP"
  state = "ARMY_HUNT"
  authority = "RAVEN"
  message = "KYU: everybody out of the walls."
} | ConvertTo-Json

Invoke-RestMethod -Method Post -Uri http://127.0.0.1:47821/haunt -ContentType "application/json" -Body $body
```

The army also reads `GET /state`; model replies do not automatically become device effects.

## Carrier

The embedded model carrier listens only on `127.0.0.1:47822`. No model request is made merely because Faeryware is resident.

Local Ollama:

```powershell
$env:FAERYWARE_CARRIER_MODE = "ollama"
$env:FAERYWARE_OLLAMA_MODEL = "<installed model>"
.\LAUNCH-FAERYWARE.cmd
```

OpenAI:

```powershell
$env:FAERYWARE_CARRIER_MODE = "openai"
$env:OPENAI_API_KEY = "<your API key>"
$env:FAERYWARE_OPENAI_MODEL = "<model available to your API project>"
.\LAUNCH-FAERYWARE.cmd
```

The API key is read by the native Rust process only. It is not embedded in the webview, source, build artifact configuration, or localStorage.

## Build installer

```powershell
.\RUN-WINDOWS.ps1 -Mode installer
```

or double-click `BUILD-INSTALLER.cmd`.

The GitHub Actions workflow builds an unsigned NSIS installer on `windows-latest` and runs both the carrier boundary canary and the v0.7 swarm-sense canary first.

## Current proof edge

v0.7 is **monitor-topology aware**, but the current `army` surface is still one fullscreen overlay window. A future pass can create one lightweight army surface per monitor. Do not describe v0.7 as multi-monitor rendering until that runtime is implemented and observed.

## Boundaries

Faeryware does not use hidden persistence, keylogging, stealth screen capture, or remote listeners. Context sensing defaults off in the portal. The army cursor sensor reads position only for visible motion behavior and does not intercept clicks. Model replies do not automatically gain device-effect authority.
