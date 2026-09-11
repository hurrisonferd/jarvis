#!/usr/bin/env python3
"""Validate and publish a public-safe Omni RV instrument envelope.

Input is expected to be produced by Jarvis-Private's OMNI-RV-PUBLIC-INSTRUMENT
projector or an equivalent owner-approved sanitizer. This script never reaches
into private state; it only validates the already-sanitized envelope before
placing it in the public observer vessel.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

REQUIRED_TOP = {
    "schema_version", "generated_at", "vehicle", "performance", "capacity",
    "proof", "safety", "access_domains", "public_safe", "receipt_hash"
}
FORBIDDEN = (
    "service_role", "SUPABASE_SERVICE_ROLE_KEY", "approval_digest", "rpc_function",
    "channel_body", "message_body", "private_relationship", "authorization",
    "secret", "password", "token"
)


def validate(value: dict[str, Any]) -> dict[str, Any]:
    missing = sorted(REQUIRED_TOP - set(value))
    if missing:
        raise ValueError("missing required fields: " + ", ".join(missing))
    if value.get("schema_version") != "omni.instrument.v2":
        raise ValueError("unsupported schema_version")
    if value.get("public_safe") is not True:
        raise ValueError("public_safe must be true")
    if value.get("safety", {}).get("public_mutation") != "BLOCKED":
        raise ValueError("public mutation must remain blocked")
    if value.get("safety", {}).get("effect_authority") != "NONE":
        raise ValueError("effect authority must be NONE")
    if len(value.get("access_domains", [])) != 16:
        raise ValueError("expected 16 public-safe domain labels")
    encoded = json.dumps(value, sort_keys=True)
    lowered = encoded.lower()
    leaks = [token for token in FORBIDDEN if token.lower() in lowered]
    if leaks:
        raise ValueError("privileged material survived sanitization: " + ", ".join(leaks))
    return value


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("input", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    value = json.loads(args.input.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError("instrument envelope must be an object")
    value = validate(value)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")
    print(f"wrote public Omni instrument: {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
