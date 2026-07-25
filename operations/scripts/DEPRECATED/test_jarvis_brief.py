#!/usr/bin/env python3
"""Tests for jarvis_brief.compose_brief. Run: python3 operations/scripts/test_jarvis_brief.py"""
import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from jarvis_brief import compose_brief, days_until, COURT_DATE

passed = failed = 0


def check(name, cond):
    global passed, failed
    if cond:
        passed += 1; print("  ok  -", name)
    else:
        failed += 1; print("FAIL  -", name)


# --- countdown math ---
check("days_until counts forward", days_until(date(2026, 6, 24), date(2026, 6, 20)) == 4)
check("court date is June 24", COURT_DATE == date(2026, 6, 24))

# --- court line surfaces within 30 days, hidden far out ---
near = compose_brief(date(2026, 6, 20), ["feat: x"], [])
check("court countdown shows within 30d", "June 24" in near["body"])
far = compose_brief(date(2026, 1, 1), ["feat: x"], [])
check("court countdown hidden far out", "June 24" not in far["body"])

# --- day-of message is present, not a countdown ---
dayof = compose_brief(date(2026, 6, 24), [], [])
check("day-of speaks directly", "Today is June 24" in dayof["body"] and "with you" in dayof["body"])

# --- commit line reflects activity ---
busy = compose_brief(date(2026, 6, 20), ["feat: a", "fix: b", "refactor: c"], [])
check("counts commits", "3 commits" in busy["body"])
quiet = compose_brief(date(2026, 6, 20), [], [])
check("quiet day acknowledged", "Quiet" in quiet["body"])

# --- pending surfaces ---
pend = compose_brief(date(2026, 6, 20), ["feat: x"], ["P08", "P17"])
check("pending listed", "P08" in pend["body"] and "P17" in pend["body"])

# --- always has a title and non-empty body ---
check("title present", compose_brief(date(2026, 6, 20), [], [])["title"].startswith("JARVIS —"))
check("body never empty", len(compose_brief(date(2026, 6, 20), [], [])["body"]) > 0)

# --- body bounded for push truncation ---
huge = compose_brief(date(2026, 6, 20), ["x" * 400], ["P01", "P02", "P03"])
check("body bounded <= 200", len(huge["body"]) <= 200)

print(f"\n{passed} passed, {failed} failed")
sys.exit(1 if failed else 0)
