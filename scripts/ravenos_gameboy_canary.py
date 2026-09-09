#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PACKET = ROOT / "ravenos-public-haunt.json"
GAMEBOY = ROOT / "ravenos-gameboy.html"
HAUNT = ROOT / "ravenos-haunt.html"
CONTRACT = ROOT / "ravenos-public-contract.js"
INDEX = ROOT / "index.html"

TOP = {"schema","target","host_url","state","god_control","fae","rooms","privacy","proof","packet_id"}
GOD = {"base_object_count","effective_object_count","registered_ghost_ports","proven_native_owners","staged_native_candidates","active_hold_count","resolved_hold_count"}
FAE = {"member","stamp","color_emoji","glyph","accent"}
ROOM = {"room","state","atmosphere","ghost_count","hold_count","absence_count","material_fae"}
PRIVACY = {"whitelist_only","source_paths_included","transaction_ids_included","source_event_ids_included","haunt_ids_included","flight_ids_included","hashes_included","receipt_bodies_included","owner_event_bodies_included","ledger_entries_included","flight_history_rows_included","secrets_or_tokens_included"}
PROOF = {"sanitized_projection_source_bound","public_write_executed","public_host_render_proven","automatic_host_invocation_proven","effect_authority"}
HOUSE_STATES = {"SETTLED","HOLD","QUIET","ACTIVE","RESIDUAL"}
ROOM_STATES = {"ACTIVE","HOLD","RESIDUAL","QUIET"}
ATMOSPHERES = {"ACTIVE_HAUNT","LOCKED_HAUNT","RESIDUAL_ECHO","QUIET"}
LEGACY_OR_FORBIDDEN_KEYS = {
    "transaction_id","source_event_id","source_snapshot","haunt_id","flight_id","event_id","evidence_refs","owner_truth_ref","receipt_path","private_source_path",
    "ravenos_platform","ravenos_core_roots","ravenos_core_source_boundaries_settled","fairyos_power_mode","fairyos_classification","fairyos_roster_count","haunt_rooms","god_map","god_tools","read_commands","transaction_spine","power","private_repo_contact_from_browser"
}


def walk_keys(value):
    if isinstance(value, dict):
        for key, item in value.items():
            yield str(key)
            yield from walk_keys(item)
    elif isinstance(value, list):
        for item in value:
            yield from walk_keys(item)


def canonical(value) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def expected_packet_id(packet: dict) -> str:
    identity = {key: value for key, value in packet.items() if key != "packet_id"}
    return "PUBLICHAUNT-" + hashlib.sha256(canonical(identity)).hexdigest()[:24].upper()


def main() -> int:
    for path in (PACKET, GAMEBOY, HAUNT, CONTRACT, INDEX):
        assert path.is_file(), path

    packet = json.loads(PACKET.read_text(encoding="utf-8"))
    gameboy = GAMEBOY.read_text(encoding="utf-8")
    haunt = HAUNT.read_text(encoding="utf-8")
    contract = CONTRACT.read_text(encoding="utf-8")
    launcher = INDEX.read_text(encoding="utf-8")

    assert set(packet) == TOP
    assert packet["schema"] == "ravenos.public-handheld.projection.v1"
    assert packet["target"] == "JARVIS_HANDHELD"
    assert packet["host_url"] == "https://hurrisonferd.github.io/jarvis/"
    assert packet["state"] in HOUSE_STATES

    god = packet["god_control"]
    assert set(god) == GOD
    assert all(isinstance(god[key], int) and not isinstance(god[key], bool) and god[key] >= 0 for key in GOD)

    assert isinstance(packet["fae"], list)
    for row in packet["fae"]:
        assert set(row) == FAE
        assert all(isinstance(row[key], str) for key in FAE)

    assert isinstance(packet["rooms"], list)
    for row in packet["rooms"]:
        assert set(row) == ROOM
        assert row["state"] in ROOM_STATES
        assert row["atmosphere"] in ATMOSPHERES
        assert all(isinstance(row[key], int) and not isinstance(row[key], bool) and row[key] >= 0 for key in ("ghost_count","hold_count","absence_count"))
        assert isinstance(row["material_fae"], list) and all(isinstance(name, str) for name in row["material_fae"])

    privacy = packet["privacy"]
    assert set(privacy) == PRIVACY
    assert privacy["whitelist_only"] is True
    assert all(privacy[key] is False for key in PRIVACY if key != "whitelist_only")

    proof = packet["proof"]
    assert set(proof) == PROOF
    assert proof["sanitized_projection_source_bound"] is True
    assert proof["public_write_executed"] is False
    assert proof["public_host_render_proven"] is False
    assert proof["automatic_host_invocation_proven"] is False
    assert proof["effect_authority"] is False

    assert packet["packet_id"] == expected_packet_id(packet)
    assert packet["packet_id"].startswith("PUBLICHAUNT-")

    forbidden = LEGACY_OR_FORBIDDEN_KEYS.intersection(set(walk_keys(packet)))
    assert not forbidden, sorted(forbidden)

    for html in (gameboy, haunt):
        assert "./ravenos-public-contract.js" in html
        assert "RavenOSPublicContract.validatePacket" in html
        assert "Jarvis-Private" not in html
        assert "./ravenos-public-haunt.json" in html

    assert "ravenos.public-handheld.contract-validator.v1" in contract
    assert "PACKET_ID_MISMATCH" in contract
    assert "GOD_CONTROL_KEYS" in contract
    assert "PRIVACY_KEYS" in contract
    assert "PROOF_KEYS" in contract
    assert "./ravenos-gameboy.html" in launcher

    print("RAVENOS_PUBLIC_HANDHELD_CANARY PASS")
    print(
        f"packet={packet['packet_id']} state={packet['state']} ports={god['registered_ghost_ports']} "
        f"native={god['proven_native_owners']} staged={god['staged_native_candidates']} "
        "strict_nested_whitelist=true packet_identity_verified=true private_fallback=false authority_amplification=false"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
