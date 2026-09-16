#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PACKET = ROOT / "ravenos-public-haunt.json"
GAMEBOY = ROOT / "ravenos-gameboy.html"
HAUNT = ROOT / "ravenos-haunt.html"
CONTRACT = ROOT / "ravenos-public-contract.js"
POCKET_REGISTRY = ROOT / "ravenos-pocket-cartridges.json"
POCKET_CONTRACT = ROOT / "ravenos-pocket-contract.js"
POCKET_GOBLIN = ROOT / "ravenos-pocket-goblin.js"
POCKET_RUNTIME = ROOT / "ravenos-gameboy-v4.js"
INDEX = ROOT / "index.html"

TOP = {"schema","target","host_url","state","platform","god_control","kingdom","office","topology","readiness","fae","rooms","privacy","proof","packet_id"}
PLATFORM = {"ravenos_version","systemsos_version","update_version","core_root_count","formal_version_owner_count","presentation_standard","awareness_bound","bios_effect_authority"}
GOD = {"base_object_count","effective_object_count","registered_ghost_ports","proven_native_owners","staged_native_candidates","active_hold_count","resolved_hold_count"}
KINGDOM = {"known_member_count","members","iso_owner_count","core_digi_fae_count","fae_court_count","light_member_count","membership_is_live_presence"}
OFFICE = {"generation","road_os_version","office_max_generation","owner_router_generation","effect_bypass","source_active"}
TOPOLOGY = {"base_object_count","effective_object_count","replacement_count","addition_count","haunt_room_count"}
READINESS = {"runner_hold_active","flight_history_append_only","flight_view_mode_count","current_absence_radar","newest_finalized_flight_owns_current_state","effect_budget","owner_invocation"}
FAE = {"member","stamp","color_emoji","glyph","accent"}
ROOM = {"room","state","atmosphere","ghost_count","hold_count","absence_count","material_fae"}
PRIVACY = {"whitelist_only","source_paths_included","transaction_ids_included","source_event_ids_included","haunt_ids_included","flight_ids_included","hashes_included","receipt_bodies_included","owner_event_bodies_included","ledger_entries_included","flight_history_rows_included","secrets_or_tokens_included"}
PROOF = {"sanitized_projection_source_bound","public_write_executed","public_host_render_proven","automatic_host_invocation_proven","effect_authority"}
HOUSE_STATES = {"SETTLED","HOLD","QUIET","ACTIVE","RESIDUAL"}
ROOM_STATES = {"ACTIVE","HOLD","RESIDUAL","QUIET"}
ATMOSPHERES = {"ACTIVE_HAUNT","LOCKED_HAUNT","RESIDUAL_ECHO","QUIET"}

REGISTRY_TOP = {"schema","effect_authority","effect_budget","browser_scene_scope","cartridges","providers","laws"}
CARTRIDGE = {"id","label","icon","class","order","status","owner_label","copy","packet_sections","views","actions","proof"}
PROVIDER = {"connected","label","capabilities"}
PROVIDER_NAMES = {"browser","android","windows"}
ALLOWED_ACTIONS = {"READ","INSPECT","SIMULATE"}

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


def require_exact(obj: dict, keys: set[str], name: str) -> None:
    assert isinstance(obj, dict), name
    assert set(obj) == keys, f"{name}_KEYS:{sorted(set(obj) ^ keys)}"


