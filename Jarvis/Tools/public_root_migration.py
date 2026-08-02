#!/usr/bin/env python3
"""Copy, verify, and optionally retire mapped public-root directory families."""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import subprocess
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
MAP_PATH = ROOT / "Jarvis/Docs/Reorganization/PUBLIC-ROOT-MIGRATION-MAP.json"
MANIFEST_PATH = ROOT / "Jarvis/Docs/Reorganization/PUBLIC-ROOT-MIGRATION-MANIFEST.json"
CONTROL_ROOTS = {".git", ".github", "Jarvis", "ISOs", "I Ching", "Personal Projects", "Evidence"}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def tracked_files() -> list[str]:
    result = subprocess.run(
        ["git", "ls-files", "-z"], cwd=ROOT, check=True, capture_output=True
    )
    return [item.decode("utf-8") for item in result.stdout.split(b"\0") if item]


def load_map() -> dict[str, Any]:
    value = json.loads(MAP_PATH.read_text(encoding="utf-8"))
    if value.get("schema_version") != "jarvis.public-root-migration-map.v1":
        raise SystemExit("Unsupported migration map")
    return value


def relative_files(source: Path) -> list[Path]:
    return sorted(path for path in source.rglob("*") if path.is_file())


def copy_family(source_rel: str, destination_rel: str) -> dict[str, Any]:
    source = ROOT / source_rel
    destination = ROOT / destination_rel
    if not source.exists():
        return {
            "source": source_rel,
            "destination": destination_rel,
            "status": "SOURCE_ABSENT",
            "files": [],
        }

    rows: list[dict[str, Any]] = []
    for source_file in relative_files(source):
        relative = source_file.relative_to(source)
        destination_file = destination / relative
        destination_file.parent.mkdir(parents=True, exist_ok=True)
        source_hash = sha256(source_file)
        if destination_file.exists():
            destination_hash = sha256(destination_file)
            if destination_hash != source_hash:
                raise SystemExit(
                    f"Collision with different content: {destination_file.relative_to(ROOT)}"
                )
        else:
            shutil.copy2(source_file, destination_file)
            destination_hash = sha256(destination_file)
        if destination_hash != source_hash:
            raise SystemExit(f"Hash mismatch: {source_file} -> {destination_file}")
        rows.append(
            {
                "source": str(source_file.relative_to(ROOT)),
                "destination": str(destination_file.relative_to(ROOT)),
                "sha256": source_hash,
                "verified": True,
            }
        )
    return {
        "source": source_rel,
        "destination": destination_rel,
        "status": "VERIFIED" if rows else "EMPTY",
        "files": rows,
    }


def unresolved_roots(files: list[str], mapped_sources: list[str]) -> list[str]:
    mapped_heads = {Path(item).parts[0] for item in mapped_sources}
    roots = {Path(item).parts[0] for item in files if Path(item).parts}
    return sorted(root for root in roots if root not in CONTROL_ROOTS | mapped_heads)


def retire(manifest: dict[str, Any]) -> None:
    if manifest.get("overall_status") != "VERIFIED":
        raise SystemExit("Retirement blocked: manifest is not VERIFIED")
    for family in manifest["families"]:
        if family["status"] != "VERIFIED":
            continue
        for row in family["files"]:
            source = ROOT / row["source"]
            destination = ROOT / row["destination"]
            if not destination.exists() or sha256(destination) != row["sha256"]:
                raise SystemExit(f"Retirement parity failed: {row['source']}")
            if source.exists():
                source.unlink()
    for path in sorted(ROOT.rglob("*"), reverse=True):
        if path.is_dir() and path != ROOT:
            try:
                path.rmdir()
            except OSError:
                pass


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("mode", choices=("copy", "verify", "retire"))
    args = parser.parse_args()

    mapping = load_map()
    families = [copy_family(row["source"], row["destination"]) for row in mapping["mappings"]]
    tracked = tracked_files()
    manifest = {
        "schema_version": "jarvis.public-root-migration-manifest.v1",
        "mode": args.mode,
        "families": families,
        "overall_status": "VERIFIED"
        if all(row["status"] in {"VERIFIED", "SOURCE_ABSENT", "EMPTY"} for row in families)
        else "BLOCKED",
        "mapped_file_count": sum(len(row["files"]) for row in families),
        "unresolved_root_entries": unresolved_roots(
            tracked, [row["source"] for row in mapping["mappings"]]
        ),
        "retirement_enabled": bool(mapping.get("retirement", {}).get("enabled")),
    }
    MANIFEST_PATH.parent.mkdir(parents=True, exist_ok=True)
    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    if args.mode == "retire":
        if not manifest["retirement_enabled"]:
            raise SystemExit("Retirement blocked by migration map")
        retire(manifest)
    print(json.dumps({
        "status": manifest["overall_status"],
        "mapped_file_count": manifest["mapped_file_count"],
        "unresolved_root_entries": manifest["unresolved_root_entries"],
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
