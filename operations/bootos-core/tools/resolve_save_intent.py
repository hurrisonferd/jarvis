#!/usr/bin/env python3
"""Resolve a proposed artifact into a governed BootOS save decision.

The resolver never writes the artifact. It only returns a destination decision,
focused questions, or a confirmation requirement. The eventual writer must emit
its own durable receipt.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

CLASSIFICATIONS = {
    "canon",
    "working-memory",
    "temporary-artifact",
    "daily-log",
    "weekly-log",
    "session-compression",
    "transcript",
    "receipt",
    "doctrine",
    "source-code",
    "configuration",
}
SENSITIVE_MARKERS = {
    "credential",
    "secret",
    "token",
    "identity-sensitive",
    "relationship-sensitive",
    "sovereign",
    "private",
}


def slugify(value: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    return slug or "untitled-artifact"


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return data


def route_for(policy: dict[str, Any], classification: str) -> dict[str, Any] | None:
    for route in policy.get("routes", []):
        if route.get("classification") == classification:
            return route
    return None


def format_directory(template: str | None, now: datetime, owner: str | None) -> str | None:
    if template is None:
        return None
    return template.format(
        YYYY=now.strftime("%Y"),
        MM=now.strftime("%m"),
        DD=now.strftime("%d"),
        owner=slugify(owner or "unassigned"),
    )


def build_filename(subject: str, extension: str | None, timestamped: bool, now: datetime) -> str | None:
    if not extension:
        return None
    stem = slugify(subject)
    if not timestamped:
        return f"{stem}.{extension}"
    stamp = now.strftime("%Y-%m-%d_%H%M%S%z")
    return f"{stamp}__{stem}.{extension}"


def resolve(request: dict[str, Any], policy: dict[str, Any], now: datetime) -> dict[str, Any]:
    request_id = str(request.get("request_id") or f"save-{now.strftime('%Y%m%d%H%M%S%z')}")
    classification = str(request.get("classification") or "unknown")
    owner = request.get("owner")
    visibility = str(request.get("visibility") or "unknown")
    subject = str(request.get("subject") or "").strip()
    write_mode = str(request.get("write_mode") or "unknown")
    sensitivity = {str(item).lower() for item in request.get("sensitivity", [])}
    route = route_for(policy, classification)
    questions: list[str] = []
    defaults = policy.get("default_questions", {})

    if classification not in CLASSIFICATIONS or route is None:
        questions.append(defaults["classification"])
    if not subject:
        questions.append(defaults["subject"])
    if visibility == "unknown":
        questions.append(defaults["visibility"])
    if owner is None and (route is None or route.get("owner") is None):
        questions.append(defaults["owner"])
    if write_mode == "unknown" and route is None:
        questions.append(defaults["write_mode"])

    resolved_owner = owner if owner is not None else (route or {}).get("owner")
    resolved_visibility = visibility if visibility != "unknown" else (route or {}).get("visibility", "unknown")
    resolved_write_mode = write_mode if write_mode != "unknown" else (route or {}).get("default_write_mode", "unknown")

    sensitive = bool(sensitivity & SENSITIVE_MARKERS)
    if sensitive and visibility == "unknown" and defaults["sensitivity"] not in questions:
        questions.append(defaults["sensitivity"])

    directory = format_directory((route or {}).get("directory"), now, resolved_owner)
    filename = build_filename(
        subject,
        (route or {}).get("extension"),
        bool((route or {}).get("timestamped")),
        now,
    ) if subject else None

    known_fields = 0
    total_fields = 6
    known_fields += classification in CLASSIFICATIONS and route is not None
    known_fields += bool(subject)
    known_fields += resolved_visibility != "unknown"
    known_fields += resolved_owner is not None
    known_fields += resolved_write_mode != "unknown"
    known_fields += directory is not None and filename is not None
    confidence = round(known_fields / total_fields, 2)

    requires_confirmation = bool((route or {}).get("requires_confirmation"))
    requires_confirmation = requires_confirmation or classification in policy.get("high_impact_classifications", [])
    requires_confirmation = requires_confirmation or resolved_write_mode in policy.get("always_confirm_write_modes", [])
    requires_confirmation = requires_confirmation or (resolved_visibility == "public" and sensitive)

    if request.get("contains_credentials") is True:
        decision = "REFUSE"
        requires_confirmation = False
        questions = []
        summary = "Credential-bearing material is refused by Save Intent Resolver policy."
    elif questions:
        decision = "ASK"
        summary = "Destination is ambiguous; focused questions are required before any write claim."
    elif requires_confirmation:
        decision = "REQUIRE_CONFIRMATION"
        summary = "The route is known, but canon, doctrine, replacement, or sensitive public impact requires explicit confirmation."
    elif confidence >= float(policy["confidence_thresholds"]["save_directly"]):
        decision = "SAVE"
        summary = "The destination and write contract are unambiguous."
    else:
        decision = "SAVE_WITH_RECEIPT"
        summary = "The route is sufficiently clear for a low-risk write, provided the writer emits a receipt."

    return {
        "schema_version": "bootos.save-intent.v1",
        "request_id": request_id,
        "classification": classification if classification in CLASSIFICATIONS else "unknown",
        "owner": resolved_owner,
        "visibility": resolved_visibility,
        "destination": directory,
        "filename": filename,
        "write_mode": resolved_write_mode,
        "confidence": confidence,
        "decision": decision,
        "questions_required": questions,
        "requires_confirmation": requires_confirmation,
        "reasoning_summary": summary,
        "receipt": None,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("request", type=Path, help="JSON save request")
    parser.add_argument("--policy", type=Path, default=Path(__file__).parents[1] / "save-routing.json")
    parser.add_argument("--now", help="ISO-8601 timestamp used for deterministic filenames")
    args = parser.parse_args()

    try:
        request = load_json(args.request)
        policy = load_json(args.policy)
        now = datetime.fromisoformat(args.now) if args.now else datetime.now().astimezone()
        result = resolve(request, policy, now)
    except (OSError, ValueError, json.JSONDecodeError, KeyError) as exc:
        print(json.dumps({"error": str(exc)}), file=sys.stderr)
        return 2

    json.dump(result, sys.stdout, indent=2)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
