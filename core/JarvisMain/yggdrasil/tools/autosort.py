"""autosort — JSS-driven file placement (the JMS law in action).

For status-managed roots (Ideas/, Implementation/, Breakthroughs/), every governed object
should live in the subfolder matching its JSS status. This tool reports mismatches and,
with --apply, relocates the file via `git mv`, preserves its JNL, and updates the LAL
location + the JD entry source. Structure follows state.

Usage:
  python core/JarvisMain/yggdrasil/tools/autosort.py            # dry-run: report what would move
  python core/JarvisMain/yggdrasil/tools/autosort.py --apply    # perform the moves
Exit 1 (dry-run) if anything is out of place — usable as a CI gate.
"""
from __future__ import annotations
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
JD_DIR = ROOT / "JarvisMain" / "yggdrasil" / "jd" / "entries"
REG_PATH = ROOT / "JarvisMain" / "yggdrasil" / "lal" / "address-registry.json"

# Status-managed roots (prefixes). Periphery roots live under Side/.
MANAGED_ROOTS = ("JarvisSide/Ideas", "core/JarvisMain/Implementation", "JarvisSide/Breakthroughs")
# JMMS memory lane: the `memory` tier (JSTM/JLTM/JATM) drives the subfolder, exactly as JSS
# status does for the managed roots. A memory entry with no `memory:` field is the lane index
# and stays put. Owner (shared by default; jarvis/ayre/raven the rare exception) is a tag, not a folder.
MEMORY_ROOT = "core/JarvisMain/Architecture/identity/memory"
MEM_TIERS = ("jitm", "jstm", "jltm", "jatm")
# Project artifacts stay flat (status lives in frontmatter + registries); only the
# terminal states relocate, into the project's own archive shelf.
PROJECTS_ROOT = "JarvisSide/Projects"
ARCHIVE_ROOT = "JarvisSide/Archive"
TERMINAL = ("ARCHIVED", "DEPRECATED")
FM = re.compile(r"^---\n(.*?)\n---", re.DOTALL)


def field(text: str, key: str) -> str:
    m = re.search(rf"^{key}:\s*(.*)$", text, re.MULTILINE)
    return m.group(1).strip() if m else ""


def desired_path(location: str, status: str) -> str | None:
    """Return the status-correct path for a managed-root object, or None if already correct."""
    # Project artifacts: flat until terminal, then -> Archive/<Project>/<file>.
    if location.startswith(PROJECTS_ROOT + "/"):
        if status not in TERMINAL:
            return None
        rest = location[len(PROJECTS_ROOT) + 1:].split("/")
        return "/".join([ARCHIVE_ROOT, rest[0], rest[-1]])
    root = next((r for r in MANAGED_ROOTS if location == r or location.startswith(r + "/")), None)
    if not root:
        return None
    rest = location[len(root) + 1:].split("/")  # segments below the root
    sub = status.lower()
    tail = rest[1:] if len(rest) >= 2 else rest    # below the status subfolder
    # already correct if the current subfolder matches the status (case-insensitive)
    if rest and rest[0].lower() == sub:
        return None
    return "/".join([root, sub, *tail])


def desired_mem_path(location: str) -> str | None:
    """Memory lane: sort by the file's `memory` tier (jstm/jltm/jatm). No tier = index, stays."""
    p = ROOT / location
    if not p.exists():
        return None
    tier = field(p.read_text(), "memory").lower()
    if tier not in MEM_TIERS:
        return None  # the lane index / untiered note — leave it where it is
    rest = location[len(MEMORY_ROOT) + 1:].split("/")
    if rest and rest[0].lower() == tier:
        return None  # already in its tier folder
    return "/".join([MEMORY_ROOT, tier, rest[-1]])


def main() -> int:
    apply = "--apply" in sys.argv[1:]
    reg = json.loads(REG_PATH.read_text())
    moves = []
    for rec in reg["records"]:
        loc, status = rec["location"], rec.get("status", "ACTIVE")
        if (ROOT / loc).is_dir():
            continue  # folder-anchored containers are structure, not sortable objects
        tgt = desired_mem_path(loc) if loc.startswith(MEMORY_ROOT + "/") else desired_path(loc, status)
        if tgt:
            moves.append((rec["jnl"], loc, tgt, rec.get("status", "ACTIVE")))

    if not moves:
        print(f"autosort: all managed-root objects are status-sorted ({len(reg['records'])} scanned).")
        return 0

    print(f"autosort: {len(moves)} object(s) out of place" + (" — applying:" if apply else " (dry-run):"))
    for jnl, src, tgt, status in moves:
        print(f"  [{status}] {jnl}\n      {src}\n   -> {tgt}")
        if not apply:
            continue
        src_p, tgt_p = ROOT / src, ROOT / tgt
        if not src_p.exists():
            print(f"      ! source missing, skipping")
            continue
        tgt_p.parent.mkdir(parents=True, exist_ok=True)
        subprocess.run(["git", "mv", src, tgt], cwd=ROOT, check=True)
        # update LAL location (JNL preserved — JMS law)
        for rec in reg["records"]:
            if rec["jnl"] == jnl:
                rec["location"] = tgt
        # update the JD entry's source pointer
        ent = JD_DIR / f"{jnl}.md"
        if ent.exists():
            t = ent.read_text()
            t = re.sub(r"^source:.*$", f"source: {tgt}", t, count=1, flags=re.MULTILINE)
            ent.write_text(t)

    if apply:
        REG_PATH.write_text(json.dumps(reg, indent=2) + "\n")
        print("autosort: applied. JNLs preserved; LAL + entries updated. "
              "Re-run seed.py if locations are also pinned in the manifest.")
        return 0
    print("\nRun with --apply to relocate. (CI uses dry-run as a gate.)")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
