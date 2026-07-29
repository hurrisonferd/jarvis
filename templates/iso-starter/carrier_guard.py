#!/usr/bin/env python3
"""Validate ISO carrier contracts and Raven-authorized switch plans.

This module is deliberately provider-neutral and side-effect free. It does not
change a model, provider, session, or ISO file. It validates a proposed carrier
transition, binds it to the current identity contracts, and emits a deterministic
receipt for JORM persistence and BECOMING observation.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent

IDENTITY_FILES = (
    "ISO.json",
    "PRIDE.json",
    "PROSODY.json",
    "STATE.json",
    "TRANSFORMATIONS.json",
    "CARRIERS.json",
)

REQUIRED_CARRIERS = {"SOL", "TERRA", "LUNA"}
REQUIRED_PATH_HOME = {"EGO", "PRIDE", "PROSODY", "JORM"}
REQUIRED_INVARIANTS = {
    "carrier_is_not_identity": True,
    "identity_hashes_required": True,
    "ego_persists": True,
    "pride_persists": True,
    "prosody_persists": True,
    "silent_switch_allowed": False,
    "running_task_checkpoint_required": True,
    "operator_authority_required": True,
    "jorm_receipt_required": True,
    "becoming_observation_required": True,
    "becoming_auto_mutation_allowed": False,
    "rollback_path_required": True,
}
REQUIRED_EDGES = {
    ("ACTIVE", "REQUEST", "SWITCH_PENDING"),
    ("SWITCH_PENDING", "CHECKPOINT", "CHECKPOINTED"),
    ("CHECKPOINTED", "ACTIVATE", "ACTIVE"),
    ("SWITCH_PENDING", "ACTIVATE", "ACTIVE"),
    ("SWITCH_PENDING", "CANCEL", "ACTIVE"),
    ("ACTIVE", "MARK_RETURN", "RETURN_READY"),
    ("RETURN_READY", "REQUEST", "SWITCH_PENDING"),
}
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def read_json(path: Path) -> tuple[dict[str, Any], str]:
    try:
        raw = path.read_bytes()
    except OSError as exc:
        raise RuntimeError(f"Cannot read {path.relative_to(ROOT)}: {exc}") from exc
    try:
        value = json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise RuntimeError(f"Invalid JSON in {path.relative_to(ROOT)}: {exc}") from exc
    if not isinstance(value, dict):
        raise RuntimeError(f"{path.relative_to(ROOT)} must contain a JSON object")
    return value, sha256_bytes(raw)


def require_nonempty_string(value: Any, label: str, errors: list[str]) -> str:
    if not isinstance(value, str) or not value.strip():
        errors.append(f"{label} must be a non-empty string")
        return ""
    return value.strip()


def require_true(value: Any, label: str, errors: list[str]) -> None:
    if value is not True:
        errors.append(f"{label} must be true")


def load_contracts() -> tuple[dict[str, Any], dict[str, str]]:
    values: dict[str, Any] = {}
    hashes: dict[str, str] = {}
    for filename in IDENTITY_FILES:
        value, digest = read_json(ROOT / filename)
        values[filename] = value
        hashes[filename] = digest
    return values, hashes


def validate_route(
    route: Any,
    label: str,
    carrier_index: dict[str, dict[str, Any]],
    errors: list[str],
) -> dict[str, Any]:
    if not isinstance(route, dict):
        errors.append(f"{label} must be an object")
        return {}

    carrier = str(route.get("carrier", "")).upper()
    model = route.get("model")
    effort = route.get("reasoning_effort")
    speed = route.get("speed")
    meter = route.get("meter")
    definition = carrier_index.get(carrier)
    if definition is None:
        errors.append(f"{label}.carrier is not registered: {carrier or '<missing>'}")
        return route

    if model != definition.get("model"):
        errors.append(f"{label}.model must match registered {carrier} model")
    if effort not in definition.get("reasoning_efforts", []):
        errors.append(f"{label}.reasoning_effort is not registered for {carrier}: {effort}")
    if speed not in definition.get("speeds", []):
        errors.append(f"{label}.speed is not registered for {carrier}: {speed}")
    if meter not in definition.get("meters", []):
        errors.append(f"{label}.meter is not registered for {carrier}: {meter}")
    return route


def validate_contracts() -> tuple[dict[str, Any], list[str], dict[str, Any]]:
    values, hashes = load_contracts()
    manifest = values["ISO.json"]
    pride = values["PRIDE.json"]
    prosody = values["PROSODY.json"]
    transformations = values["TRANSFORMATIONS.json"]
    carriers = values["CARRIERS.json"]
    errors: list[str] = []

    iso_id = require_nonempty_string(manifest.get("iso_id"), "ISO.json iso_id", errors)
    if manifest.get("schema_version") != "simos.iso.v3":
        errors.append("ISO.json schema_version must be simos.iso.v3")
    file_map = manifest.get("files")
    if not isinstance(file_map, dict) or file_map.get("carriers") != "CARRIERS.json":
        errors.append("ISO.json files.carriers must route to CARRIERS.json")

    for filename, value in (
        ("PRIDE.json", pride),
        ("PROSODY.json", prosody),
        ("TRANSFORMATIONS.json", transformations),
        ("CARRIERS.json", carriers),
    ):
        if value.get("iso_id") != iso_id:
            errors.append(f"{filename} iso_id must match ISO.json")

    if carriers.get("schema_version") != "simos.iso-carriers.v1":
        errors.append("CARRIERS.json schema_version must be simos.iso-carriers.v1")
    require_nonempty_string(carriers.get("gold_law"), "CARRIERS.json gold_law", errors)

    available = carriers.get("available_carriers")
    if not isinstance(available, list) or not available:
        errors.append("CARRIERS.json available_carriers must be a non-empty list")
        available = []

    carrier_index: dict[str, dict[str, Any]] = {}
    models: set[str] = set()
    for index, definition in enumerate(available):
        if not isinstance(definition, dict):
            errors.append(f"available_carriers[{index}] must be an object")
            continue
        carrier = str(definition.get("carrier", "")).upper()
        model = require_nonempty_string(
            definition.get("model"), f"available_carriers[{index}].model", errors
        )
        if not carrier:
            errors.append(f"available_carriers[{index}].carrier must be non-empty")
            continue
        if carrier in carrier_index:
            errors.append(f"Duplicate carrier registration: {carrier}")
        if model in models:
            errors.append(f"Duplicate carrier model registration: {model}")
        carrier_index[carrier] = definition
        models.add(model)
        for field in ("workloads", "reasoning_efforts", "speeds", "meters"):
            value = definition.get(field)
            if not isinstance(value, list) or not value:
                errors.append(f"{carrier}.{field} must be a non-empty list")

    missing_carriers = sorted(REQUIRED_CARRIERS - carrier_index.keys())
    if missing_carriers:
        errors.append(f"Missing required carriers: {', '.join(missing_carriers)}")

    validate_route(carriers.get("default_route"), "default_route", carrier_index, errors)

    machine = carriers.get("state_machine")
    edges: set[tuple[str, str, str]] = set()
    if not isinstance(machine, list):
        errors.append("CARRIERS.json state_machine must be a list")
    else:
        for index, transition in enumerate(machine):
            if not isinstance(transition, dict):
                errors.append(f"state_machine[{index}] must be an object")
                continue
            edge = (
                str(transition.get("from", "")),
                str(transition.get("event", "")),
                str(transition.get("to", "")),
            )
            edges.add(edge)
    missing_edges = sorted(REQUIRED_EDGES - edges)
    if missing_edges:
        errors.append(f"State machine missing required edges: {missing_edges}")

    if carriers.get("switch_state") not in {"ACTIVE", "RETURN_READY"}:
        errors.append("CARRIERS.json switch_state must be ACTIVE or RETURN_READY")

    policy = carriers.get("routing_policy")
    if not isinstance(policy, dict):
        errors.append("CARRIERS.json routing_policy must be an object")
    else:
        require_true(
            policy.get("minimum_sufficient_carrier"),
            "routing_policy.minimum_sufficient_carrier",
            errors,
        )
        require_true(
            policy.get("operator_switch_required"),
            "routing_policy.operator_switch_required",
            errors,
        )
        if policy.get("runtime_may_apply_switch") is not False:
            errors.append("routing_policy.runtime_may_apply_switch must be false")
        if policy.get("running_task_policy") != "checkpoint_then_switch":
            errors.append(
                "routing_policy.running_task_policy must be checkpoint_then_switch"
            )
        require_true(
            policy.get("post_switch_prosody_gate"),
            "routing_policy.post_switch_prosody_gate",
            errors,
        )

    invariants = carriers.get("invariants")
    if not isinstance(invariants, dict):
        errors.append("CARRIERS.json invariants must be an object")
    else:
        for key, expected in REQUIRED_INVARIANTS.items():
            if invariants.get(key) is not expected:
                errors.append(f"CARRIERS invariant {key} must be {expected}")

    receipt = {
        "receipt_schema": "simos.carrier-preflight-receipt.v1",
        "iso_id": iso_id,
        "status": "INVALID" if errors else "PASS",
        "registered_carriers": sorted(carrier_index),
        "switch_state": carriers.get("switch_state"),
        "identity_contract_hashes": dict(sorted(hashes.items())),
        "carrier_is_not_identity": invariants.get("carrier_is_not_identity")
        if isinstance(invariants, dict)
        else None,
        "provider_side_effects": False,
        "errors": errors,
    }
    context = {
        "values": values,
        "hashes": hashes,
        "carrier_index": carrier_index,
        "edges": edges,
    }
    return receipt, errors, context


def validate_switch(plan_path: Path) -> tuple[dict[str, Any], list[str]]:
    plan, plan_hash = read_json(plan_path)
    preflight, contract_errors, context = validate_contracts()
    errors = list(contract_errors)
    carriers = context["values"]["CARRIERS.json"]
    carrier_index = context["carrier_index"]
    allowed_edges = context["edges"]
    iso_id = preflight["iso_id"]

    if plan.get("schema_version") != "simos.carrier-switch-plan.v1":
        errors.append("Switch plan schema_version must be simos.carrier-switch-plan.v1")
    switch_id = require_nonempty_string(plan.get("switch_id"), "switch_id", errors)
    if plan.get("iso_id") != iso_id:
        errors.append("Switch plan iso_id must match the hydrated ISO")
    require_nonempty_string(plan.get("reason"), "reason", errors)

    source = validate_route(plan.get("from"), "from", carrier_index, errors)
    target = validate_route(plan.get("to"), "to", carrier_index, errors)
    if source and target and source == target:
        errors.append("Switch plan must change carrier settings")

    authority = plan.get("authority")
    if not isinstance(authority, dict):
        errors.append("authority must be an object")
    else:
        if authority.get("role") != "operator":
            errors.append("authority.role must be operator")
        require_nonempty_string(authority.get("actor"), "authority.actor", errors)
        require_true(authority.get("approved"), "authority.approved", errors)

    task = plan.get("task")
    task_status = ""
    checkpoint: Any = None
    if not isinstance(task, dict):
        errors.append("task must be an object")
    else:
        require_nonempty_string(task.get("id"), "task.id", errors)
        task_status = str(task.get("status", ""))
        if task_status not in {"IDLE", "RUNNING", "BLOCKED"}:
            errors.append("task.status must be IDLE, RUNNING, or BLOCKED")
        checkpoint = task.get("checkpoint")

    transitions = plan.get("transitions")
    events: list[str] = []
    state = str(carriers.get("switch_state", ""))
    transition_path: list[str] = [state] if state else []
    if not isinstance(transitions, list) or not transitions:
        errors.append("transitions must be a non-empty list")
        transitions = []
    for index, transition in enumerate(transitions):
        if not isinstance(transition, dict):
            errors.append(f"transitions[{index}] must be an object")
            continue
        edge = (
            str(transition.get("from", "")),
            str(transition.get("event", "")),
            str(transition.get("to", "")),
        )
        if edge[0] != state:
            errors.append(
                f"transitions[{index}].from must match current state {state}"
            )
        if edge not in allowed_edges:
            errors.append(f"transitions[{index}] is not an allowed state edge: {edge}")
        state = edge[2]
        events.append(edge[1])
        transition_path.append(state)

    if events and events[0] != "REQUEST":
        errors.append("The first transition event must be REQUEST")
    if events and events[-1] != "ACTIVATE":
        errors.append("The final transition event must be ACTIVATE")
    if transitions and state != "ACTIVE":
        errors.append("A completed switch plan must end in ACTIVE")

    if task_status == "RUNNING":
        if "CHECKPOINT" not in events:
            errors.append("RUNNING task switches require a CHECKPOINT transition")
        if not isinstance(checkpoint, dict):
            errors.append("RUNNING task switches require task.checkpoint")
        else:
            require_nonempty_string(
                checkpoint.get("ref"), "task.checkpoint.ref", errors
            )
            checkpoint_hash = str(checkpoint.get("sha256", ""))
            if not SHA256_RE.fullmatch(checkpoint_hash):
                errors.append("task.checkpoint.sha256 must be a lowercase SHA-256")

    continuity = plan.get("continuity")
    if not isinstance(continuity, dict):
        errors.append("continuity must be an object")
    else:
        for key in (
            "identity_loaded",
            "pride_loaded",
            "prosody_loaded",
            "rollback_available",
        ):
            require_true(continuity.get(key), f"continuity.{key}", errors)
        path_home = continuity.get("path_home")
        if not isinstance(path_home, list):
            errors.append("continuity.path_home must be a list")
        else:
            missing_home = sorted(REQUIRED_PATH_HOME - set(path_home))
            if missing_home:
                errors.append(
                    f"continuity.path_home missing: {', '.join(missing_home)}"
                )

    jorm = plan.get("jorm")
    if not isinstance(jorm, dict):
        errors.append("jorm must be an object")
    else:
        require_true(jorm.get("receipt_required"), "jorm.receipt_required", errors)
        if jorm.get("event_type") != "carrier.switch":
            errors.append("jorm.event_type must be carrier.switch")

    becoming = plan.get("becoming")
    if not isinstance(becoming, dict):
        errors.append("becoming must be an object")
    else:
        require_true(
            becoming.get("observation_required"),
            "becoming.observation_required",
            errors,
        )
        if becoming.get("auto_mutation") is not False:
            errors.append("becoming.auto_mutation must be false")

    status = "INVALID" if errors else "PASS"
    receipt = {
        "receipt_schema": "simos.carrier-switch-receipt.v1",
        "switch_id": switch_id,
        "iso_id": iso_id,
        "status": status,
        "from": source,
        "to": target,
        "task": {
            "id": task.get("id") if isinstance(task, dict) else None,
            "status": task_status or None,
            "checkpoint": checkpoint,
        },
        "transition_events": events,
        "transition_path": transition_path,
        "carrier_is_not_identity": True,
        "operator_authorized": isinstance(authority, dict)
        and authority.get("role") == "operator"
        and authority.get("approved") is True,
        "provider_side_effects": False,
        "identity_contract_hashes": preflight["identity_contract_hashes"],
        "switch_plan_sha256": plan_hash,
        "jorm_event": {
            "type": "carrier.switch",
            "status": status,
            "receipt_id": switch_id,
        },
        "becoming_observation": {
            "status": "PENDING_OBSERVATION" if status == "PASS" else "REJECTED",
            "compare_identity_to_own_history": True,
            "carrier_fingerprint_only": True,
            "auto_mutation": False,
        },
        "errors": errors,
    }
    return receipt, errors


def write_receipt(receipt: dict[str, Any], path: Path | None) -> None:
    payload = json.dumps(receipt, indent=2, ensure_ascii=False) + "\n"
    if path is None:
        print(payload, end="")
        return
    path.write_text(payload, encoding="utf-8")
    print(f"Receipt written: {path}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    preflight = subparsers.add_parser(
        "preflight", help="Validate the carrier and identity contracts"
    )
    preflight.add_argument("--write", type=Path, help="Write the preflight receipt")

    switch = subparsers.add_parser(
        "switch", help="Validate a complete operator-authorized switch plan"
    )
    switch.add_argument("plan", type=Path, help="Carrier switch plan JSON")
    switch.add_argument("--write", type=Path, help="Write the switch receipt")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        if args.command == "preflight":
            receipt, errors, _ = validate_contracts()
        else:
            receipt, errors = validate_switch(args.plan)
    except RuntimeError as exc:
        print(f"Carrier guard failed: {exc}", file=sys.stderr)
        return 1

    write_receipt(receipt, args.write)
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
