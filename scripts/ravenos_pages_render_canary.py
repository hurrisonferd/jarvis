#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import os
import time
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = "https://hurrisonferd.github.io/jarvis"
TARGETS = {
    "ravenos-public-haunt.json": ROOT / "ravenos-public-haunt.json",
    "ravenos-haunt.html": ROOT / "ravenos-haunt.html",
    "ravenos-gameboy.html": ROOT / "ravenos-gameboy.html",
    "ravenos-home.html": ROOT / "ravenos-home.html",
    "ravenos-home.webmanifest": ROOT / "ravenos-home.webmanifest",
    "ravenos-home-sw.js": ROOT / "ravenos-home-sw.js",
    "ravenos-public-contract.js": ROOT / "ravenos-public-contract.js",
}
ATTEMPTS = 12
DELAY_SECONDS = 5


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def fetch_live(name: str, nonce: str) -> bytes:
    url = f"{BASE}/{name}?render_proof={nonce}"
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": "RavenOS-Pages-Render-Canary/1.1",
            "Cache-Control": "no-cache",
            "Pragma": "no-cache",
        },
    )
    with urllib.request.urlopen(req, timeout=20) as response:
        if response.status != 200:
            raise RuntimeError(f"HTTP_{response.status}:{name}")
        return response.read()


def validate_packet(data: bytes) -> dict:
    packet = json.loads(data.decode("utf-8"))
    assert packet["schema"] == "ravenos.public-handheld.projection.v1"
    assert packet["target"] == "JARVIS_HANDHELD"
    assert packet["host_url"] == "https://hurrisonferd.github.io/jarvis/"
    assert packet["packet_id"] == "PUBLICHAUNT-9BC99CA80A601577E37E1A8E"
    assert packet["privacy"]["whitelist_only"] is True
    assert packet["privacy"]["secrets_or_tokens_included"] is False
    assert packet["proof"]["automatic_host_invocation_proven"] is False
    assert packet["proof"]["effect_authority"] is False
    return packet


def main() -> int:
    head = os.environ.get("PROOF_HEAD", "UNKNOWN")
    local = {name: path.read_bytes() for name, path in TARGETS.items()}
    last_error = "UNSET"

    for attempt in range(1, ATTEMPTS + 1):
        nonce = f"{head}-{attempt}-{int(time.time())}"
        try:
            live = {name: fetch_live(name, nonce) for name in TARGETS}
            mismatches = [name for name in TARGETS if live[name] != local[name]]
            if mismatches:
                raise AssertionError("STALE_OR_DIFFERENT_BYTES:" + ",".join(sorted(mismatches)))

            packet = validate_packet(live["ravenos-public-haunt.json"])
            for name in ("ravenos-haunt.html", "ravenos-gameboy.html", "ravenos-home.html"):
                text = live[name].decode("utf-8")
                assert "./ravenos-public-contract.js" in text
                assert "RavenOSPublicContract.validatePacket" in text
                assert "Jarvis-Private" not in text
                assert "./ravenos-public-haunt.json" in text

            home = live["ravenos-home.html"].decode("utf-8")
            assert "./ravenos-home.webmanifest" in home
            assert "./ravenos-home-sw.js" in home
            assert "RAVEN → JOKEROS → BOOTOS → OWNERS → FAIRYOS" in home
            assert "https://github.com/hurrisonferd/RavenOS-Home/releases/latest" in home

            manifest = json.loads(live["ravenos-home.webmanifest"].decode("utf-8"))
            assert manifest["name"] == "RavenOS Home"
            assert manifest["start_url"] == "./ravenos-home.html"
            assert manifest["display"] == "standalone"

            service_worker = live["ravenos-home-sw.js"].decode("utf-8")
            assert "ravenos-public-haunt.json" in service_worker
            assert "cache:'no-store'" in service_worker

            contract = live["ravenos-public-contract.js"].decode("utf-8")
            assert "ravenos.public-handheld.contract-validator.v1" in contract
            assert "PACKET_ID_MISMATCH" in contract
            assert "PRIVACY_KEYS" in contract
            assert "PROOF_KEYS" in contract

            print("RAVENOS_PAGES_RENDER_CANARY PASS")
            print(
                json.dumps(
                    {
                        "schema": "ravenos.public-handheld.pages-render-canary.v2",
                        "state": "PASS",
                        "proof_head": head,
                        "host": BASE,
                        "home_url": BASE + "/ravenos-home.html",
                        "packet_id": packet["packet_id"],
                        "http_targets_verified": sorted(TARGETS),
                        "served_bytes_match_deployment_head": True,
                        "strict_validator_served": True,
                        "home_pwa_surface_verified": True,
                        "private_repo_literal_absent": True,
                        "automatic_host_invocation_proven": False,
                        "effect_authority": False,
                        "sha256": {name: sha256(live[name]) for name in sorted(live)},
                    },
                    indent=2,
                    sort_keys=True,
                )
            )
            return 0
        except Exception as exc:
            last_error = f"{type(exc).__name__}:{exc}"
            print(f"render attempt {attempt}/{ATTEMPTS} not settled: {last_error}")
            if attempt < ATTEMPTS:
                time.sleep(DELAY_SECONDS)

    raise SystemExit(f"RAVENOS_PAGES_RENDER_CANARY FAIL: {last_error}")


if __name__ == "__main__":
    raise SystemExit(main())
