#!/usr/bin/env python3
"""Build a public-safe OMNI observer projection from a private command-room snapshot."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

ALLOWED_PANEL_FIELDS = {
    "system_id", "role", "state", "unread_work", "last_delta", "identity_note"
}
ALLOWED_INTERVENTION_FIELDS = {
    "intervention_type", "summary", "owner", "state", "severity"
}
FORBIDDEN_TOKENS = (
    "service_role", "SUPABASE_SERVICE_ROLE_KEY", "approval_digest", "rpc_function",
    "channel_body", "message_body", "private_relationship", "authorization", "secret"
)


def clean_record(record: dict[str, Any], allowed: set[str]) -> dict[str, Any]:
    return {key: record[key] for key in allowed if key in record}


def sanitize(source: dict[str, Any]) -> dict[str, Any]:
    room = source.get("command_room", source)
    compression = room.get("compression") or {}
    public = {
        "schema_version": "omni.observer.v1",
        "generated_at": room.get("generated_at"),
        "receipt_hash": room.get("receipt_hash"),
        "interventions": [
            clean_record(item, ALLOWED_INTERVENTION_FIELDS)
            for item in room.get("interventions", [])
            if isinstance(item, dict)
        ],
        "compression": {
            "what_changed": compression.get("what_changed", []),
            "why_it_matters": compression.get("why_it_matters", ""),
            "owners": compression.get("owners", []),
            "uncertainty": compression.get("uncertainty", []),
            "flattening_prevented": bool(compression.get("flattening_prevented", False)),
        },
        "panels": [
            clean_record(panel, ALLOWED_PANEL_FIELDS)
            for panel in room.get("panels", [])
            if isinstance(panel, dict)
        ],
    }
    encoded = json.dumps(public, sort_keys=True)
    lowered = encoded.lower()
    leaks = [token for token in FORBIDDEN_TOKENS if token.lower() in lowered]
    if leaks:
        raise ValueError(f"privileged material survived sanitization: {', '.join(leaks)}")
    required = ("generated_at", "receipt_hash")
    missing = [key for key in required if not public.get(key)]
    if missing:
        raise ValueError(f"missing required public fields: {', '.join(missing)}")
    return public


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("input", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    source = json.loads(args.input.read_text(encoding="utf-8"))
    public = sanitize(source)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(public, indent=2) + "\n", encoding="utf-8")
    print(f"wrote public observer projection: {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
