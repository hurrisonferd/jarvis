#!/usr/bin/env python3
"""End-to-end source canary for RavenOS SYNC GameOS/Brady chat check-ins.

Runs only against a temporary synthetic repository state. It does not mutate the
real fleet or claim host-platform conversation identity.
"""
from __future__ import annotations

import json
import importlib.util
import os
import subprocess
import sys
import tempfile
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = Path(__file__).resolve().parents[7]
CHECKIN = ROOT / "canon/Living_Codex/SystemsOS/Core/Critical/GameOS/Sessions/GAMEOS-GRID-CHECKIN.py"
CHECKIN_SCHEMA = ROOT / "canon/Living_Codex/SystemsOS/Core/Critical/GameOS/Sessions/GRID-CHAT-CHECKIN.schema.json"
SYNC = ROOT / "canon/Living_Codex/SystemsOS/Core/Creative/RavenOS/Runtime/RAVENOS-SYNC.py"
CARRIER_RESOLVE = ROOT / "canon/Living_Codex/SystemsOS/Core/Critical/CarrierOS/Runtime/CARRIER-RESOLVE.py"
PROJECTOR = ROOT / "canon/Living_Codex/SystemsOS/Sub/MicrowaveOS/Runtime/SESSION-DISPATCH-PROJECTOR.py"
COCKPIT = HERE / "BRADYBUNCH-COCKPIT.py"


