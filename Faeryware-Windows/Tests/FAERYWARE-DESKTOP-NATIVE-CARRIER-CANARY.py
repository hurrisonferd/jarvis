from pathlib import Path
import json

root = Path(__file__).resolve().parents[1]
lib = (root / "src-tauri" / "src" / "lib.rs").read_text(encoding="utf-8")
main = (root / "src" / "main.js").read_text(encoding="utf-8")
cargo = (root / "src-tauri" / "Cargo.toml").read_text(encoding="utf-8")
conf = json.loads((root / "src-tauri" / "tauri.conf.json").read_text(encoding="utf-8"))

checks = {
    "carrier_port": 'const CARRIER_PORT: u16 = 47_822;' in lib,
    "state_port": 'const STATE_PORT: u16 = 47_821;' in lib,
    "openai_endpoint_fixed": 'https://api.openai.com/v1/responses' in lib,
    "key_native_only": 'env_trim("OPENAI_API_KEY")' in lib and "OPENAI_API_KEY" not in main,
    "ollama_guard": "is_loopback_http" in lib,
    "origin_allowlist": "ALLOWED_CARRIER_ORIGINS" in lib and "origin_not_allowed" in lib,
    "loopback_bind": '([127, 0, 0, 1], CARRIER_PORT)' in lib and '([127, 0, 0, 1], STATE_PORT)' in lib,
    "reqwest": 'reqwest = ' in cargo,
    "frontend_localhost": 'http://127.0.0.1:47822/chat' in main,
    "v05": conf.get("version") == "0.5.0",
    "no_literal_key": "sk-" not in (lib + main + cargo),
    "no_private_locator": "Jarvis-Private" not in (lib + main + cargo),
}
failed = [name for name, ok in checks.items() if not ok]
if failed:
    raise SystemExit("FAERYWARE_WINDOWS_CANARY FAIL: " + ", ".join(failed))
print("FAERYWARE_WINDOWS_CANARY PASS")
print("embedded=true openai=true ollama=true loopback=true origin_guard=true key_in_webview=false")