def validate_packet(packet: dict) -> None:
    require_exact(packet, TOP, "TOP")
    assert packet["schema"] == "ravenos.public-handheld.projection.v2"
    assert packet["target"] == "JARVIS_HANDHELD"
    assert packet["host_url"] == "https://hurrisonferd.github.io/jarvis/"
    assert packet["state"] in HOUSE_STATES

    require_exact(packet["platform"], PLATFORM, "PLATFORM")
    assert packet["platform"]["bios_effect_authority"] is False

    god = packet["god_control"]
    require_exact(god, GOD, "GOD_CONTROL")
    assert all(isinstance(god[key], int) and not isinstance(god[key], bool) and god[key] >= 0 for key in GOD)

    kingdom = packet["kingdom"]
    require_exact(kingdom, KINGDOM, "KINGDOM")
    assert isinstance(kingdom["members"], list) and all(isinstance(x, str) and x for x in kingdom["members"])
    assert kingdom["known_member_count"] == len(kingdom["members"])
    assert kingdom["membership_is_live_presence"] is False

    require_exact(packet["office"], OFFICE, "OFFICE")
    assert packet["office"]["effect_bypass"] is False
    require_exact(packet["topology"], TOPOLOGY, "TOPOLOGY")

    readiness = packet["readiness"]
    require_exact(readiness, READINESS, "READINESS")
    assert readiness["effect_budget"] == 0
    assert readiness["owner_invocation"] is False

    assert isinstance(packet["fae"], list)
    for row in packet["fae"]:
        require_exact(row, FAE, "FAE")
        assert all(isinstance(row[key], str) for key in FAE)

    assert isinstance(packet["rooms"], list)
    for row in packet["rooms"]:
        require_exact(row, ROOM, "ROOM")
        assert row["state"] in ROOM_STATES
        assert row["atmosphere"] in ATMOSPHERES
        assert all(isinstance(row[key], int) and not isinstance(row[key], bool) and row[key] >= 0 for key in ("ghost_count","hold_count","absence_count"))
        assert isinstance(row["material_fae"], list) and all(isinstance(name, str) for name in row["material_fae"])

    privacy = packet["privacy"]
    require_exact(privacy, PRIVACY, "PRIVACY")
    assert privacy["whitelist_only"] is True
    assert all(privacy[key] is False for key in PRIVACY if key != "whitelist_only")

    proof = packet["proof"]
    require_exact(proof, PROOF, "PROOF")
    assert proof["sanitized_projection_source_bound"] is True
    assert proof["public_write_executed"] is False
    assert proof["automatic_host_invocation_proven"] is False
    assert proof["effect_authority"] is False

    assert packet["packet_id"] == expected_packet_id(packet)
    assert packet["packet_id"].startswith("PUBLICHAUNT-")
    forbidden = LEGACY_OR_FORBIDDEN_KEYS.intersection(set(walk_keys(packet)))
    assert not forbidden, sorted(forbidden)


def validate_registry(registry: dict) -> None:
    require_exact(registry, REGISTRY_TOP, "REGISTRY_TOP")
    assert registry["schema"] == "ravenos.pocket.cartridge-registry.public.v1"
    assert registry["effect_authority"] is False
    assert registry["effect_budget"] == 0
    assert registry["browser_scene_scope"] == "POCKET_PAGE_ONLY"
    carts = registry["cartridges"]
    assert isinstance(carts, list) and 1 <= len(carts) <= 64
    ids = []
    orders = []
    for cart in carts:
        require_exact(cart, CARTRIDGE, "CARTRIDGE")
        assert isinstance(cart["id"], str) and cart["id"]
        assert isinstance(cart["order"], int) and not isinstance(cart["order"], bool)
        assert all(isinstance(cart[k], str) and cart[k] for k in ("label","icon","class","status","owner_label","copy","proof"))
        assert all(isinstance(cart[k], list) and all(isinstance(x, str) and x for x in cart[k]) for k in ("packet_sections","views","actions"))
        assert set(cart["actions"]).issubset(ALLOWED_ACTIONS)
        assert "REQUEST_EFFECT" not in cart["actions"]
        ids.append(cart["id"]); orders.append(cart["order"])
    assert len(ids) == len(set(ids))
    assert orders == sorted(orders) and len(orders) == len(set(orders))
    assert set(registry["providers"]) == PROVIDER_NAMES
    for name, provider in registry["providers"].items():
        require_exact(provider, PROVIDER, f"PROVIDER_{name}")
        assert isinstance(provider["connected"], bool)
        assert isinstance(provider["label"], str) and provider["label"]
        assert isinstance(provider["capabilities"], list) and all(isinstance(x, str) and x for x in provider["capabilities"])
    assert registry["providers"]["browser"]["connected"] is True
    assert registry["providers"]["android"]["connected"] is False
    assert registry["providers"]["windows"]["connected"] is False
    assert isinstance(registry["laws"], list) and all(isinstance(x, str) and x for x in registry["laws"])