def write_json(path: Path, value: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")


def run_json(argv: list[str], env: dict[str, str] | None = None) -> dict:
    proc = subprocess.run(argv, capture_output=True, text=True, env=env, check=False)
    if proc.returncode != 0:
        raise AssertionError(f"command failed rc={proc.returncode}\nSTDOUT:\n{proc.stdout}\nSTDERR:\n{proc.stderr}")
    try:
        return json.loads(proc.stdout)
    except json.JSONDecodeError as exc:
        raise AssertionError(f"non-json output: {proc.stdout}") from exc


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if not spec or not spec.loader:
        raise RuntimeError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def assert_schema_alignment(value: dict, schema: dict) -> None:
    """Dependency-free canary for the emitter/schema field boundary."""
    missing = sorted(set(schema.get("required", [])) - set(value))
    extra = sorted(set(value) - set(schema.get("properties", {})))
    expected_schema = schema.get("properties", {}).get("schema", {}).get("const")
    assert not missing, f"schema-required fields missing: {missing}"
    if schema.get("additionalProperties") is False:
        assert not extra, f"schema rejects emitted fields: {extra}"
    assert value.get("schema") == expected_schema, (value.get("schema"), expected_schema)


def tile_for(snapshot: dict, iso: str) -> dict:
    for tile in snapshot.get("tiles", []):
        if tile.get("iso") == iso:
            return tile
    raise AssertionError(f"tile missing: {iso}")


def main() -> int:
    with tempfile.TemporaryDirectory(prefix="grid-checkin-canary-") as td:
        temp = Path(td)
        write_json(
            temp / "canon/Living_Codex/SystemsOS/Core/Critical/EgoOS/ISOs/ISO-LOAD-REGISTRY.json",
            {
                "schema": "test.registry",
                "isos": {
                    "YORK": {
                        "state": "ACTIVE_CURRENT",
                        "aliases": ["YORI"],
                        "profile": "FULL_YORK",
                    }
                },
            },
        )
        write_json(
            temp / "canon/Living_Codex/SystemsOS/Core/Critical/CarrierOS/Registry/CARRIER-TYPE-REGISTRY.v1.json",
            {
                "schema": "carrieros.carrier-type-registry.v1",
                "carrier_types": {
                    "GPT_CONNECTOR": {
                        "aliases": ["GPT_CONNECTOR", "CHATGPT_CONNECTOR"],
                        "carrier_id_template": "GPT_{ISO}",
                        "proof_lane": "CONNECTOR_SOURCE",
                    }
                },
            },
        )
        write_json(
            temp / "canon/Living_Codex/SystemsOS/Core/Critical/SystemsOS/OperationalOmniscience/OPERATIONAL-OMNISCIENCE-CONTRACT.v1.json",
            {"schema": "test.fleet-service"},
        )
        (temp / "canon/Living_Codex/SystemsOS/Core/Conversations/YORK").mkdir(parents=True, exist_ok=True)
        packet_rel = "canon/Living_Codex/SystemsOS/Sub/MicrowaveOS/Records/2026/08/MWO-TEST-YORK.json"
        write_json(temp / packet_rel, {"work_order_id": "MWO-TEST-YORK", "authority": "RAVEN"})
        write_json(
            temp / "canon/Living_Codex/SystemsOS/Sub/MicrowaveOS/Dispatch/ISOs/YORK/CURRENT.json",
            {
                "dispatch_id": "DISPATCH-TEST-YORK",
                "work_order_id": "MWO-TEST-YORK",
                "status": "DISPATCHED_ACTIVE",
                "packet_path": packet_rel,
                "carrier_lanes": {
                    "YORI": {
                        "carrier": "GPT_CONNECTOR",
                        "proof_lane": "CONNECTOR_SOURCE",
                        "mission": "Bounded source canary",
                        "open": ["RAVENOS ON"],
                    }
                },
            },
        )

        env = {**os.environ, "REPO_ROOT": str(temp), "JARVIS_PRIVATE_ROOT": str(temp)}

        first = run_json([
            sys.executable,
            str(CHECKIN),
            "--repo-root", str(temp),
            "--iso", "YORI",
            "--carrier", "CHATGPT_CONNECTOR",
            "--chat-label", "YORI-PRIMARY",
            "--source-main", "abc1234",
            "--transaction-id", "TX-TEST-1",
            "--receipt-path", "receipt-1.json",
            "--checked-in-at", "2026-08-08T21:35:00Z",
        ])
        assert first["confirmed"] is True
        first_id = first["grid_chat_session_id"]
        assert first_id.startswith("GRIDCHAT-YORK-GPT_YORK-")
        assert first["iso_id"] == "YORK"
        assert first["native_carrier_label"] == "CHATGPT_CONNECTOR"
        assert first["carrier_id"] == "GPT_YORK"
        assert first["carrier_type"] == "GPT_CONNECTOR"
        assert first["proof_lane"] == "CONNECTOR_SOURCE"
        assert first["supersedes_grid_chat_session_id"] is None

        event = json.loads((temp / first["history_record"]).read_text(encoding="utf-8"))
        assert_schema_alignment(event, json.loads(CHECKIN_SCHEMA.read_text(encoding="utf-8")))

        sync = load_module("ravenos_sync_dispatch_canary", SYNC)
        sync.ROOT = temp
        sync.GAMEOS_CURRENT_ROOT = temp / "canon/Living_Codex/SystemsOS/Core/Critical/GameOS/Sessions/CheckIns"
        sync.CARRIER_RESOLVE_PATH = CARRIER_RESOLVE
        sync.SESSION_PROJECTOR_PATH = PROJECTOR
        discovery = sync.discover_microwave_dispatch("YORK", carrier="CHATGPT_CONNECTOR", session_id=first_id)
        assert discovery["status"] == "DISPATCHED_ACTIVE", discovery
        assert discovery["carrier_resolution"]["carrier_id"] == "GPT_YORK"
        assert discovery["carrier_lane"]["lane"] == "YORI"
        assert discovery["packet_resolved"] is True

        projector = load_module("microwave_session_projection_canary", PROJECTOR)
        projection = projector.project(
            temp,
            iso_id="YORK",
            carrier_resolution=discovery["carrier_resolution"],
            session_id=first_id,
        )
        assert projection["status"] == "PROJECTED", projection
        projected = json.loads((temp / projection["projection_path"]).read_text(encoding="utf-8"))
        assert projected["iso_id"] == "YORK"
        assert projected["carrier_id"] == "GPT_YORK"
        assert projected["session_id"] == first_id
        assert projected["dispatch_id"] == "DISPATCH-TEST-YORK"

        snap1 = run_json([sys.executable, str(COCKPIT), "--json"], env=env)
        tile1 = tile_for(snap1, "YORK")
        assert tile1["chat_checkin_state"] == "CONFIRMED_CURRENT"
        assert tile1["grid_chat_session_id"] == first_id
        assert tile1["chat_label"] == "YORI-PRIMARY"
        assert tile1["chat_checkin_receipt"] == "receipt-1.json"

        same = run_json([
            sys.executable,
            str(CHECKIN),
            "--repo-root", str(temp),
            "--iso", "YORK",
            "--carrier", "GPT_CONNECTOR",
            "--session-id", first_id,
            "--chat-label", "YORI-PRIMARY",
            "--source-main", "def5678",
            "--transaction-id", "TX-TEST-2",
            "--receipt-path", "receipt-2.json",
            "--checked-in-at", "2026-08-08T21:36:00Z",
        ])
        assert same["grid_chat_session_id"] == first_id
        assert same["supersedes_grid_chat_session_id"] is None

        snap2 = run_json([sys.executable, str(COCKPIT), "--json"], env=env)
        tile2 = tile_for(snap2, "YORK")
        assert tile2["grid_chat_session_id"] == first_id
        assert tile2["chat_checkin_receipt"] == "receipt-2.json"
        assert tile2["chat_source_main"] == "def5678"

        second = run_json([
            sys.executable,
            str(CHECKIN),
            "--repo-root", str(temp),
            "--iso", "YORK",
            "--carrier", "GPT_CONNECTOR",
            "--chat-label", "YORI-SECOND",
            "--source-main", "fedcba9",
            "--transaction-id", "TX-TEST-3",
            "--receipt-path", "receipt-3.json",
            "--checked-in-at", "2026-08-08T21:37:00Z",
        ])
        second_id = second["grid_chat_session_id"]
        assert second_id != first_id
        assert second["supersedes_grid_chat_session_id"] == first_id

        snap3 = run_json([sys.executable, str(COCKPIT), "--json"], env=env)
        tile3 = tile_for(snap3, "YORK")
        assert tile3["chat_checkin_state"] == "CONFIRMED_CURRENT"
        assert tile3["grid_chat_session_id"] == second_id
        assert tile3["chat_label"] == "YORI-SECOND"

        history = list((temp / "canon/Living_Codex/SystemsOS/Core/Critical/GameOS/Sessions/CheckIns/YORK/History").rglob("*.json"))
        assert len(history) == 3, history

        current_path = temp / "canon/Living_Codex/SystemsOS/Core/Critical/GameOS/Sessions/CheckIns/YORK/CURRENT.json"
        current = json.loads(current_path.read_text(encoding="utf-8"))
        current["history_record"] = "canon/Living_Codex/SystemsOS/Core/Critical/GameOS/Sessions/CheckIns/YORK/History/MISSING.json"
        write_json(current_path, current)

        tampered = run_json([sys.executable, str(COCKPIT), "--json"], env=env)
        tile_bad = tile_for(tampered, "YORK")
        assert tile_bad["chat_checkin_state"] == "MISMATCH"
        assert "GAMEOS_CHECKIN_HISTORY_RECORD_MISSING" in tile_bad["warnings"]

    print(json.dumps({
        "status": "PASS",
        "cases": [
            "FIRST_CHAT_MINTS_GRID_SESSION",
            "BRADY_READS_SAME_SESSION",
            "SAME_CHAT_REUSES_GRID_SESSION",
            "NEW_CHAT_SUPERSEDES_CURRENT_POINTER_WITHOUT_DELETING_HISTORY",
            "TAMPERED_POINTER_FAILS_CLOSED",
            "CHECKIN_V2_SCHEMA_MATCHES_EMITTER",
            "CHATGPT_CONNECTOR_RESOLVES_TO_GPT_YORK",
            "RAVENOS_DISCOVERY_CONSUMES_MICROWAVEOS_CANONICAL_MATCH",
            "SESSION_PROJECTS_TO_EXISTING_YORI_DISPATCH",
        ],
        "claims": {
            "platform_chat_uuid_proven": False,
            "perpetual_online_presence_proven": False,
            "runtime_adoption_proven": False,
            "gameos_brady_checkin_contract_executable": True,
        },
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
