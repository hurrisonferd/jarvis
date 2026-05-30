#!/usr/bin/env python3
"""Tests for capture_decisions.extract_decision. Run: python3 scripts/test_capture_decisions.py"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from capture_decisions import extract_decision

TS = "2026-05-30T00:00:00Z"
passed = failed = 0


def check(name, cond):
    global passed, failed
    if cond:
        passed += 1; print("  ok  -", name)
    else:
        failed += 1; print("FAIL  -", name)


# feat -> decision
d = extract_decision("abc1234def", "feat(odin): intent router [GL7-OK]", TS)
check("feat is a decision", d is not None)
check("sha truncated to 7", d and d["sha"] == "abc1234")
check("scope -> tag", d and "odin" in d["tags"])
check("gl7 marker -> tag", d and "gl7" in d["tags"])
check("marker stripped from text", d and "[GL7-OK]" not in d["text"])

# refactor -> decision
check("refactor is a decision", extract_decision("x", "refactor(server): carve templates", TS) is not None)

# explicit [DECISION] marker on any type -> decision
check("[DECISION] marker forces capture", extract_decision("y", "chore: pick cloud-first stack [DECISION]", TS) is not None)

# noise types -> skipped
check("chore skipped", extract_decision("z", "chore(mnemos): session ledger [skip ci]", TS) is None)
check("docs skipped", extract_decision("z", "docs: update readme", TS) is None)
check("ci skipped", extract_decision("z", "ci: add workflow", TS) is None)
check("plain fix skipped", extract_decision("z", "fix: typo", TS) is None)

# empty / malformed
check("empty message -> None", extract_decision("z", "", TS) is None)
check("non-conventional subject -> None", extract_decision("z", "random words here", TS) is None)

print(f"\n{passed} passed, {failed} failed")
sys.exit(1 if failed else 0)
