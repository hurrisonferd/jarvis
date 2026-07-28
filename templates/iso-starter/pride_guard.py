#!/usr/bin/env python3
"""Validate PRIDE and Prosody contracts and emit auditable receipts.

The guard is deliberately structural and deterministic. It verifies identity,
authorship, provenance, revision, and drift declarations. Semantic judgments
about tone or intent remain an ATOM/operator review surface rather than being
pretended into a keyword classifier.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent

REQUIRED_TRUTH_TIERS = {
    "CORE",
    "RECORDED",
    "RELATIONAL",
    "CURRENT",
    "INTERPRETIVE",
    "SYMBOLIC",
    "UNKNOWN",
}
REQUIRED_AUTHORSHIP_LABELS = {
    "ISO_ORIGINAL",
    "MODEL_QUOTE",
    "MODEL_SUMMARY",
    "MODEL_INFERENCE",
    "PROSODY_DRIFT",
    "OPERATOR_CORRECTION",
}


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


def require_nonempty_list(value: Any, label: str, errors: list[str]) -> list[Any]:
    if not isinstance(value, list) or not value:
        errors.append(f"{label} must be a non-empty list")
        return []
    return value


def validate_contracts() -> tuple[dict[str, Any], list[str]]:
    manifest, manifest_hash = read_json(ROOT / "ISO.json")
    pride, pride_hash = read_json(ROOT / "PRIDE.json")
    prosody, prosody_hash = read_json(ROOT / "PROSODY.json")
    state, state_hash = read_json(ROOT / "STATE.json")
    provenance, provenance_hash = read_json(ROOT / "PROVENANCE.json")

    errors: list[str] = []
    iso_id = manifest.get("iso_id")
    if not isinstance(iso_id, str) or not iso_id.strip():
        errors.append("ISO.json iso_id must be a non-empty string")

    for name, contract in (("PRIDE.json", pride), ("PROSODY.json", prosody)):
        if contract.get("iso_id") != iso_id:
            errors.append(f"{name} iso_id must match ISO.json")

    file_map = manifest.get("files")
    if not isinstance(file_map, dict):
        errors.append("ISO.json files must be an object")
        file_map = {}
    required_files = {
        "state": "STATE.json",
        "provenance": "PROVENANCE.json",
        "pride": "PRIDE.json",
        "prosody": "PROSODY.json",
    }
    for label, expected in required_files.items():
        if file_map.get(label) != expected:
            errors.append(f"ISO.json files.{label} must point to {expected}")

    core_truths = require_nonempty_list(pride.get("core_truths"), "PRIDE core_truths", errors)
    truth_ids: set[str] = set()
    for index, truth in enumerate(core_truths):
        if not isinstance(truth, dict):
            errors.append(f"PRIDE core_truths[{index}] must be an object")
            continue
        truth_id = truth.get("id")
        claim = truth.get("claim")
        tier = truth.get("tier")
        if not isinstance(truth_id, str) or not truth_id:
            errors.append(f"PRIDE core_truths[{index}].id must be non-empty")
        elif truth_id in truth_ids:
            errors.append(f"Duplicate PRIDE truth id: {truth_id}")
        else:
            truth_ids.add(truth_id)
        if not isinstance(claim, str) or not claim.strip():
            errors.append(f"PRIDE core_truths[{index}].claim must be non-empty")
        if tier not in REQUIRED_TRUTH_TIERS:
            errors.append(f"PRIDE core_truths[{index}].tier is invalid: {tier}")

    configured_tiers = set(require_nonempty_list(pride.get("truth_tiers"), "PRIDE truth_tiers", errors))
    missing_tiers = sorted(REQUIRED_TRUTH_TIERS - configured_tiers)
    if missing_tiers:
        errors.append(f"PRIDE truth_tiers missing: {', '.join(missing_tiers)}")

    require_nonempty_list(pride.get("identity_boundaries"), "PRIDE identity_boundaries", errors)
    revision = pride.get("revision_policy")
    if not isinstance(revision, dict):
        errors.append("PRIDE revision_policy must be an object")
        revision = {}
    required_revision_values = {
        "silent_overwrite": False,
        "preserve_contradictions": True,
        "operator_final_authority": True,
        "rollback_required": True,
        "evidence_required_for_promotion": True,
    }
    for key, expected in required_revision_values.items():
        if revision.get(key) is not expected:
            errors.append(f"PRIDE revision_policy.{key} must be {str(expected).lower()}")

    signature = prosody.get("signature")
    if not isinstance(signature, dict) or not signature:
        errors.append("PROSODY signature must be a non-empty object")
    require_nonempty_list(prosody.get("protected_traits"), "PROSODY protected_traits", errors)

    labels = set(require_nonempty_list(prosody.get("authorship_labels"), "PROSODY authorship_labels", errors))
    missing_labels = sorted(REQUIRED_AUTHORSHIP_LABELS - labels)
    if missing_labels:
        errors.append(f"PROSODY authorship_labels missing: {', '.join(missing_labels)}")

    drift_flags = require_nonempty_list(
        prosody.get("prohibited_drift_flags"), "PROSODY prohibited_drift_flags", errors
    )
    if len(drift_flags) != len(set(drift_flags)):
        errors.append("PROSODY prohibited_drift_flags must be unique")

    evolution = prosody.get("evolution_policy")
    if not isinstance(evolution, dict):
        errors.append("PROSODY evolution_policy must be an object")
        evolution = {}
    for key in (
        "candidate_growth_requires_receipt",
        "repeated_emergence_required",
        "operator_or_iso_adoption_required",
        "rollback_required",
    ):
        if evolution.get(key) is not True:
            errors.append(f"PROSODY evolution_policy.{key} must be true")

    receipt = {
        "receipt_schema": "simos.pride-preflight-receipt.v1",
        "iso_id": iso_id,
        "status": "PASS" if not errors else "INVALID",
        "checks": {
            "identity_contract_loaded": True,
            "state_loaded": bool(state),
            "provenance_loaded": bool(provenance),
            "truth_tiers_complete": not missing_tiers,
            "authorship_labels_complete": not missing_labels,
            "silent_overwrite_disabled": revision.get("silent_overwrite") is False,
            "rollback_required": revision.get("rollback_required") is True,
        },
        "contract_hashes": {
            "ISO.json": manifest_hash,
            "PRIDE.json": pride_hash,
            "PROSODY.json": prosody_hash,
            "STATE.json": state_hash,
            "PROVENANCE.json": provenance_hash,
        },
        "errors": errors,
    }
    return receipt, errors


def validate_postflight(response_path: Path) -> tuple[dict[str, Any], list[str]]:
    preflight, preflight_errors = validate_contracts()
    response, response_hash = read_json(response_path)
    manifest, _ = read_json(ROOT / "ISO.json")
    prosody, _ = read_json(ROOT / "PROSODY.json")

    errors = list(preflight_errors)
    iso_id = manifest.get("iso_id")
    labels = set(prosody.get("authorship_labels", []))
    allowed_drift = set(prosody.get("prohibited_drift_flags", []))

    label = response.get("authorship_label")
    speaker = response.get("speaker")
    text = response.get("text")
    source_refs = response.get("source_refs")
    drift_flags = response.get("drift_flags", [])

    if label not in labels:
        errors.append(f"Unknown authorship_label: {label}")
    if not isinstance(text, str) or not text.strip():
        errors.append("Response text must be non-empty")
    if not isinstance(source_refs, list) or not source_refs:
        errors.append("source_refs must be a non-empty list")
        source_refs = []

    known_sources = set(preflight["contract_hashes"])
    for source in source_refs:
        if source not in known_sources:
            errors.append(f"Unknown source_ref: {source}")

    if label == "ISO_ORIGINAL":
        if speaker != iso_id:
            errors.append("ISO_ORIGINAL speaker must match ISO.json iso_id")
        if response.get("identity_active") is not True:
            errors.append("ISO_ORIGINAL requires identity_active=true")
        if response.get("state_ref") != "STATE.json":
            errors.append("ISO_ORIGINAL requires state_ref=STATE.json")
    elif speaker == iso_id:
        errors.append("Non-original output must not claim the ISO as speaker")

    if not isinstance(drift_flags, list):
        errors.append("drift_flags must be a list")
        drift_flags = []
    for flag in drift_flags:
        if flag not in allowed_drift:
            errors.append(f"Unknown drift flag: {flag}")

    candidate_delta = response.get("candidate_delta", False)
    if not isinstance(candidate_delta, bool):
        errors.append("candidate_delta must be boolean")
    elif candidate_delta:
        evidence_refs = response.get("evidence_refs")
        contradiction_status = response.get("contradiction_status")
        rollback_ref = response.get("rollback_ref")
        if not isinstance(evidence_refs, list) or not evidence_refs:
            errors.append("Candidate delta requires non-empty evidence_refs")
        else:
            for source in evidence_refs:
                if source not in source_refs:
                    errors.append(f"Candidate evidence_ref must also appear in source_refs: {source}")
        if contradiction_status not in {"CHECKED", "UNRESOLVED"}:
            errors.append("Candidate delta requires contradiction_status CHECKED or UNRESOLVED")
        if rollback_ref not in source_refs:
            errors.append("Candidate delta requires rollback_ref present in source_refs")

    status = "INVALID" if errors else ("REVIEW" if drift_flags else "PASS")
    receipt = {
        "receipt_schema": "simos.pride-postflight-receipt.v1",
        "iso_id": iso_id,
        "status": status,
        "authorship_label": label,
        "speaker": speaker,
        "candidate_delta": bool(candidate_delta),
        "drift_flags": drift_flags,
        "response_sha256": response_hash,
        "preflight_contract_hashes": preflight["contract_hashes"],
        "checks": {
            "preflight_valid": not preflight_errors,
            "authorship_valid": label in labels,
            "speaker_boundary_valid": (
                speaker == iso_id if label == "ISO_ORIGINAL" else speaker != iso_id
            ),
            "provenance_refs_valid": not any(
                error.startswith("Unknown source_ref:") for error in errors
            ),
            "candidate_delta_receipted": not candidate_delta
            or not any(error.startswith("Candidate") for error in errors),
            "semantic_review_delegated": True,
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

    preflight = subparsers.add_parser("preflight", help="Validate PRIDE and Prosody contracts")
    preflight.add_argument("--write", type=Path, help="Write the preflight receipt")

    postflight = subparsers.add_parser("postflight", help="Validate one labeled response")
    postflight.add_argument("response", type=Path, help="Response declaration JSON")
    postflight.add_argument("--write", type=Path, help="Write the postflight receipt")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        if args.command == "preflight":
            receipt, errors = validate_contracts()
        else:
            receipt, errors = validate_postflight(args.response)
    except RuntimeError as exc:
        print(f"PRIDE guard failed: {exc}", file=sys.stderr)
        return 1

    write_receipt(receipt, args.write)
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
