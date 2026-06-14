#!/usr/bin/env python3
"""rollup.py — the compression ladder (bounded files -> weekly/monthly/yearly compilations).

Raven's model: append logs grow unbounded; bound them by rolling detail UP into
timestamped compilation summaries (week -> month -> year). Nothing is deleted — the raw
archive is retained (graves discipline); the compilations POINT at it (JMS law: references,
never truth) and carry a freshness stamp. You navigate by summary and descend to raw only
when needed (navigable time, not a pile of records).

Source: mnemos/memories/growth_archive.jsonl (timestamped session entries).
Output: logs/compilation/{yearly,monthly,weekly}/*.md
Run standalone; schedule via the Pulse for auto-maintenance once Supabase is ungated.
"""
from __future__ import annotations
import ast
import json
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[3]
ARCHIVE = ROOT / "mnemos" / "memories" / "growth_archive.jsonl"
OUT = ROOT / "logs" / "compilation"


def _aslist(v):
    if isinstance(v, list):
        return v
    try:
        x = ast.literal_eval(str(v))
        return x if isinstance(x, list) else [x]
    except Exception:
        return [v] if v else []


def _dt(e: dict) -> datetime | None:
    sid = str(e.get("session_id", ""))
    for fmt, s in ((("%Y%m%d_%H%M%S"), sid), (("%Y-%m-%d"), str(e.get("date", "")))):
        try:
            return datetime.strptime(s, fmt)
        except Exception:
            continue
    return None


def _summarize(entries: list[dict], period: str, label: str, now: str) -> str:
    sessions = len(entries)
    exch = sum(int(str(e.get("exchanges", 0)) or 0) for e in entries)
    aligns = [float(str(e.get("alignment", 0)) or 0) for e in entries]
    avg = round(sum(aligns) / len(aligns), 3) if aligns else 0
    patches = sorted({p for e in entries for p in _aslist(e.get("patches_touched"))})
    topics = sorted({t for e in entries for t in _aslist(e.get("topics"))})
    built = sum(len(_aslist(e.get("built"))) for e in entries)
    refs = [str(e.get("session_id", "")) for e in entries]
    insights = [str(e.get("key_insight", "")).strip() for e in entries if e.get("key_insight")]
    # keep a bounded sample of insights (first+last few) — the rest stay in the archive
    sample = insights[:3] + (["…"] + insights[-2:] if len(insights) > 5 else insights[3:])
    lines = [
        f"# Compilation — {label} ({period})",
        "",
        f"generated: {now} · source: mnemos/memories/growth_archive.jsonl · sessions: {sessions}",
        "_JMS: this summary points at the archive; raw entries are retained there, never duplicated here._",
        "",
        f"- **sessions:** {sessions} · **exchanges:** {exch} · **avg alignment:** {avg}",
        f"- **patches touched:** {', '.join(patches) or '—'}",
        f"- **topics:** {', '.join(topics) or '—'}",
        f"- **built:** {built} artifacts",
        "- **key insights (sampled — full set in the archive):**",
    ]
    lines += [f"  - {s}" for s in sample if s and s != "…"] or ["  - —"]
    lines += ["", f"- **session refs:** {', '.join(refs)}", ""]
    return "\n".join(lines)


def build() -> dict:
    if not ARCHIVE.exists():
        return {"error": "no archive"}
    entries = []
    for line in ARCHIVE.read_text().splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            entries.append(json.loads(line))
        except Exception:
            continue
    now = datetime.now(timezone.utc)
    stamp = f"{now.strftime('%Y-%m-%dT%H:%M:%SZ')} ({now.astimezone(ZoneInfo('America/New_York')).strftime('%Y-%m-%d %H:%M %Z')})"

    buckets: dict[str, dict[str, list]] = {"yearly": defaultdict(list), "monthly": defaultdict(list), "weekly": defaultdict(list)}
    for e in entries:
        dt = _dt(e)
        if not dt:
            continue
        iso = dt.isocalendar()
        buckets["yearly"][f"{dt.year}"].append(e)
        buckets["monthly"][f"{dt.year}-{dt.month:02d}"].append(e)
        buckets["weekly"][f"{iso[0]}-W{iso[1]:02d}"].append(e)

    written = 0
    for period, group in buckets.items():
        d = OUT / period
        d.mkdir(parents=True, exist_ok=True)
        for label, items in sorted(group.items()):
            (d / f"{label}.md").write_text(_summarize(items, period, label, stamp) + "\n")
            written += 1
    return {"entries": len(entries), "files": written, "stamp": stamp}


def main() -> int:
    r = build()
    if r.get("error"):
        print(f"rollup: {r['error']}")
        return 0
    print(f"rollup: {r['entries']} entries -> {r['files']} compilation logs (week/month/year) @ {r['stamp']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
