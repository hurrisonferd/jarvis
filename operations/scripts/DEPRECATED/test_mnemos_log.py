#!/usr/bin/env python3
"""Tests for mnemos_log bounded logging. Run: python3 operations/scripts/test_mnemos_log.py"""
import json
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from mnemos_log import append_bounded, summarize_entries

passed = failed = 0


def check(name, cond):
    global passed, failed
    if cond:
        passed += 1; print("  ok  -", name)
    else:
        failed += 1; print("FAIL  -", name)


def entry(i):
    return {"ts": f"2026-05-30T00:00:{i:02d}Z", "source_type": "github_push", "text": f"event {i}", "tags": ["development"]}


with tempfile.TemporaryDirectory() as d:
    active = Path(d) / "events.jsonl"

    # --- under bounds: appends, no rotation ---
    for i in range(3):
        r = append_bounded(active, entry(i), source="github_events", max_entries=5)
    check("appends under bound", not r["rotated"])
    check("active has 3 rows", len(active.read_text().splitlines()) == 3)
    check("no archive dir yet", not (Path(d) / "archive").exists())

    # --- crossing entry bound triggers rotation (mid-loop) ---
    rotated_any = False
    archive_seen = None
    for i in range(3, 7):
        r = append_bounded(active, entry(i), source="github_events", max_entries=5)
        if r["rotated"]:
            rotated_any = True
            archive_seen = r["archive"]
    check("rotation happened", rotated_any is True)
    check("archive file created", archive_seen and Path(archive_seen).exists())
    check("active log reset small", len(active.read_text().splitlines()) <= 3)

    # --- summary ledger written with a rollup ---
    summ = Path(d) / "summaries.jsonl"
    check("summary ledger exists", summ.exists())
    rollup = json.loads(summ.read_text().splitlines()[0])
    check("rollup is a rollup", rollup["type"] == "rollup")
    check("rollup counts the batch", rollup["count"] == 5)
    check("rollup has span", rollup["span"]["from"] and rollup["span"]["to"])
    check("rollup tallies by_type", rollup["by_type"].get("github_push") == 5)
    check("rollup keeps samples bounded", len(rollup["samples"]) <= 5)

    # --- size bound also triggers rotation ---
    active2 = Path(d) / "big.jsonl"
    big = {"ts": "2026-05-30T00:00:00Z", "source_type": "x", "text": "y" * 500, "tags": []}
    last = None
    for _ in range(40):
        last = append_bounded(active2, big, source="big", max_entries=10_000, max_bytes=4096)
    check("size bound rotates", any(Path(d).glob("archive/big.*.jsonl")))

# --- summarize is content-light ---
s = summarize_entries([entry(i) for i in range(10)], "github_events")
check("summary smaller than raw", len(json.dumps(s)) < len(json.dumps([entry(i) for i in range(10)])))

print(f"\n{passed} passed, {failed} failed")
sys.exit(1 if failed else 0)
