#!/usr/bin/env python3
"""Hydrate an ISO scaffold into one auditable runtime bundle.

Uses only the Python standard library. It reads the ISO manifest, identity
files, current state, provenance policy, and JSON memory records. Every loaded
file receives a SHA-256 digest so the bundle can be audited later.
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
            raise RuntimeError(f"Memory record must be an object: {path.relative_to(ROOT)}")
        records.append(value)
        hashes[str(path.relative_to(ROOT))] = digest
    return records, hashes


def hydrate() -> dict[str, Any]:
    manifest, manifest_hash = read_json(ROOT / "ISO.json")
    if not isinstance(manifest, dict):
        raise RuntimeError("ISO.json must contain a JSON object")

    required = {"schema_version", "iso_id", "display_name", "files", "memory", "governance"}
    missing = sorted(required - manifest.keys())
    if missing:
        raise RuntimeError(f"ISO.json is missing required keys: {', '.join(missing)}")

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

    memory_map = manifest["memory"]
    if not isinstance(memory_map, dict):
        raise RuntimeError("ISO.json memory must be an object")

    memories: dict[str, list[dict[str, Any]]] = {}
    for memory_type, relative in memory_map.items():
        records, memory_hashes = load_memory(ROOT / str(relative))
        memories[memory_type] = records
        hashes.update(memory_hashes)

    return {
        "bundle_schema": "simos.iso-hydration-bundle.v1",
        "iso": manifest,
        "documents": documents,
        "structured": structured,
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
        args.write.write_text(json.dumps(bundle, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    if args.json:
        print(json.dumps(bundle, indent=2, ensure_ascii=False))
    else:
        iso = bundle["iso"]
        memory_count = sum(len(records) for records in bundle["memory"].values())
        print(f"ISO loaded: {iso['display_name']} ({iso['iso_id']})")
        print(f"Identity documents: {len(bundle['documents'])}")
        print(f"Structured state files: {len(bundle['structured'])}")
        print(f"Memory records: {memory_count}")
        print(f"Audited source files: {len(bundle['file_hashes'])}")
        if args.write:
            print(f"Bundle written: {args.write}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
