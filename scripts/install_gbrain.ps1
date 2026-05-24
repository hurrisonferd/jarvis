$ErrorActionPreference = "Stop"

if (-not (Get-Command bun -ErrorAction SilentlyContinue)) {
    $wingetBun = Get-ChildItem -Path "$env:LOCALAPPDATA\Microsoft\WinGet\Packages" -Recurse -Filter bun.exe -ErrorAction SilentlyContinue |
        Select-Object -First 1 -ExpandProperty FullName

    if ($wingetBun) {
        $env:PATH = "$(Split-Path $wingetBun);$env:USERPROFILE\.bun\bin;$env:PATH"
    } else {
        Write-Host "Bun is required for the GBrain CLI."
        Write-Host "Install Bun first, then re-run this script:"
        Write-Host "  winget install -e --id Oven-sh.Bun --source winget"
        exit 1
    }
}

bun install -g github:garrytan/gbrain

$env:PATH = "$env:USERPROFILE\.bun\bin;$env:PATH"

if ($env:OPENAI_API_KEY -or $env:ZEROENTROPY_API_KEY -or $env:VOYAGE_API_KEY) {
    gbrain init --pglite
} else {
    gbrain init --pglite --no-embedding
}

gbrain doctor --fast
