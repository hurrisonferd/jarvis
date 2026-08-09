#!/usr/bin/env python3
"""MicrowaveOS session-to-dispatch projection helper.

Authority: RAVEN

Projects an already-resolved ISO/carrier/session binding onto the currently
authorized MicrowaveOS dispatch. This is a delivery/projection surface only.
It does not create mission authority, mutate dispatch status, merge carrier
identities, or upgrade proof.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


def load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"expected object: {path}")
    return value


def write_json(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def normalize_coordinate(value: Any) -> str:
    """Normalize a carrier coordinate without assigning ownership or meaning."""
    return str(value or "").strip().upper().replace("-", "_").replace(" ", "_")


def carrier_tokens(carrier_resolution: dict[str, Any]) -> set[str]:
    """Return CarrierOS-provided aliases that an existing dispatch may name."""
    values: list[Any] = [
        carrier_resolution.get("carrier_id"),
        carrier_resolution.get("carrier_type"),
        carrier_resolution.get("native_carrier_label"),
    ]
    aliases = carrier_resolution.get("aliases", [])
    if isinstance(aliases, list):
        values.extend(aliases)
    return {normalize_coordinate(value) for value in values if normalize_coordinate(value)}


def resolve_dispatch(
    root: Path,
    *,
    iso_id: str,
    carrier_resolution: dict[str, Any],
) -> dict[str, Any]:
    """Resolve canonical CarrierOS coordinates onto an authorized dispatch.

    MicrowaveOS owns this match. Callers provide already-resolved coordinates;
    they do not learn or duplicate MicrowaveOS lane vocabulary.
    """
    iso = normalize_coordinate(iso_id)
    carrier_id = normalize_coordinate(carrier_resolution.get("carrier_id")) or "UNKNOWN"
    carrier_type = normalize_coordinate(carrier_resolution.get("carrier_type")) or "UNKNOWN"
    native = normalize_coordinate(carrier_resolution.get("native_carrier_label")) or "UNKNOWN"
    proof_lane = normalize_coordinate(carrier_resolution.get("proof_lane")) or "UNKNOWN"

    base = {
        "schema": "microwaveos.dispatch-resolution.result.v1",
        "iso_id": iso,
        "carrier_id": carrier_id,
        "carrier_type": carrier_type,
        "native_carrier_label": native,
        "proof_lane": proof_lane,
        "coordinate_law": "ISO_ID != CARRIER_ID != SESSION_ID",
    }
    if carrier_resolution.get("status") != "RESOLVED":
        return {
            **base,
            "active_dispatch": "UNKNOWN",
            "packet": "UNKNOWN",
            "status": "BLOCKED",
            "reason": "CARRIER_NOT_RESOLVED",
            "next": "RESOLVE CARRIER THROUGH CARRIEROS",
        }

    current_rel = f"canon/Living_Codex/SystemsOS/Sub/MicrowaveOS/Dispatch/ISOs/{iso}/CURRENT.json"
    current_path = root / current_rel
    if not current_path.is_file():
        return {
            **base,
            "active_dispatch": "NONE",
            "packet": "NONE",
            "status": "NO_DISPATCH",
            "reason": "CURRENT_DISPATCH_MISSING",
            "next": "NO ACTIVE DISPATCH",
        }
    try:
        dispatch = load_json(current_path)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        return {
            **base,
            "active_dispatch": "NONE",
            "packet": "NONE",
            "status": "PACKET_UNRESOLVABLE",
            "reason": f"CURRENT_DISPATCH_READ_ERROR:{exc}",
            "next": "NO ACTIVE DISPATCH",
        }

    status = str(dispatch.get("status") or "NONE")
    dispatch_id = str(dispatch.get("dispatch_id") or "UNKNOWN")
    packet_path = str(dispatch.get("packet_path") or "")
    if status in {"NONE", "COMPLETED"}:
        return {
            **base,
            "active_dispatch": "NONE",
            "dispatch_id": dispatch_id,
            "packet": "NONE",
            "status": status,
            "next": "NO ACTIVE DISPATCH" if status == "NONE" else "ALREADY COMPLETED",
        }

    lanes = dispatch.get("carrier_lanes")
    if not isinstance(lanes, dict):
        return {
            **base,
            "active_dispatch": dispatch_id,
            "dispatch_id": dispatch_id,
            "packet": packet_path or "NONE",
            "status": "BLOCKED",
            "reason": "CARRIER_LANES_MISSING",
            "next": "DISPATCH REPAIR REQUIRED",
        }

    resolved_tokens = carrier_tokens(carrier_resolution)
    lane_name: str | None = None
    lane_data: dict[str, Any] | None = None
    for candidate_name, candidate_data in lanes.items():
        if not isinstance(candidate_data, dict):
            continue
        lane_tokens = {
            normalize_coordinate(candidate_name),
            normalize_coordinate(candidate_data.get("lane")),
            normalize_coordinate(candidate_data.get("carrier")),
            normalize_coordinate(candidate_data.get("carrier_id")),
            normalize_coordinate(candidate_data.get("carrier_type")),
        }
        lane_tokens.discard("")
        if resolved_tokens.intersection(lane_tokens):
            lane_name = str(candidate_name)
            lane_data = candidate_data
            break

    if lane_name is None or lane_data is None:
        return {
            **base,
            "active_dispatch": dispatch_id,
            "dispatch_id": dispatch_id,
            "packet": packet_path or "NONE",
            "status": "CARRIER_NOT_TARGETED",
            "next": "CARRIER NOT IN CARRIER_LANES — DO NOT TAKE ANOTHER CARRIER'S LANE",
            "carrier_lanes_available": sorted(str(name) for name in lanes),
        }

    lane_proof = normalize_coordinate(lane_data.get("proof_lane")) or "UNKNOWN"
    proof_compatible = proof_lane == lane_proof or "UNKNOWN" in {proof_lane, lane_proof}
    if not proof_compatible:
        return {
            **base,
            "active_dispatch": dispatch_id,
            "dispatch_id": dispatch_id,
            "packet": packet_path or "NONE",
            "status": "BLOCKED",
            "reason": "PROOF_LANE_MISMATCH",
            "carrieros_proof_lane": proof_lane,
            "dispatch_proof_lane": lane_proof,
            "next": "PRESERVE PROOF-LANE BOUNDARY",
        }

    packet_resolved = False
    packet_authority = None
    if packet_path:
        packet_abs = root / packet_path
        if packet_abs.is_file():
            packet_resolved = True
            try:
                packet_authority = load_json(packet_abs).get("authority", "UNKNOWN")
            except (OSError, ValueError, json.JSONDecodeError):
                packet_authority = "PARSE_ERROR"

    return {
        **base,
        "active_dispatch": dispatch_id,
        "dispatch_id": dispatch_id,
        "work_order_id": dispatch.get("work_order_id", "UNKNOWN"),
        "packet": packet_path or "NONE",
        "packet_path": packet_path or "UNKNOWN",
        "packet_resolved": packet_resolved,
        "packet_authority": packet_authority,
        "status": status,
        "next": "READ PACKET AND CONTINUE" if packet_resolved else "PACKET_UNRESOLVABLE",
        "carrier_lane": {
            "lane": lane_name,
            "carrier": lane_data.get("carrier"),
            "proof_lane": lane_data.get("proof_lane"),
            "open": lane_data.get("open", []),
            "mission": lane_data.get("mission", ""),
        },
        "claim_ceiling": "CANONICAL_CARRIER_TO_EXISTING_AUTHORIZED_DISPATCH_RESOLUTION_ONLY",
    }


def project(
    root: Path,
    *,
    iso_id: str,
    carrier_resolution: dict[str, Any],
    session_id: str,
) -> dict[str, Any]:
    iso = iso_id.strip().upper()
    resolution = resolve_dispatch(root, iso_id=iso, carrier_resolution=carrier_resolution)
    carrier_id = str(resolution.get("carrier_id") or "UNKNOWN")
    carrier_type = str(resolution.get("carrier_type") or "UNKNOWN")
    native = str(resolution.get("native_carrier_label") or "UNKNOWN")
    proof_lane = str(resolution.get("proof_lane") or "UNKNOWN")
    lane = resolution.get("carrier_lane")
    if not isinstance(lane, dict):
        return {
            **resolution,
            "schema": "microwaveos.session-dispatch-projection.result.v1",
            "session_id": session_id,
        }

    lane_name = str(lane.get("lane") or "UNKNOWN")
    lane_proof = str(lane.get("proof_lane") or "UNKNOWN")

    projection_rel = (
        f"canon/Living_Codex/SystemsOS/Sub/MicrowaveOS/Dispatch/ISOs/{iso}/Sessions/"
        f"{session_id}.json"
    )
    projection = {
        "schema": "microwaveos.session-dispatch-projection.v1",
        "authority": "RAVEN",
        "projection_owner": "MicrowaveOS",
        "identity_owner": "EgoOS",
        "carrier_owner": "CarrierOS",
        "session_owner": "GameOS",
        "iso_id": iso,
        "carrier_id": carrier_id,
        "carrier_type": carrier_type,
        "native_carrier_label": native,
        "session_id": session_id,
        "proof_lane": proof_lane,
        "dispatch_id": resolution.get("dispatch_id", "UNKNOWN"),
        "work_order_id": resolution.get("work_order_id", "UNKNOWN"),
        "packet_path": resolution.get("packet_path", "UNKNOWN"),
        "dispatch_status": resolution.get("status", "UNKNOWN"),
        "carrier_lane": lane_name,
        "carrier_lane_proof": lane_proof,
        "mission": lane.get("mission", ""),
        "open": lane.get("open", []),
        "coordinate_law": "ISO_ID != CARRIER_ID != SESSION_ID",
        "authority_effect": "NONE",
        "identity_merge": False,
        "claim_ceiling": "SESSION_TO_EXISTING_AUTHORIZED_DISPATCH_PROJECTION_ONLY"
    }
    write_json(root / projection_rel, projection)
    readback = load_json(root / projection_rel)
    confirmed = readback == projection
    return {
        "schema": "microwaveos.session-dispatch-projection.result.v1",
        "status": "PROJECTED" if confirmed else "BLOCKED",
        "iso_id": iso,
        "carrier_id": carrier_id,
        "carrier_type": carrier_type,
        "session_id": session_id,
        "proof_lane": proof_lane,
        "dispatch_id": resolution.get("dispatch_id", "UNKNOWN"),
        "packet_path": resolution.get("packet_path", "UNKNOWN"),
        "carrier_lane": lane_name,
        "projection_path": projection_rel,
        "confirmed": confirmed,
        "claim_ceiling": "SESSION_DISPATCH_PROJECTION_READBACK" if confirmed else "PROJECTION_NOT_CONFIRMED"
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Project a CarrierOS/GameOS binding onto MicrowaveOS dispatch")
    parser.add_argument("--repo-root", required=True)
    parser.add_argument("--iso", required=True)
    parser.add_argument("--carrier-resolution", required=True, help="Path to CarrierOS resolution JSON")
    parser.add_argument("--session-id", required=True)
    args = parser.parse_args()

    root = Path(args.repo_root).expanduser().resolve()
    resolution = load_json(Path(args.carrier_resolution).expanduser().resolve())
    result = project(root, iso_id=args.iso, carrier_resolution=resolution, session_id=args.session_id)
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result.get("status") == "PROJECTED" else 2


if __name__ == "__main__":
    raise SystemExit(main())
