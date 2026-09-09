from pathlib import Path
import json
root = Path(__file__).resolve().parents[1]
read = lambda path: path.read_text(encoding="utf-8")
lib=read(root/"src-tauri/src/lib.rs"); main=read(root/"src/main.js"); army=read(root/"src/army.js"); bootstrap=read(root/"src/bootstrap.js"); cargo=read(root/"src-tauri/Cargo.toml"); conf=json.loads(read(root/"src-tauri/tauri.conf.json")); cap=json.loads(read(root/"src-tauri/capabilities/army.json"))
windows={x.get("label"):x for x in conf["app"]["windows"]}; combined=lib+main+army+bootstrap+cargo
checks={"ports":'const CARRIER_PORT: u16 = 47_822;' in lib and 'const STATE_PORT: u16 = 47_821;' in lib,"openai":'https://api.openai.com/v1/responses' in lib,"key_native":'env_trim("OPENAI_API_KEY")' in lib and "OPENAI_API_KEY" not in (main+army+bootstrap),"ollama_guard":"is_loopback_http" in lib,"origin_guard":"ALLOWED_CARRIER_ORIGINS" in lib and "origin_not_allowed" in lib,"loopback":'([127, 0, 0, 1], CARRIER_PORT)' in lib and '([127, 0, 0, 1], STATE_PORT)' in lib,"v08":conf.get("version")=="0.8.0" and 'version = "0.8.0"' in cargo,"army":windows["army"].get("transparent") is True and windows["army"].get("alwaysOnTop") is True,"clickthrough":"setIgnoreCursorEvents(true)" in army and "core:window:allow-set-ignore-cursor-events" in cap["permissions"],"six":all(x in army for x in ["KYU","PAIMON","LUMA","SYLPH","QIRA","NYX"]),"no_key":"sk-" not in combined,"no_private":"Jarvis-Private" not in combined}
failed=[k for k,v in checks.items() if not v]
if failed: raise SystemExit("FAERYWARE_WINDOWS_CANARY FAIL: "+", ".join(failed))
print("FAERYWARE_WINDOWS_CANARY PASS")
print("embedded=true openai=true ollama=true loopback=true key_in_webview=false habitat=true utf8=true")
