#!/usr/bin/env python3
"""Tests for the remember loop. Run: python3 operations/scripts/test_companion_remember.py"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from companion_remember import resolve, ledger_entry, seed_record, CATEGORIES

passed = failed = 0


def check(name, cond):
    global passed, failed
    if cond:
        passed += 1; print("  ok  -", name)
    else:
        failed += 1; print("FAIL  -", name)


# --- category routing ---
for cat, (_, st) in CATEGORIES.items():
    r = resolve(cat)
    check(f"'{cat}' resolves", r is not None and r[1] == st and r[0].name == f"{cat}.md")

check("raven -> raven_profile source", resolve("raven")[1] == "raven_profile")
check("relationship -> decision source", resolve("relationship")[1] == "decision")

# --- project sub-routing ---
proj = resolve("project:grid")
check("project routes to projects/ subfolder", proj is not None and proj[0].parent.name == "projects" and proj[0].name == "grid.md")
check("project normalized category", proj[2] == "project:grid")
check("project with spaces -> hyphen", resolve("project:pachinko bounce")[0].name == "pachinko-bounce.md")

# --- session routing ---
sess = resolve("session")
check("session routes to sessions/ + dated file", sess is not None and sess[0].parent.name == "sessions" and sess[0].name.endswith(".md"))
check("session source_type", sess[1] == "session_summary")

# --- unknowns rejected ---
check("unknown category -> None", resolve("nonsense") is None)
check("empty project -> None", resolve("project:") is None)
check("case-insensitive", resolve("RAVEN") is not None)

# --- ledger entry shape ---
e = ledger_entry("raven", "  a fact about raven  ", "raven_profile")
check("ledger trims text", e["text"] == "a fact about raven")
check("ledger has ts/category/source_type", all(k in e for k in ("ts", "category", "source_type")))

# --- seed record (queued for the live-memory sync) ---
s = seed_record("a fact", "raven_profile", "raven")
check("seed has text/source_type/tags", all(k in s for k in ("text", "source_type", "tags")))
check("seed tagged learned + category", s["tags"] == ["learned", "raven"])
check("project seed strips subname in tag", seed_record("x", "raven_profile", "project:grid")["tags"] == ["learned", "project"])

print(f"\n{passed} passed, {failed} failed")
sys.exit(1 if failed else 0)
