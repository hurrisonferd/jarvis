@echo off
echo JARVIS Cloudflare Tunnel
echo ========================
echo Requires: cloudflared.exe on PATH
echo Download: https://developers.cloudflare.com/cloudflare-one/connections/connect-networks/downloads/
echo.
echo Starting ephemeral tunnel to http://localhost:7777 ...
echo (Cloudflare will print a public https:// URL below)
echo.
cloudflared tunnel --url http://localhost:7777
echo.
echo == NAMED TUNNEL (stable URL across restarts) ==
echo 1. cloudflared tunnel login
echo 2. cloudflared tunnel create jarvis
echo 3. cloudflared tunnel route dns jarvis ^<subdomain.yourdomain.com^>
echo 4. cloudflared tunnel run jarvis
pause
