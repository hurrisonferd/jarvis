"""Smoke test for jarvis_mcp_server — the safety net for the monolith carve.

Boots the FastAPI app in-process (no network) and asserts the route surface and
the served templates are intact. Run before and after every extraction:

    python3 scripts/smoke_server.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import jarvis_mcp_server as m

EXPECTED_MIN_ROUTES = 30
REQUIRED_PATHS = {
    "/", "/health", "/rpc", "/sse",
    "/grid", "/dashboard", "/live", "/gameboy", "/intake",
}
REQUIRED_TEMPLATES = {
    "_GAMEBOY_HTML", "_DASHBOARD_HTML", "_GALLERY_HTML",
    "_LIVE_HTML", "_INTAKE_HTML", "_GAMEBOY_SW_JS",
}

failures = []

paths = {getattr(r, "path", None) for r in m.app.routes}
missing = REQUIRED_PATHS - paths
if missing:
    failures.append(f"missing routes: {sorted(missing)}")
if len(m.app.routes) < EXPECTED_MIN_ROUTES:
    failures.append(f"route count {len(m.app.routes)} < {EXPECTED_MIN_ROUTES}")

for name in sorted(REQUIRED_TEMPLATES):
    val = getattr(m, name, None)
    if not isinstance(val, str) or len(val) < 100:
        failures.append(f"template {name} missing or too small")

if failures:
    print("SMOKE FAIL")
    for f in failures:
        print("  -", f)
    sys.exit(1)

print(f"SMOKE OK — {len(m.app.routes)} routes, {len(REQUIRED_TEMPLATES)} templates intact")
