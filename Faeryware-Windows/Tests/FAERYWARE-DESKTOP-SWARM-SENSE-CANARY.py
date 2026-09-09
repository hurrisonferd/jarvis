from pathlib import Path
import json

root = Path(__file__).resolve().parents[1]
army = (root / "src" / "army.js").read_text(encoding="utf-8")
css = (root / "src" / "army.css").read_text(encoding="utf-8")
cap = json.loads((root / "src-tauri" / "capabilities" / "default.json").read_text(encoding="utf-8"))
conf = json.loads((root / "src-tauri" / "tauri.conf.json").read_text(encoding="utf-8"))
pkg = json.loads((root / "package.json").read_text(encoding="utf-8"))
lib = (root / "src-tauri" / "src" / "lib.rs").read_text(encoding="utf-8")

permissions = set(cap.get("permissions", []))
windows = set(cap.get("windows", []))
checks = {
    "version_config": conf.get("version") == "0.7.0",
    "version_package": pkg.get("version") == "0.7.0",
    "army_window": any(w.get("label") == "army" and w.get("transparent") and w.get("alwaysOnTop") for w in conf.get("app", {}).get("windows", [])),
    "army_capability": "army" in windows,
    "ignore_cursor_permission": "core:window:allow-set-ignore-cursor-events" in permissions,
    "cursor_permission": "core:window:allow-cursor-position" in permissions,
    "monitors_permission": "core:window:allow-available-monitors" in permissions,
    "cursor_sensor": "cursorPosition" in army and "senseCursor" in army,
    "monitor_sensor": "availableMonitors" in army and "refreshTopology" in army,
    "physics_loop": "requestAnimationFrame(frame)" in army and "applySeparation" in army,
    "army_modes": all(f'"{mode}"' in army for mode in ["ROAM", "HUNT", "FLOCK", "ORBIT", "REST", "SCATTER"]),
    "six_fae": all(name in army for name in ["KYU", "PAIMON", "LUMA", "SYLPH", "QIRA", "NYX"]),
    "kyu_pink": '#ff4fba' in army,
    "paimon_green": '#57d96b' in army,
    "eighteen_echoes": "length: 3" in army and "ORDER.map" in army,
    "click_through_call": "setIgnoreCursorEvents(true)" in army,
    "no_screen_capture": "screen" not in permissions and "capture" not in permissions,
    "state_bus_loopback": '([127, 0, 0, 1], STATE_PORT)' in lib,
    "carrier_loopback": '([127, 0, 0, 1], CARRIER_PORT)' in lib,
    "css_gpu_transform": "translate3d" in css and "will-change:transform" in css,
}
failed = [name for name, ok in checks.items() if not ok]
if failed:
    raise SystemExit("FAERYWARE_SWARM_SENSE_CANARY FAIL: " + ", ".join(failed))
print("FAERYWARE_SWARM_SENSE_CANARY PASS")
print("six_fae=true echoes=18 cursor=true monitors=true physics=raf modes=6 click_through=declared remote_listen=false")
