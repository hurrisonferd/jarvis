@echo off
REM JARVIS Tunnel — exposes localhost:7777 via Cloudflare Tunnel
REM
REM First-time setup:
REM   1. Download cloudflared: https://developers.cloudflare.com/cloudflare-one/connections/connect-networks/downloads/
REM   2. Place cloudflared.exe anywhere on PATH (or same folder as this file)
REM   3. Run this script — Cloudflare prints a public https:// URL to the console
REM
REM The URL changes each run (free tier). For a stable URL, run:
REM   cloudflared tunnel login
REM   cloudflared tunnel create jarvis
REM   cloudflared tunnel route dns jarvis <your-subdomain>.<domain>
REM   cloudflared tunnel run jarvis
REM
REM ngrok alternative (if you prefer ngrok):
REM   ngrok http 7777
REM   ngrok http --domain=<your-static-domain>.ngrok-free.app 7777

echo Starting Cloudflare Tunnel for JARVIS MCP (localhost:7777)...
cloudflared tunnel --url http://localhost:7777