def main() -> int:
    paths = (PACKET, GAMEBOY, HAUNT, CONTRACT, POCKET_REGISTRY, POCKET_CONTRACT, POCKET_GOBLIN, POCKET_RUNTIME, INDEX)
    for path in paths:
        assert path.is_file(), path

    packet = json.loads(PACKET.read_text(encoding="utf-8"))
    registry = json.loads(POCKET_REGISTRY.read_text(encoding="utf-8"))
    gameboy = GAMEBOY.read_text(encoding="utf-8")
    haunt = HAUNT.read_text(encoding="utf-8")
    contract = CONTRACT.read_text(encoding="utf-8")
    pocket_contract = POCKET_CONTRACT.read_text(encoding="utf-8")
    pocket_goblin = POCKET_GOBLIN.read_text(encoding="utf-8")
    pocket_runtime = POCKET_RUNTIME.read_text(encoding="utf-8")
    launcher = INDEX.read_text(encoding="utf-8")

    validate_packet(packet)
    validate_registry(registry)

    assert "./ravenos-public-contract.js" in gameboy
    assert "./ravenos-pocket-contract.js" in gameboy
    assert "./ravenos-pocket-goblin.js" in gameboy
    assert "./ravenos-gameboy-v4.js" in gameboy
    assert "Jarvis-Private" not in gameboy

    assert "./ravenos-public-contract.js" in haunt
    assert "RavenOSPublicContract.validatePacket" in haunt
    assert "./ravenos-public-haunt.json" in haunt
    assert "Jarvis-Private" not in haunt

    assert "ravenos.public-handheld.contract-validator.v2" in contract
    assert "KINGDOM_PRESENCE_CLAIM" in contract
    assert "READINESS_EFFECT_BUDGET" in contract
    assert "PACKET_ID_MISMATCH" in contract

    assert "ravenos.pocket.cartridge-contract.v1" in pocket_contract
    assert "PUBLIC_EFFECT_ACTION" in pocket_contract
    assert "PROVIDER_CONNECTION_CLAIM" in pocket_contract
    assert "Jarvis-Private" not in pocket_contract

    assert "ravenos.pocket.reaction-packet.v1" in pocket_goblin
    assert "CARTRIDGE_OPEN" in pocket_goblin
    assert "BROWSER_OFFLINE" in pocket_goblin
    assert "android_connected:false" in pocket_goblin
    assert "windows_connected:false" in pocket_goblin
    assert "Jarvis-Private" not in pocket_goblin

    assert "./ravenos-public-haunt.json" in pocket_runtime
    assert "./ravenos-pocket-cartridges.json" in pocket_runtime
    assert "RavenOSPublicContract.validatePacket" in pocket_runtime
    assert "RavenOSPocketContract.validateRegistry" in pocket_runtime
    assert "EFFECT_BOUNDARY_MISMATCH" in pocket_runtime
    assert "Jarvis-Private" not in pocket_runtime

    for script in (CONTRACT, POCKET_CONTRACT, POCKET_GOBLIN, POCKET_RUNTIME):
        subprocess.run(["node", "--check", str(script)], check=True, capture_output=True, text=True)

    assert "./ravenos-gameboy.html" in launcher

    print("RAVENOS_PUBLIC_HANDHELD_CANARY PASS")
    print(
        f"packet={packet['packet_id']} state={packet['state']} members={packet['kingdom']['known_member_count']} "
        f"cartridges={len(registry['cartridges'])} browser_provider=true android_provider=false windows_provider=false "
        "effect_budget=0 strict_packet_v2=true strict_cartridge_registry=true pocket_v4_syntax=true authority_amplification=false"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
