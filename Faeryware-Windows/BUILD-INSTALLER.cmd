@echo off
setlocal
cd /d "%~dp0"
echo [FAERYWARE] Building Windows installer...
powershell.exe -NoLogo -NoProfile -ExecutionPolicy Bypass -File ".\RUN-WINDOWS.ps1" -Mode installer
pause
