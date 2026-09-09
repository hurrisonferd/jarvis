# Faeryware for Windows v0.5

Faeryware is a user-visible resident Windows body for RavenOS / FairyOS. It provides six Digi Fae, tray presence, summon links, notifications, a persistent colony, a command surface, and an embedded model carrier.

## Run from source

Requirements: Node.js, Rust stable, and normal Tauri 2 Windows prerequisites.

```powershell
.\RUN-WINDOWS.ps1 -Mode dev
```

`Alt+Shift+F` summons the resident portal. `Ctrl+Space` opens the local command palette. `ask <message>` sends an explicit model request through the embedded carrier.

## Carrier

The carrier listens only on `127.0.0.1:47822`. No model request is made just because the app is resident.

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

The GitHub Actions workflow also builds an unsigned NSIS installer artifact on `windows-latest`.

## Boundaries

Faeryware does not use hidden persistence, keylogging, stealth screen capture, or remote listeners. Context sensing defaults off. Model replies do not automatically gain device-effect authority.
