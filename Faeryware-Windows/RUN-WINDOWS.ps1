param(
  [ValidateSet("dev", "build", "installer")]
  [string]$Mode = "dev"
)

$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot

function Require-Command([string]$Name, [string]$InstallHint) {
  if (-not (Get-Command $Name -ErrorAction SilentlyContinue)) {
    Write-Host "[HOLD] Missing $Name" -ForegroundColor Yellow
    Write-Host $InstallHint
    exit 2
  }
}

Require-Command "node" "Install current Node.js, then reopen PowerShell."
Require-Command "npm" "Install current Node.js/npm, then reopen PowerShell."
Require-Command "cargo" "Install Rust using rustup, then reopen PowerShell."

if (-not (Test-Path ".\node_modules")) {
  Write-Host "[FAERYWARE] Installing JavaScript dependencies..." -ForegroundColor Magenta
  npm install
}

if (Get-Command python -ErrorAction SilentlyContinue) {
  python .\Tests\FAERYWARE-DESKTOP-NATIVE-CARRIER-CANARY.py
}

$carrierMode = if ($env:FAERYWARE_CARRIER_MODE) { $env:FAERYWARE_CARRIER_MODE } else { "auto" }
Write-Host "[FAERYWARE] Embedded carrier mode: $carrierMode" -ForegroundColor Cyan

switch ($Mode) {
  "dev" { npm run windows:dev }
  "build" { npm run windows:build }
  "installer" {
    npm run windows:installer
    $installer = Get-ChildItem ".\src-tauri\target\release\bundle\nsis\*.exe" -ErrorAction SilentlyContinue | Sort-Object LastWriteTime -Descending | Select-Object -First 1
    if (-not $installer) { Write-Host "[HOLD] No NSIS .exe found." -ForegroundColor Yellow; exit 3 }
    Write-Host "[PASS] $($installer.FullName)" -ForegroundColor Green
  }
}
