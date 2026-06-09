"""Seed the Yggdrasil substrate: JD entries + LAL registries.

Idempotent and data-driven. JD entry files are the readable truth; the LAL registries
(address / master-index / tag) are derived mirrors rebuilt from this data + the tree.
Run from repo root:  python yggdrasil/tools/seed.py
"""
from __future__ import annotations
import json
import os
import re
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
JD_DIR = ROOT / "yggdrasil" / "jd" / "entries"
LAL_DIR = ROOT / "yggdrasil" / "lal"
TODAY = date.today().isoformat()

_CREATED_RE = re.compile(r"^created:\s*(\S+)", re.MULTILINE)


def existing_created(jnl: str) -> str:
    """Preserve an entry's original created date across re-seeds; mint today if new."""
    f = JD_DIR / f"{jnl}.md"
    if f.exists():
        m = _CREATED_RE.search(f.read_text())
        if m:
            return m.group(1)
    return TODAY

# --- Substrate entries (ARCH). location = where truth actually lives. ---
SUBSTRATE = [
    ("YGG", "Yggdrasil", "ARCH-YGG-CORE-0001", "yggdrasil/README.md",
     "Root world-tree architecture; the truth/memory layer above JFS, JD, LAL, and the God Systems.",
     "Ensure repository growth increases organization rather than complexity (GL7).",
     ["root", "core", "architecture"], []),
    ("JFS", "Jarvis File System", "ARCH-JFS-CORE-0001", "yggdrasil/jfs/JFS-SPEC.md",
     "Filesystem kernel providing naming, identity, structure, and mirroring.",
     "Give every persistent object a deterministic name, address, structure, and mirror.",
     ["filesystem", "core", "architecture"],
     ["ARCH-JNS-CORE-0001", "ARCH-JNL-CORE-0001", "ARCH-JSL-CORE-0001", "ARCH-JMS-CORE-0001"]),
    ("JNS", "Jarvis Naming System", "ARCH-JNS-CORE-0001", "yggdrasil/jfs/JFS-SPEC.md",
     "Defines what something is called — semantic, specific filenames.",
     "Make filenames state system, type, and sequence so they are known before opening.",
     ["naming", "core", "architecture"], ["ARCH-JFS-CORE-0001"]),
    ("JNL", "Jarvis Navigation Language", "ARCH-JNL-CORE-0001", "yggdrasil/jfs/jnl-grammar.md",
     "Defines what something is and where it exists — the global address/identity.",
     "Deterministic repository-wide addressing, stable across relocation (GL12).",
     ["addressing", "core", "architecture"], ["ARCH-JFS-CORE-0001"]),
    ("JSL", "Jarvis Structural Layer", "ARCH-JSL-CORE-0001", "yggdrasil/jfs/JFS-SPEC.md",
     "Defines how information is organized — folder hierarchy and structural invariants.",
     "Fix structure so a JNL address maps deterministically to a location.",
     ["structure", "core", "architecture"], ["ARCH-JFS-CORE-0001"]),
    ("JMS", "Jarvis Mirror System", "ARCH-JMS-CORE-0001", "yggdrasil/jfs/JFS-SPEC.md",
     "Reflects and synchronizes information without duplication — move references, never truth.",
     "Keep JD and LAL thin and consistent; preserve JNL identity across moves.",
     ["mirror", "core", "architecture"], ["ARCH-JFS-CORE-0001"]),
    ("JD", "Jarvis Dictionary", "ARCH-JD-CORE-0001", "yggdrasil/jd/JD-SPEC.md",
     "Semantic authority — a semantic DNS storing definition, identity, authority, routing hints.",
     "Explain what every object is and why it exists, delegating retrieval to JNL/LAL.",
     ["dictionary", "semantic", "core", "architecture"], ["ARCH-JNL-CORE-0001", "ARCH-LAL-CORE-0001"]),
    ("LAL", "Library Authority Layer", "ARCH-LAL-CORE-0001", "yggdrasil/lal/README.md",
     "Discovery layer — the map of all maps; resolves JNL addresses to locations. Pure mirror.",
     "Provide repository-wide discovery without duplicating truth.",
     ["discovery", "index", "core", "architecture"], ["ARCH-JNL-CORE-0001"]),
]

