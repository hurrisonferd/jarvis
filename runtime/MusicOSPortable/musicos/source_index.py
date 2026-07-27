from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

from .models import SourceRecord

TEXT_EXTENSIONS = {".md", ".txt", ".json", ".yaml", ".yml", ".py", ".ts", ".js", ".toml"}
SIGNALS = {
    "MusicOS": re.compile(r"\bMusicOS\b", re.I),
    "PromptAI": re.compile(r"\bPromptAI\b", re.I),
    "RemixAI": re.compile(r"\bRemixAI\b", re.I),
    "FollinsAI": re.compile(r"\bFollinsAI\b", re.I),
    "CNSAI": re.compile(r"\bCNSAI\b", re.I),
    "EMDRAI": re.compile(r"\bEMDRAI\b", re.I),
    "ColorAI": re.compile(r"\bColorAI\b", re.I),
    "MetricsAI": re.compile(r"\bMetricsAI\b", re.I),
    "Music7": re.compile(r"Music\s*7|The Music 7", re.I),
    "Music13": re.compile(r"Music\s*13|The Music 13", re.I),
    "rail": re.compile(r"rail authority|never let the rail drop|many parts, one rail", re.I),
    "RGB": re.compile(r"\bRGB\b|R=Power|G=Groove|B=Range", re.I),
    "OSDD": re.compile(r"\bOSDD\b|dissociat", re.I),
    "runtime": re.compile(r"runtime|engine|kernel|compile|boot", re.I),
}


def classify(path: Path) -> str:
    p = path.as_posix().lower()
    if "/inbox/" in p or "raw-chat-exports" in p or "full-transcript" in p:
        return "RAW"
    if "/canon/" in p:
        return "CANON"
    if "recovery_ledgers" in p or "ledger" in path.name.lower():
        return "LEDGER"
    if path.suffix.lower() in {".py", ".ts", ".js"}:
        return "IMPLEMENTATION"
    return "UNKNOWN"


def family_tags(text: str, path: Path) -> list[str]:
    tags = [name for name, pattern in SIGNALS.items() if pattern.search(text)]
    if "musicos" in path.as_posix().lower() and "MusicOS" not in tags:
        tags.insert(0, "MusicOS")
    return tags


def index_vault(vault: Path, output: Path) -> dict:
    if not vault.exists() or not vault.is_dir():
        raise FileNotFoundError(f"Vault directory not found: {vault}")
    records: list[SourceRecord] = []
    unreadable: list[dict] = []
    for path in sorted(p for p in vault.rglob("*") if p.is_file()):
        if path.suffix.lower() not in TEXT_EXTENSIONS:
            continue
        try:
            blob = path.read_bytes()
            text = blob.decode("utf-8", errors="replace")
            signals = family_tags(text, path)
            if not signals and "musicos" not in path.as_posix().lower():
                continue
            stat = path.stat()
            records.append(SourceRecord(
                path=str(path.relative_to(vault)),
                sha256=hashlib.sha256(blob).hexdigest(),
                size_bytes=len(blob),
                modified_ns=stat.st_mtime_ns,
                status=classify(path),
                families=sorted(set(signals)),
                signals=sorted(set(signals)),
            ))
        except Exception as exc:
            unreadable.append({"path": str(path), "error": str(exc)})
    counts: dict[str, int] = {}
    for record in records:
        counts[record.status] = counts.get(record.status, 0) + 1
    payload = {
        "schema": "musicos-source-index-v1",
        "vault": str(vault.resolve()),
        "source_count": len(records),
        "status_counts": counts,
        "unreadable": unreadable,
        "sources": [record.to_dict() for record in records],
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    return payload
