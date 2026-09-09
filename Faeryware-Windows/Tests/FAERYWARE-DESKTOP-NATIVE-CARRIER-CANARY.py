from pathlib import Path
import json

root = Path(__file__).resolve().parents[1]
lib = (root / "src-tauri" / "src" / "lib.rs").read_text(encoding="utf-8")
main = (root / "src" / "main.js").read_text(encoding="utf-8")
army = (root / "src" / "army.js").read_text(encoding="utf-8")
bootstrap = (root / "src" / "bootstrap.js").read_text(encoding="utf-8")
army_css = (root / "src" / "army.css").read_text(encoding="utf-8")
cargo = (root / "src-tauri" / "Cargo.toml").read_text(encoding="utf-8")
conf = json.loads((root / "src-tauri" / "tauri.conf.json").read_text(encoding="utf-8"))
army_cap = json.loads((root / "src-tauri" / "capabilities" / "army.json").read_text(encoding="utf-8"))

windows = {item.get("label"): item for item in conf.get("app", {}).get("windows", [])}
army_window = windows.get("army", {})
combined = lib + main + army + bootstrap + army_css + cargo

checks = {
    "carrier_port": 'const CARRIER_PORT: u16 = 47_822;' in lib,
    "state_port": 'const STATE_PORT: u16 = 47_821;' in lib,
    "openai_endpoint_fixed": 'https://api.openai.com/v1/responses' in lib,
    "key_native_only": 'env_trim("OPENAI_API_KEY")' in lib and "OPENAI_API_KEY" not in (main + army + bootstrap),
    "ollama_guard": "is_loopback_http" in lib,
    "origin_allowlist": "ALLOWED_CARRIER_ORIGINS" in lib and "origin_not_allowed" in lib,
    "loopback_bind": '([127, 0, 0, 1], CARRIER_PORT)' in lib and '([127, 0, 0, 1], STATE_PORT)' in lib,
    "reqwest": 'reqwest = ' in cargo,
    "frontend_localhost": 'http://127.0.0.1:47822/chat' in main,
    "v07": conf.get("version") == "0.7.0",
    "army_window": army_window.get("url") == "index.html?surface=army" and army_window.get("transparent") is True and army_window.get("alwaysOnTop") is True and army_window.get("skipTaskbar") is True and army_window.get("fullscreen") is True,
    "army_clickthrough": "setIgnoreCursorEvents(true)" in army and "core:window:allow-set-ignore-cursor-events" in army_cap.get("permissions", []),
    "army_six": all(name in army for name in ["KYU", "PAIMON", "LUMA", "SYLPH", "QIRA", "NYX"]),
    "army_state_bus": "http://127.0.0.1:47821/state" in army,
    "army_bootstrap": 'params.get("surface") === "army"' in bootstrap,
    "no_literal_key": "sk-" not in combined,
    "no_private_locator": "Jarvis-Private" not in combined,
}
failed = [name for name, ok in checks.items() if not ok]
if failed:
    raise SystemExit("FAERYWARE_WINDOWS_CANARY FAIL: " + ", ".join(failed))
print("FAERYWARE_WINDOWS_CANARY PASS")
print("embedded=true openai=true ollama=true loopback=true origin_guard=true key_in_webview=false army=true clickthrough=true")
