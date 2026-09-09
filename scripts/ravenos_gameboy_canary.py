#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PACKET = ROOT / "ravenos-public-haunt.json"
HANDHELD = ROOT / "ravenos-gameboy.html"
INDEX = ROOT / "index.html"

FAE = {"KYU", "PAIMON", "LUMA", "SYLPH", "QIRA", "NYX"}
SCREENS = {
    "GOD CONTROL",
    "GOD MAP",
    "FAIRYOS",
    "HAUNT STATE",
    "RAVENOS OFFICE",
    "BLACK BOX",
    "PUBLIC BOUNDARY",
}
FORBIDDEN_PACKET_KEYS = {
    "transaction_id",
    "source_event_id",
    "source_snapshot",
    "haunt_id",
    "event_id",
    "evidence_refs",
    "owner_truth_ref",
    "receipt_path",
    "private_source_path",
}


def walk_keys(value):
    if isinstance(value, dict):
        for key, item in value.items():
            yield str(key)
            yield from walk_keys(item)
    elif isinstance(value, list):
        for item in value:
            yield from walk_keys(item)


def main() -> int:
    assert PACKET.is_file() and HANDHELD.is_file() and INDEX.is_file()
    packet = json.loads(PACKET.read_text(encoding="utf-8"))
    html = HANDHELD.read_text(encoding="utf-8")
    launcher = INDEX.read_text(encoding="utf-8")

    assert packet["schema"] == "ravenos.public-handheld.projection.v1"
    assert packet["target"] == "JARVIS_HANDHELD"
    assert packet["privacy"]["whitelist_only"] is True
    assert packet["privacy"]["source_paths_included"] is False
    assert packet["privacy"]["transaction_ids_included"] is False
    assert packet["privacy"]["secrets_or_tokens_included"] is False
    assert packet["privacy"]["private_repo_contact_from_browser"] is False

    god = packet["god_control"]
    assert god["registered_ghost_ports"] == 24
    assert god["proven_native_owners"] == 6
    assert god["staged_native_candidates"] == 4
    assert god["haunt_rooms"] == 9
    assert god["ravenos_core_roots"] == 80
    assert god["ravenos_core_source_boundaries_settled"] == 80
    assert god["fairyos_power_mode"] == "MAX_POWER"
    assert god["fairyos_classification"] == "BOUNDED_GOD_OBJECTS"
    assert god["fairyos_roster_count"] == 6
    assert god["effect_authority"] is False

    members = {row["member"] for row in packet["fae"]}
    assert members == FAE
    assert len(packet["fae"]) == 6
    assert len(packet["rooms"]) == 9
    assert all(row["state"] == "SOURCE_BOUND" for row in packet["rooms"])
    assert packet["proof"]["effect_authority_amplification"] is False
    assert packet["proof"]["automatic_external_host_invocation_proven"] is False
    assert packet["proof"]["public_packet_is_live_private_runtime"] is False

    forbidden = FORBIDDEN_PACKET_KEYS.intersection(set(walk_keys(packet)))
    assert not forbidden, sorted(forbidden)

    for screen in SCREENS:
        assert screen in html, screen
    for member in FAE:
        assert member in PACKET.read_text(encoding="utf-8"), member
    assert "BOUNDED_GOD_OBJECTS" in html
    assert "MAX POWER" in html
    assert "EFFECT BUDGET 0" in html
    assert "fair yos" not in html.lower()
    assert "Jarvis-Private" not in html
    assert "./ravenos-public-haunt.json" in html
    assert "./ravenos-gameboy.html" in launcher

    print("RAVENOS_GAMEBOY_CANARY PASS")
    print("ports=24 native=6 staged=4 fae=6 rooms=9 public_private_contact=false authority_amplification=false")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