# --- The 27 God Systems (GS). (code, name, tier_group, definition) ---
GOD_SYSTEMS = [
    ("AYR", "AYRE", "core", "Intake / reflection stream; normalizes inbound payloads into events."),
    ("AEG", "AEGIS", "core", "Permission + safety gating; validates before execution (GL6)."),
    ("ODN", "ODIN", "core", "Intent routing + classification; single routing plane."),
    ("KRN", "KRONOS", "core", "Temporal sequencing + patch governance; deterministic ordering."),
    ("SKD", "SKADI", "core", "Execution runtime; the single write/dispatch gateway."),
    ("MNE", "MNEMOS", "core", "Semantic memory; the meaning layer."),
    ("HUG", "HUGINN", "core", "Retrieval + observability + reconciliation; truth reconciliation."),
    ("CHA", "CHAOS", "core", "Entropy + system drift generator / seed-state controller."),
    ("BFR", "BIFROST", "orchestration", "Node + cross-system communication bridge."),
    ("HAL", "HALO", "orchestration", "Conversational intent router; default entry intelligence."),
    ("ATH", "ATHENA", "orchestration", "Planning + decomposition engine."),
    ("NEM", "NEMESIS", "orchestration", "Audit + consistency enforcement."),
    ("APO", "APOLLO", "orchestration", "Rendering + output shaping layer."),
    ("LOK", "LOKI", "governance", "Rollback + mutation control."),
    ("MER", "MERIDIAN", "governance", "Cross-system alignment + normalization."),
    ("DAN", "DANTE", "governance", "Constraint enforcement + edge-case containment."),
    ("ATL", "ATLAS", "governance", "Infrastructure + system topology map."),
    ("HER", "HERMES", "governance", "Translation + protocol conversion (MCP <-> external)."),
    ("IRS", "IRIS", "governance", "Integrity verification + anomaly detection."),
    ("PRO", "PROMETHEUS", "governance", "Decision ledger + foresight logging."),
    ("ARG", "ARGUS", "governance", "Monitoring + continuous surveillance layer."),
    ("JAN", "JANUS", "governance", "Dual-state comparison; before/after, fork detection (GL5 aid)."),
    ("ERI", "ERIS", "cosmic", "Entropy balancing + unpredictability shaping (simulation)."),
    ("ZEU", "ZEUS", "cosmic", "Emergency override + system-wide halt authority."),
    ("POS", "POSEIDON", "cosmic", "Lossless state preservation + recovery snapshots."),
    ("HAD", "HADES", "cosmic", "Immutable event spine + chronological truth layer."),
    ("MIM", "MIMIR", "cosmic", "Deep recall + compressed wisdom extraction."),
]

# Each God System's truth lives in its own contract folder: god_systems/<TIER>_<NAME>/.
GOD_SYSTEMS_DIR = ROOT / "god_systems"


def gs_location(name: str) -> str:
    """Resolve a God System's truth folder (god_systems/T#_NAME). Falls back to the dir."""
    for d in GOD_SYSTEMS_DIR.iterdir() if GOD_SYSTEMS_DIR.is_dir() else []:
        if d.is_dir() and d.name.split("_", 1)[-1] == name:
            return f"god_systems/{d.name}"
    return "god_systems"


def jd_entry_md(name, typ, authority, jnl, definition, purpose, tags, related, ref, source) -> str:
    fm = [
        "---",
        f"name: {name}",
        f"type: {typ}",
        f"authority: {authority}",
        f"jnl: {jnl}",
        f"created: {existing_created(jnl)}",
        f"updated: {TODAY}",
        f"source: {source}",
        f"related: [{', '.join(related)}]",
        f"tags: [{', '.join(tags)}]",
        f"ref: [{', '.join(ref)}]",
        "---",
        "",
        f"**Definition:** {definition}",
        "",
        f"**Purpose:** {purpose}",
        "",
    ]
    return "\n".join(fm)


def main() -> None:
    JD_DIR.mkdir(parents=True, exist_ok=True)
    address_registry = []
    tag_index: dict[str, list[str]] = {}

    def register(jnl, location, tags, name, typ, state="active"):
        address_registry.append({
            "jnl": jnl, "name": name, "type": typ, "location": location,
            "tags": tags, "anchors": [], "state": state,
            "created": existing_created(jnl), "updated": TODAY,
        })
        for t in tags:
            tag_index.setdefault(t, []).append(jnl)

    # Substrate entries.
    for code, name, jnl, loc, definition, purpose, tags, related in SUBSTRATE:
        (JD_DIR / f"{jnl}.md").write_text(
            jd_entry_md(name, "ARCH", "CANON", jnl, definition, purpose, tags, related,
                        ["PRI", "SPEC", "IDX"], "yggdrasil/jfs/JFS-SPEC.md"))
        register(jnl, loc, tags, name, "ARCH")

    # God-system entries.
    for code, name, group, definition in GOD_SYSTEMS:
        jnl = f"GS-{code}-CORE-0001"
        tags = [group, "god-system", "canon"]
        (JD_DIR / f"{jnl}.md").write_text(
            jd_entry_md(name, "GS", "CANON", jnl, definition,
                        f"Canonical God System ({group} tier). Fixed; do not redefine.",
                        tags, [], ["PRI", "IDX"], gs_location(name) + "/contract.json"))
        register(jnl, gs_location(name), tags, name, "GS")

    address_registry.sort(key=lambda r: r["jnl"])
    (LAL_DIR / "address-registry.json").write_text(json.dumps(
        {"note": "Derived mirror — rebuilt by tools/seed.py. JNL -> location. Truth lives at location.",
         "count": len(address_registry), "records": address_registry}, indent=2) + "\n")

    master = [{"object": r["name"], "jnl": r["jnl"], "location": r["location"],
               "tags": r["tags"], "anchors": r["anchors"], "state": r["state"]}
              for r in address_registry]
    (LAL_DIR / "master-index.json").write_text(json.dumps(
        {"note": "MasterIndexSummary — repository-wide routing mirror. Derived; do not hand-edit.",
         "count": len(master), "index": master}, indent=2) + "\n")

    (LAL_DIR / "tag-registry.json").write_text(json.dumps(
        {"note": "Canonical tag vocabulary -> addresses carrying each tag. Derived.",
         "tags": {t: sorted(v) for t, v in sorted(tag_index.items())}}, indent=2) + "\n")

    print(f"seeded {len(SUBSTRATE)} substrate + {len(GOD_SYSTEMS)} god-system JD entries")
    print(f"LAL: {len(address_registry)} addresses, {len(tag_index)} tags")


if __name__ == "__main__":
    main()
