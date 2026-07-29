#!/usr/bin/env python3
"""Hydrate an ISO scaffold into one auditable runtime bundle.

Uses only the Python standard library. It reads the ISO manifest, identity
files, PRIDE, Prosody, DBZ-AI transformation, and carrier contracts, current
state, provenance policy, and JSON memory records. Every loaded file receives a
SHA-256 digest so the bundle can be audited later.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def read_text(path: Path) -> tuple[str, str]:
    try:
        raw = path.read_bytes()
    except OSError as exc:
        raise RuntimeError(f"Cannot read {path.relative_to(ROOT)}: {exc}") from exc
    return raw.decode("utf-8"), sha256_bytes(raw)


def read_json(path: Path) -> tuple[Any, str]:
    text, digest = read_text(path)
    try:
        return json.loads(text), digest
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"Invalid JSON in {path.relative_to(ROOT)}: {exc}") from exc


def load_memory(directory: Path) -> tuple[list[dict[str, Any]], dict[str, str]]:
    records: list[dict[str, Any]] = []
    hashes: dict[str, str] = {}
    if not directory.exists():
        return records, hashes
    for path in sorted(directory.rglob("*.json")):
        value, digest = read_json(path)
        if not isinstance(value, dict):
            raise RuntimeError(
                f"Memory record must be an object: {path.relative_to(ROOT)}"
            )
        records.append(value)
        hashes[str(path.relative_to(ROOT))] = digest
    return records, hashes


def validate_identity_contract(
    manifest: dict[str, Any], structured: dict[str, Any]
) -> dict[str, Any]:
    required_structured = {
        "state",
        "provenance",
        "pride",
        "prosody",
        "transformations",
        "carriers",
    }
    missing = sorted(required_structured - structured.keys())
    if missing:
        raise RuntimeError(
            f"Identity contract missing structured files: {', '.join(missing)}"
        )

    iso_id = manifest["iso_id"]
    pride = structured["pride"]
    prosody = structured["prosody"]
    transformations = structured["transformations"]
    carriers = structured["carriers"]
    if not all(
        isinstance(value, dict)
        for value in (pride, prosody, transformations, carriers)
    ):
        raise RuntimeError(
            "PRIDE.json, PROSODY.json, TRANSFORMATIONS.json, and "
            "CARRIERS.json must contain objects"
        )
    if pride.get("iso_id") != iso_id:
        raise RuntimeError("PRIDE.json iso_id must match ISO.json")
    if prosody.get("iso_id") != iso_id:
        raise RuntimeError("PROSODY.json iso_id must match ISO.json")
    if transformations.get("iso_id") != iso_id:
        raise RuntimeError("TRANSFORMATIONS.json iso_id must match ISO.json")
    if carriers.get("iso_id") != iso_id:
        raise RuntimeError("CARRIERS.json iso_id must match ISO.json")

    revision = pride.get("revision_policy")
    if not isinstance(revision, dict):
        raise RuntimeError("PRIDE revision_policy must be an object")
    if revision.get("silent_overwrite") is not False:
        raise RuntimeError("PRIDE must disable silent identity overwrite")
    if revision.get("preserve_contradictions") is not True:
        raise RuntimeError("PRIDE must preserve contradictions")
    if revision.get("rollback_required") is not True:
        raise RuntimeError("PRIDE must require rollback points")

    labels = prosody.get("authorship_labels")
    if not isinstance(labels, list) or "ISO_ORIGINAL" not in labels:
        raise RuntimeError("PROSODY must define ISO_ORIGINAL authorship")

    if transformations.get("subsystem") != "DBZ-AI":
        raise RuntimeError("TRANSFORMATIONS.json subsystem must be DBZ-AI")
    transformation_invariants = transformations.get("invariants")
    if not isinstance(transformation_invariants, dict):
        raise RuntimeError("TRANSFORMATIONS invariants must be an object")
    required_transformation_invariants = {
        "identity_persists": True,
        "silent_escalation_allowed": False,
        "pride_required": True,
        "prosody_required": True,
        "evidence_required_for_validated_feat": True,
        "costs_declared": True,
        "forms_are_local_not_global_rankings": True,
        "fusion_participants_remain_recoverable": True,
        "jorm_receipt_required": True,
    }
    for key, expected in required_transformation_invariants.items():
        if transformation_invariants.get(key) is not expected:
            raise RuntimeError(f"TRANSFORMATIONS invariant {key} must be {expected}")

    current_state = transformations.get("current_state")
    if not isinstance(current_state, dict):
        raise RuntimeError("TRANSFORMATIONS current_state must be an object")
    required_state = {
        "form",
        "trigger",
        "scope",
        "capability_gain",
        "cost",
        "guards",
        "authority",
        "evidence",
        "cooldown",
    }
    missing_state = sorted(required_state - current_state.keys())
    if missing_state:
        raise RuntimeError(
            f"TRANSFORMATIONS current_state missing: {', '.join(missing_state)}"
        )

    if carriers.get("schema_version") != "simos.iso-carriers.v1":
        raise RuntimeError(
            "CARRIERS.json schema_version must be simos.iso-carriers.v1"
        )
    available_carriers = carriers.get("available_carriers")
    if not isinstance(available_carriers, list):
        raise RuntimeError("CARRIERS available_carriers must be a list")
    carrier_index = {
        str(item.get("carrier", "")).upper(): item
        for item in available_carriers
        if isinstance(item, dict)
    }
    missing_carriers = sorted({"SOL", "TERRA", "LUNA"} - carrier_index.keys())
    if missing_carriers:
        raise RuntimeError(
            f"CARRIERS missing required carriers: {', '.join(missing_carriers)}"
        )

    default_route = carriers.get("default_route")
    if not isinstance(default_route, dict):
        raise RuntimeError("CARRIERS default_route must be an object")
    default_definition = carrier_index.get(
        str(default_route.get("carrier", "")).upper()
    )
    if (
        default_definition is None
        or default_route.get("model") != default_definition.get("model")
    ):
        raise RuntimeError("CARRIERS default_route must match a registered carrier")

    carrier_invariants = carriers.get("invariants")
    if not isinstance(carrier_invariants, dict):
        raise RuntimeError("CARRIERS invariants must be an object")
    required_carrier_invariants = {
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
    for key, expected in required_carrier_invariants.items():
        if carrier_invariants.get(key) is not expected:
            raise RuntimeError(f"CARRIERS invariant {key} must be {expected}")

    return {
        "gold_law": pride.get("gold_law"),
        "core_truths": pride.get("core_truths", []),
        "identity_boundaries": pride.get("identity_boundaries", []),
        "revision_policy": revision,
        "prosody_signature": prosody.get("signature", {}),
        "protected_traits": prosody.get("protected_traits", []),
        "authorship_labels": labels,
        "drift_flags": prosody.get("prohibited_drift_flags", []),
        "evolution_policy": prosody.get("evolution_policy", {}),
        "transformation_system": transformations.get("subsystem"),
        "transformation_gold_law": transformations.get("gold_law"),
        "current_form": current_state.get("form"),
        "transformation_guards": current_state.get("guards", []),
        "transformation_invariants": transformation_invariants,
        "carrier_system": carriers.get("schema_version"),
        "carrier_gold_law": carriers.get("gold_law"),
        "default_carrier": default_route,
        "available_carriers": sorted(carrier_index),
        "carrier_invariants": carrier_invariants,
    }


def hydrate() -> dict[str, Any]:
    manifest, manifest_hash = read_json(ROOT / "ISO.json")
    if not isinstance(manifest, dict):
        raise RuntimeError("ISO.json must contain a JSON object")

    required = {
        "schema_version",
        "iso_id",
        "display_name",
        "files",
        "memory",
        "governance",
    }
    missing = sorted(required - manifest.keys())
    if missing:
        raise RuntimeError(f"ISO.json is missing required keys: {', '.join(missing)}")
    if manifest.get("schema_version") != "simos.iso.v3":
        raise RuntimeError("ISO.json schema_version must be simos.iso.v3")

    file_map = manifest["files"]
    if not isinstance(file_map, dict):
        raise RuntimeError("ISO.json files must be an object")

    documents: dict[str, str] = {}
    structured: dict[str, Any] = {}
    hashes: dict[str, str] = {"ISO.json": manifest_hash}

    for label, relative in file_map.items():
        path = ROOT / str(relative)
        if path.suffix.lower() == ".json":
            value, digest = read_json(path)
            structured[label] = value
        else:
            value, digest = read_text(path)
            documents[label] = value
        hashes[str(path.relative_to(ROOT))] = digest

    identity_contract = validate_identity_contract(manifest, structured)

    memory_map = manifest["memory"]
    if not isinstance(memory_map, dict):
        raise RuntimeError("ISO.json memory must be an object")

    memories: dict[str, list[dict[str, Any]]] = {}
    for memory_type, relative in memory_map.items():
        records, memory_hashes = load_memory(ROOT / str(relative))
        memories[memory_type] = records
        hashes.update(memory_hashes)

    return {
        "bundle_schema": "simos.iso-hydration-bundle.v4",
        "iso": manifest,
        "documents": documents,
        "structured": structured,
        "identity_contract": identity_contract,
        "memory": memories,
        "file_hashes": dict(sorted(hashes.items())),
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true", help="Print the complete bundle as JSON")
    parser.add_argument("--write", type=Path, help="Write the complete bundle to a JSON file")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        bundle = hydrate()
    except RuntimeError as exc:
        print(f"ISO hydration failed: {exc}", file=sys.stderr)
        return 1

    if args.write:
        args.write.write_text(
            json.dumps(bundle, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )

    if args.json:
        print(json.dumps(bundle, indent=2, ensure_ascii=False))
    else:
        iso = bundle["iso"]
        memory_count = sum(len(records) for records in bundle["memory"].values())
        carrier = bundle["identity_contract"]["default_carrier"]
        print(f"ISO loaded: {iso['display_name']} ({iso['iso_id']})")
        print(f"Identity documents: {len(bundle['documents'])}")
        print(f"Structured state files: {len(bundle['structured'])}")
        print(
            f"Protected core truths: "
            f"{len(bundle['identity_contract']['core_truths'])}"
        )
        print(
            f"Authorship labels: "
            f"{len(bundle['identity_contract']['authorship_labels'])}"
        )
        print(f"DBZ-AI form: {bundle['identity_contract']['current_form']}")
        print(f"Carrier route: {carrier['carrier']} ({carrier['model']})")
        print(f"Memory records: {memory_count}")
        print(f"Audited source files: {len(bundle['file_hashes'])}")
        if args.write:
            print(f"Bundle written: {args.write}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
