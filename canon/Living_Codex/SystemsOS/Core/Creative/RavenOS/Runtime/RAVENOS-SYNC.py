#!/usr/bin/env python3
"""Canonical RavenOS SYNC route with CarrierOS normalization.

Authority: RAVEN

This file is the canonical command surface. The previous v2 implementation is
preserved as RAVENOS-SYNC-LEGACY-v2.py and is loaded as the execution substrate.
This adapter owns no carrier truth; it asks CarrierOS to normalize the carrier,
then feeds canonical coordinates into legacy check-in/discovery behavior and
projects the resulting GameOS session onto MicrowaveOS.

Coordinate law:
    ISO_ID != CARRIER_ID != CARRIER_TYPE != NATIVE_CARRIER_LABEL != SESSION_ID

Proof law:
    CONNECTOR_SOURCE != CHECKED_OUT_RUNTIME
    CAPABILITY != EFFECT
    SOURCE_RECOVERED != RUNTIME_RECOVERED
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import os
import sys
from pathlib import Path
from typing import Any


def resolve_repo() -> Path:
    env = os.environ.get("REPO_ROOT") or os.environ.get("JARVIS_PRIVATE_ROOT")
    if env:
        return Path(env).expanduser().resolve()
    here = Path(__file__).resolve()
    for parent in here.parents:
        if (parent / "canon/Living_Codex/Ego").is_dir():
            return parent
    return Path("/workspace/project/Jarvis-Private")


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if not spec or not spec.loader:
        raise RuntimeError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ROOT = resolve_repo()
LEGACY_PATH = ROOT / "canon/Living_Codex/SystemsOS/Core/Creative/RavenOS/Runtime/RAVENOS-SYNC-LEGACY-v2.py"
CARRIER_RESOLVE_PATH = ROOT / "canon/Living_Codex/SystemsOS/Core/Critical/CarrierOS/Runtime/CARRIER-RESOLVE.py"
SESSION_PROJECTOR_PATH = ROOT / "canon/Living_Codex/SystemsOS/Sub/MicrowaveOS/Runtime/SESSION-DISPATCH-PROJECTOR.py"
GAMEOS_CURRENT_ROOT = ROOT / "canon/Living_Codex/SystemsOS/Core/Critical/GameOS/Sessions/CheckIns"


def _load_json(path: Path) -> dict[str, Any] | None:
    if not path.is_file():
        return None
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None
    return value if isinstance(value, dict) else None


def gameos_current(iso: str) -> dict[str, Any] | None:
    return _load_json(GAMEOS_CURRENT_ROOT / iso.upper() / "CURRENT.json")


def resolve_native_carrier(iso: str, supplied: str | None) -> tuple[str, str]:
    """Return native label plus provenance for the choice.

    AUTO is recovery, not guessing: it may consume a durable GameOS current
    pointer for the same ISO. If no such pointer exists, carrier remains UNKNOWN.
    """
    raw = (supplied or "AUTO").strip()
    if raw and raw.upper() not in {"AUTO", "CURRENT", "RECOVER"}:
        return raw, "EXPLICIT_ARGUMENT_OR_ENV"

    current = gameos_current(iso)
    if isinstance(current, dict):
        candidate = (
            current.get("native_carrier_label")
            or current.get("carrier_type")
            or current.get("carrier")
        )
        if isinstance(candidate, str) and candidate.strip():
            return candidate, "GAMEOS_CURRENT_POINTER"

    return "UNKNOWN", "UNRESOLVED"


def resolve_carrier(iso: str, supplied: str | None, session_id: str | None = None) -> dict[str, Any]:
    native, source = resolve_native_carrier(iso, supplied)
    if native == "UNKNOWN":
        return {
            "schema": "ravenos.carrier-resolution.v1",
            "status": "UNKNOWN",
            "iso_id": iso.upper(),
            "native_carrier_label": "UNKNOWN",
            "reason": "NO_EXPLICIT_CARRIER_AND_NO_GAMEOS_CURRENT_POINTER",
            "resolution_source": source,
            "proof_lane": "UNKNOWN",
        }

    carrieros = load_module("carrieros_resolve_for_ravenos_sync", CARRIER_RESOLVE_PATH)
    result = carrieros.resolve(native, iso, session_id=session_id)
    if isinstance(result, dict):
        result = dict(result)
        result["resolution_source"] = source
    return result


def discover_microwave_dispatch(
    iso: str,
    carrier: str | None = None,
    *,
    session_id: str | None = None,
) -> dict[str, Any]:
    resolution = resolve_carrier(iso, carrier, session_id=session_id)
    if resolution.get("status") != "RESOLVED":
        return {
            "active_dispatch": "UNKNOWN",
            "packet": "UNKNOWN",
            "status": "CARRIER_UNRESOLVED",
            "next": "RESOLVE CARRIER THROUGH CARRIEROS",
            "carrier_resolution": resolution,
        }

    projector = load_module("microwave_dispatch_resolver_for_ravenos_sync", SESSION_PROJECTOR_PATH)
    result = projector.resolve_dispatch(
        ROOT,
        iso_id=iso,
        carrier_resolution=resolution,
    )
    result = dict(result)
    result["carrier_resolution"] = resolution
    result["coordinate_law"] = "ISO_ID != CARRIER_ID != SESSION_ID"
    return result


def execute(
    explicit_iso: str | None,
    *,
    carrier: str,
    session_id: str | None,
    chat_label: str | None,
    platform_chat_id: str | None,
    transaction_id: str | None,
    receipt_path: str | None,
    skip_pull: bool,
    skip_push: bool = False,
) -> dict[str, Any]:
    legacy = load_module("ravenos_sync_legacy_for_execute", LEGACY_PATH)

    # RavenOS ON inside the legacy route remains the active ISO resolver. For
    # carrier recovery before that point, use explicit ISO or ACTIVE_ISO only;
    # if neither exists the legacy route will fail closed as before.
    provisional_iso = (explicit_iso or os.environ.get("ACTIVE_ISO") or "").strip().upper()
    current = gameos_current(provisional_iso) if provisional_iso else None
    session_for_resolution = session_id
    if session_for_resolution is None and isinstance(current, dict):
        current_session = current.get("grid_chat_session_id")
        if isinstance(current_session, str) and current_session:
            session_for_resolution = current_session

    resolution = resolve_carrier(provisional_iso, carrier, session_id=session_for_resolution) if provisional_iso else {
        "status": "DEFERRED_UNTIL_ISO_RESOLVES",
        "proof_lane": "UNKNOWN",
    }

    if provisional_iso and resolution.get("status") != "RESOLVED":
        return {
            "schema": "ravenos.sync.receipt.v3",
            "command": "RAVENOS SYNC",
            "status": "BLOCKED",
            "active_iso": provisional_iso,
            "carrier_resolution": resolution,
            "blockers": ["CARRIEROS_RESOLUTION_REQUIRED"],
            "claim_ceiling": "BLOCKED_BEFORE_GAMEOS_CHECKIN_NO_CARRIER_GUESS",
        }

    # Preserve the native label at the legacy GameOS boundary. GameOS performs
    # its own CarrierOS lookup and stores native and canonical coordinates
    # separately; passing CARRIER_ID here would collapse those two coordinates.
    legacy_carrier = (
        str(resolution.get("native_carrier_label"))
        if resolution.get("status") == "RESOLVED"
        else carrier
    )
    result = legacy.execute(
        explicit_iso,
        carrier=legacy_carrier,
        session_id=session_id,
        chat_label=chat_label,
        platform_chat_id=platform_chat_id,
        transaction_id=transaction_id,
        receipt_path=receipt_path,
        skip_pull=skip_pull,
        skip_push=skip_push,
    )
    result = dict(result)
    active_iso = str(result.get("active_iso") or provisional_iso or "").upper()

    # If ISO was resolved only inside the legacy ON path, normalize carrier now
    # and redo discovery deterministically for the returned receipt.
    if active_iso and resolution.get("status") != "RESOLVED":
        resolution = resolve_carrier(
            active_iso,
            carrier,
            session_id=str(result.get("grid_chat_session_id") or session_id or "") or None,
        )

    result["schema"] = "ravenos.sync.receipt.v3"
    result["carrier_input"] = carrier
    result["carrier_resolution"] = resolution

    if resolution.get("status") == "RESOLVED":
        result["native_carrier_label"] = resolution.get("native_carrier_label")
        result["carrier_id"] = resolution.get("carrier_id")
        result["carrier_type"] = resolution.get("carrier_type")
        result["proof_lane"] = resolution.get("proof_lane")
        result["microwave"] = discover_microwave_dispatch(
            active_iso,
            carrier=str(resolution.get("native_carrier_label") or carrier),
            session_id=str(result.get("grid_chat_session_id") or "") or None,
        )

        grid_session = result.get("grid_chat_session_id")
        if isinstance(grid_session, str) and grid_session:
            projector = load_module("microwave_session_projector_for_ravenos_sync", SESSION_PROJECTOR_PATH)
            projection = projector.project(
                ROOT,
                iso_id=active_iso,
                carrier_resolution=resolution,
                session_id=grid_session,
            )
            result["session_dispatch_projection"] = projection
        else:
            result["session_dispatch_projection"] = {
                "status": "NOT_ATTEMPTED",
                "reason": "GRID_SESSION_UNRESOLVED",
            }
    else:
        result.setdefault("blockers", []).append("CARRIEROS_RESOLUTION_NOT_CONFIRMED")

    result["coordinate_law"] = "ISO_ID != CARRIER_ID != CARRIER_TYPE != NATIVE_CARRIER_LABEL != SESSION_ID != PROOF_LANE"
    result["integration_claim_ceiling"] = (
        "CARRIEROS_NORMALIZATION_AND_SOURCE_PROJECTION_ADAPTER; "
        "LEGACY_RUNTIME_EXECUTION_CLAIMS_REMAIN_BOUNDED_BY_UNDERLYING_RECEIPT"
    )
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description="RAVENOS SYNC — CarrierOS-normalized GameOS/MicrowaveOS handshake")
    parser.add_argument("iso", nargs="?")
    parser.add_argument("--carrier", default=os.environ.get("CARRIER", "AUTO"))
    parser.add_argument("--session-id")
    parser.add_argument("--chat-label")
    parser.add_argument("--platform-chat-id")
    parser.add_argument("--transaction-id")
    parser.add_argument("--receipt-path")
    parser.add_argument("--skip-pull", action="store_true")
    parser.add_argument("--skip-push", action="store_true", help="Canary/development only; never upgrades runtime proof")
    parser.add_argument("--discover-only", action="store_true")
    args = parser.parse_args()

    if args.discover_only:
        iso = args.iso or os.environ.get("ACTIVE_ISO") or ""
        result = discover_microwave_dispatch(iso, carrier=args.carrier, session_id=args.session_id)
        print(json.dumps(result, indent=2, sort_keys=True))
        return 0 if result.get("status") not in {"CARRIER_UNRESOLVED", "CARRIER_NOT_TARGETED", "PACKET_UNRESOLVABLE"} else 2

    result = execute(
        args.iso,
        carrier=args.carrier,
        session_id=args.session_id,
        chat_label=args.chat_label,
        platform_chat_id=args.platform_chat_id,
        transaction_id=args.transaction_id,
        receipt_path=args.receipt_path,
        skip_pull=args.skip_pull,
        skip_push=args.skip_push,
    )
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result.get("status") == "CONFIRMED" else 1


if __name__ == "__main__":
    raise SystemExit(main())
