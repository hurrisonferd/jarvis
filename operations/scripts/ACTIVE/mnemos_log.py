#!/usr/bin/env python3
"""MNEMOS — bounded logging with summarization.

The old logs capped by dropping the oldest entry, so memory just evaporated.
This keeps the signal: when an active log crosses a size or count bound, it
rolls — the full batch is archived, a compact rollup is written to a summary
ledger, and the active log starts fresh. Nothing is silently lost, nothing
bloats unbounded. SKADI writes; MNEMOS remembers; HUGINN can reconcile later.

Pure + testable. The GitHub Actions workflows call `append_bounded`.

Run tests: python3 operations/scripts/test_mnemos_log.py
"""
import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

# Defaults — a JSONL entry is small, so ~64 KB is a few hundred events.
DEFAULT_MAX_BYTES = 64 * 1024
DEFAULT_MAX_ENTRIES = 250


def _read_jsonl(path: Path) -> list:
    if not path.exists():
        return []
    out = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line:
            try:
                out.append(json.loads(line))
            except Exception:
                pass
    return out


def _write_jsonl(path: Path, rows: list) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(json.dumps(r, ensure_ascii=False) for r in rows) + ("\n" if rows else ""), encoding="utf-8")


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()[:19] + "Z"


def summarize_entries(entries: list, source: str) -> dict:
    """Compact rollup of a batch — counts and span, not content. No bloat."""
    times = sorted(e.get("ts", "") for e in entries if e.get("ts"))
    by_type = Counter(e.get("source_type") or e.get("event") or "unknown" for e in entries)
    tags = Counter(t for e in entries for t in (e.get("tags") or []))
    # A few representative subjects, truncated — enough to recall the gist.
    samples = []
    for e in entries[-5:]:
        s = (e.get("text") or e.get("msg") or "").strip().replace("\n", " ")
        if s:
            samples.append(s[:80])
    return {
        "ts": _now(),
        "type": "rollup",
        "source": source,
        "count": len(entries),
        "span": {"from": times[0] if times else None, "to": times[-1] if times else None},
        "by_type": dict(by_type),
        "by_tag": dict(tags.most_common(8)),
        "samples": samples,
    }


def _over_bounds(rows: list, max_entries: int, max_bytes: int) -> bool:
    if len(rows) >= max_entries:
        return True
    size = sum(len(json.dumps(r, ensure_ascii=False)) + 1 for r in rows)
    return size >= max_bytes


def append_bounded(
    active_path,
    entry: dict,
    *,
    source: str,
    max_entries: int = DEFAULT_MAX_ENTRIES,
    max_bytes: int = DEFAULT_MAX_BYTES,
    archive_dir=None,
    summary_path=None,
) -> dict:
    """Append `entry` to the active log, rotating with a summary if bounds hit.

    Bounds are checked BEFORE appending, so the new entry always lands in a
    fresh, non-full log. Returns {"rotated": bool, "archive": path|None}.
    """
    active_path = Path(active_path)
    archive_dir = Path(archive_dir) if archive_dir else active_path.parent / "archive"
    summary_path = Path(summary_path) if summary_path else active_path.parent / "summaries.jsonl"

    rows = _read_jsonl(active_path)
    rotated = False
    archive_file = None

    if rows and _over_bounds(rows, max_entries, max_bytes):
        # Roll: summarize the full batch, archive it, start fresh.
        summary = summarize_entries(rows, source)
        archive_dir.mkdir(parents=True, exist_ok=True)
        stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S")
        archive_file = archive_dir / f"{active_path.stem}.{stamp}.jsonl"
        _write_jsonl(archive_file, rows)

        summaries = _read_jsonl(summary_path)
        summaries.append(summary)
        _write_jsonl(summary_path, summaries)

        rows = []
        rotated = True

    rows.append(entry)
    _write_jsonl(active_path, rows)

    return {"rotated": rotated, "archive": str(archive_file) if archive_file else None, "active_count": len(rows)}
