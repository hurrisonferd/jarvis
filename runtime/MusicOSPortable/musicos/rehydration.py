from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path

from .source_index import TEXT_EXTENSIONS, classify, family_tags


@dataclass(frozen=True, slots=True)
class SourceFamily:
    name: str
    patterns: tuple[str, ...]
    terms: tuple[str, ...] = ()
    required: bool = False


SOURCE_FAMILIES = (
    SourceFamily(
        "musicos_vault_core",
        (
            "Jorm/Vault/GLOBAL_CAPTURE_INDEX.md",
            "Jorm/Vault/Sources/MusicOS/**/*",
        ),
        required=True,
    ),
    SourceFamily(
        "musicos_raw_exports",
        ("Jorm/Vault/Inbox/raw-chat-exports/**/*MUSICOS*",),
        required=True,
    ),
    SourceFamily(
        "musicos_recovery_ledgers",
        ("Jorm/Vault/Recovery_Ledgers/**/*MUSICOS*",),
        required=True,
    ),
    SourceFamily(
        "musicos_atlas",
        ("memory/BarberHistory/06_Project_Ideas/MusicOSAtlas/**/*",),
        required=True,
    ),
    SourceFamily(
        "inactive_music_tools",
        (
            "operations/scripts/INACTIVE/music_ears.py",
            "operations/scripts/INACTIVE/music_nlp.py",
            "operations/scripts/INACTIVE/music_distill.py",
        ),
    ),
    SourceFamily(
        "jx2_cecil_lineage",
        (
            "Jorm/Vault/Inbox/raw-chat-exports/2026-02-16_LILITH_BRANCH_01_JX2_CECIL.txt",
            "Jorm/Vault/Recovery_Ledgers/2026-02-16_LILITH_BRANCH_01_JX2_CECIL.md",
        ),
        required=True,
    ),
    SourceFamily(
        "shaka_bones_seed",
        ("Jorm/Vault/**/*", "memory/**/*"),
        ("shaka bones", "SHAKA_MAIN", "JX2_SHAKA_REV2"),
    ),
    SourceFamily(
        "cecil_sweeps_resolver",
        ("Jorm/Vault/**/*", "memory/**/*"),
        ("cecil sweep", "CECIL_LINK", "resolver index"),
    ),
    SourceFamily(
        "old_gpt_musicos_memory",
        ("Jorm/Vault/**/*", "memory/**/*"),
        ("GPT", "MusicOS"),
    ),
)


def _matches_terms(path: Path, terms: tuple[str, ...]) -> bool:
    if not terms:
        return True
    text = path.read_text(encoding="utf-8", errors="replace").lower()
    return all(term.lower() in text for term in terms)


def _family_files(repo: Path, family: SourceFamily) -> list[Path]:
    found: set[Path] = set()
    for pattern in family.patterns:
        for path in repo.glob(pattern):
            if (
                path.is_file()
                and path.suffix.lower() in TEXT_EXTENSIONS
                and _matches_terms(path, family.terms)
            ):
                found.add(path.resolve())
    return sorted(found)


def rehydrate_sources(repo: Path, output: Path) -> dict:
    repo = repo.resolve()
    if not (repo / "Jorm" / "Vault").is_dir():
        raise FileNotFoundError(f"JORM/Vault not found under repository: {repo}")

    family_receipts: list[dict] = []
    source_receipts: dict[str, dict] = {}
    for family in SOURCE_FAMILIES:
        files = _family_files(repo, family)
        state = "CONFIRMED" if files else "UNKNOWN"
        family_receipts.append(
            {
                "family": family.name,
                "state": state,
                "required": family.required,
                "paths": [str(path.relative_to(repo)) for path in files],
            }
        )
        for path in files:
            blob = path.read_bytes()
            rel = str(path.relative_to(repo))
            receipt = source_receipts.setdefault(
                rel,
                {
                    "path": rel,
                    "sha256": hashlib.sha256(blob).hexdigest(),
                    "size_bytes": len(blob),
                    "status": classify(path),
                    "families": [],
                    "signals": family_tags(
                        blob.decode("utf-8", errors="replace"), path
                    ),
                    "canon_promotion": "PROHIBITED_AUTOMATICALLY",
                },
            )
            receipt["families"].append(family.name)

    for receipt in source_receipts.values():
        receipt["families"] = sorted(set(receipt["families"]))
        receipt["signals"] = sorted(set(receipt["signals"]))

    missing_required = [
        item["family"]
        for item in family_receipts
        if item["required"] and item["state"] != "CONFIRMED"
    ]
    stable = {
        "schema": "musicos-rehydration-v1",
        "authority": {
            "private_truth": "Jarvis-Private/MusicOS/registry/",
            "public_role": "carry-runtime-and-reference",
        },
        "families": family_receipts,
        "sources": sorted(source_receipts.values(), key=lambda item: item["path"]),
        "missing_required": missing_required,
    }
    receipt_sha256 = hashlib.sha256(
        json.dumps(stable, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()
    payload = {
        **stable,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "source_count": len(source_receipts),
        "coverage": "PASS" if not missing_required else "PARTIAL",
        "receipt_sha256": receipt_sha256,
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    return payload
