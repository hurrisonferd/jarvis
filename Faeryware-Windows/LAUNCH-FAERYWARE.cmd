@echo off
setlocal
cd /d "%~dp0"
echo [FAERYWARE] Starting Desktop Colony...
powershell.exe -NoLogo -NoProfile -ExecutionPolicy Bypass -File ".\RUN-WINDOWS.ps1" -Mode dev
if errorlevel 1 pause
