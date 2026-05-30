#!/usr/bin/env python3
"""Tests for the narrative log system. Run: python3 scripts/test_companion_log.py"""
import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from companion_log import (
    slugify, log_path, render_front_matter, parse_front_matter,
    section_notes, index_row,
)

passed = failed = 0


def check(name, cond):
    global passed, failed
    if cond:
        passed += 1; print("  ok  -", name)
    else:
        failed += 1; print("FAIL  -", name)


# --- slugify ---
check("slug lowercases + hyphenates", slugify("The Companion Entity!") == "the-companion-entity")
check("slug collapses junk", slugify("a   --  b") == "a-b")
check("slug bounded", len(slugify("x" * 200)) <= 48)
check("slug empty -> untitled", slugify("") == "untitled")

# --- chronological pathing ---
p = log_path(date(2026, 5, 30), "memory-system")
check("path has YYYY/MM folders", p.parent.name == "05" and p.parent.parent.name == "2026")
check("filename = date_slug.md", p.name == "2026-05-30_memory-system.md")

# --- front-matter round-trip ---
meta = {"title": "T", "date": "2026-05-30", "summary": "a summary line", "tags": ["companion", "memory"], "status": "active"}
fm = render_front_matter(meta)
parsed = parse_front_matter(fm + "\n# body\n")
check("front-matter round-trips title", parsed["title"] == "T")
check("front-matter round-trips summary", parsed["summary"] == "a summary line")
check("front-matter round-trips tags", parsed["tags"] == ["companion", "memory"])
check("front-matter default status", parsed["status"] == "active")
check("missing front-matter -> defaults", parse_front_matter("no header here")["status"] == "active")

# --- section notes extraction (retrieval/audit layer) ---
doc = """---
title: x
---
# x
## Context
*Note: why this exists*
some text
## Thoughts
*Note: the brainstorming*
more text
## NoNote
just text
"""
notes = section_notes(doc)
check("extracts section notes", ("Context", "why this exists") in notes)
check("extracts second note", ("Thoughts", "the brainstorming") in notes)
check("section without note skipped", all(s != "NoNote" for s, _ in notes))

# --- index row ---
row = index_row(meta, "2026/05/2026-05-30_x.md")
check("index row has summary + status", "a summary line" in row and "active" in row)
check("index row links the file", "2026-05-30_x.md)" in row)

print(f"\n{passed} passed, {failed} failed")
sys.exit(1 if failed else 0)
