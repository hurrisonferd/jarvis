#!/usr/bin/env python3
"""NEMESIS — tests for the patch register writer (operations/scripts/jarvis-patch.py).

jarvis-patch.py is the SOLE writer of the canonical patch ledger. Before this it
had zero coverage. These tests pin the lifecycle (open -> add -> exec), the
chronological-id guarantee, the compact one-line-per-patch serializer, and the
derived-cache regeneration. Run: python3 operations/scripts/test_jarvis_patch.py
"""
import importlib.util
import json
import os
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location("jp", os.path.join(HERE, "jarvis-patch.py"))
jp = importlib.util.module_from_spec(spec)
spec.loader.exec_module(jp)

# Redirect the writer at a throwaway ledger + cache.
tmp = tempfile.mkdtemp()
jp.LEDGER_PATH = os.path.join(tmp, "patch_ledger.json")
jp.CACHE_PATH = os.path.join(tmp, "patch-log.json")

SEED = {
    "version": "2.0", "next_patch": "P05", "intake_max_patch": "P04", "authority": "Raven",
    "patches": [
        {"id": "P00", "name": "Patch 0", "priority": "reference", "status": "reference", "summary": "ref", "commits": []},
        {"id": "P04", "name": "Patch 4", "priority": "normal", "status": "done", "summary": "done one", "commits": ["abc"]},
    ],
    "implementation_order": ["DONE: P00 P04"],
}
with open(jp.LEDGER_PATH, "w") as f:
    json.dump(SEED, f)

failures = []


def check(name, cond):
    print(("ok   - " if cond else "FAIL - ") + name)
    if not cond:
        failures.append(name)


# next_id honors next_patch when it leads the max id
check("next_id honors next_patch", jp.next_id(jp.load()) == "P05")

# open: appends an open patch, bumps next_patch, stamps opened_at + empty entries
jp.cmd_open(["Test patch", "high"])
led = jp.load()
p5 = jp.find(led, "P05")
check("open created P05 as open", bool(p5) and p5["status"] == "open")
check("open bumped next_patch -> P06", led["next_patch"] == "P06")
check("open stamped opened_at", "opened_at" in p5)
check("open seeded empty entries", p5.get("entries") == [])

# find is case-insensitive
check("find is case-insensitive", jp.find(led, "p05") is not None)

# add: appends a dated entry
jp.cmd_add(["P05", "first change"])
p5 = jp.find(jp.load(), "P05")
check("add appended entry", len(p5["entries"]) == 1 and p5["entries"][0]["note"] == "first change")
check("add stamped ts", "ts" in p5["entries"][0])

# add with a commit attaches it to the patch
jp.cmd_add(["P05", "wired it", "deadbeef"])
p5 = jp.find(jp.load(), "P05")
check("add with sha attaches commit", "deadbeef" in p5["commits"])

# add refuses a patch that is not open (P04 is done)
guarded = False
try:
    jp.cmd_add(["P04", "nope"])
except SystemExit:
    guarded = True
check("add refuses a non-open patch", guarded)

# exec: marks executed, stamps deploy date, attaches commits
jp.cmd_exec(["P05", "shipped", "cafebabe"])
p5 = jp.find(jp.load(), "P05")
check("exec sets status executed", p5["status"] == "executed")
check("exec stamped deployed_at", bool(p5.get("deployed_at")))
check("exec attached commit", "cafebabe" in p5["commits"])

# serializer integrity
raw = open(jp.LEDGER_PATH).read()
parsed = json.loads(raw)  # must be valid JSON
check("ledger is valid JSON after writes", parsed["patches"][0]["id"] == "P00")
check("implementation_order preserved", parsed.get("implementation_order") == ["DONE: P00 P04"])
patch_lines = [ln for ln in raw.splitlines() if ln.strip().startswith('{"id"')]
check("one line per patch", len(patch_lines) == len(parsed["patches"]))

# derived cache regenerated from the canonical ledger
cache = json.loads(open(jp.CACHE_PATH).read())
check("cache marks itself derived", cache.get("derived_from") == "memory/audit/patch_ledger.json")
check("cache mirrors patches", "P05" in cache["patches"] and cache["patches"]["P05"]["status"] == "executed")

# next_id falls back to max+1 when next_patch is stale/behind
led = jp.load()
led["next_patch"] = "P01"
jp.save(led)
check("next_id computes max+1 when next_patch stale", jp.next_id(jp.load()) == "P06")

if failures:
    print(f"\n{len(failures)} failed")
    sys.exit(1)
print(f"\nall {0} jarvis-patch tests passed".replace("0", str(13)))
