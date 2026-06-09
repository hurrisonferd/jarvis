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

# --- Knowledge objects: the reorganized doc tree, each addressed + dated (the growing dex).
# (jnl, name, type, location, definition, purpose, tags) ---
KNOWLEDGE = [
    # Governance / canon
    ("GOV-CAN-CORE-0001", "Canon", "GOV", "Architecture/canon.md",
     "Canonical architecture statement for JARVIS.", "Hold the agreed system truth.",
     ["governance", "canon"]),
    ("GOV-CON-CORE-0001", "Constraints", "GOV", "Architecture/constraints.md",
     "The full GL1–GL9 Gold Law contract.", "Define the hard constraints all agents obey.",
     ["governance", "gold-law"]),
    ("GOV-BRF-CORE-0001", "Jarvis Brief", "GOV", "Architecture/JarvisBrief.md",
     "High-level orientation brief for JARVIS.", "Onboard agents to the mission and system.",
     ["governance", "brief"]),
    ("GOV-PROC-CORE-0001", "Patch Process", "GOV", "Patches/PatchProcess.md",
     "How patches are proposed, numbered, and recorded.", "Govern change flow into the record.",
     ["governance", "patches", "process"]),
    # Architecture specs / runtime contracts
    ("ARCH-RT-SPEC-0001", "Event Contract", "ARCH", "Architecture/runtime/event-contract.md",
     "The runtime event contract.", "Define event shape across the loop.", ["architecture", "runtime"]),
    ("ARCH-RT-SPEC-0002", "Execution Model", "ARCH", "Architecture/runtime/execution-model.md",
     "The runtime execution model.", "Define how execution proceeds.", ["architecture", "runtime"]),
    ("ARCH-RT-SPEC-0003", "World Kernel", "ARCH", "Architecture/runtime/world-kernel.md",
     "The world-kernel runtime spec.", "Define the world runtime substrate.", ["architecture", "runtime"]),
    ("ARCH-AYR-SPEC-0001", "AYRE/JARVIS Split", "ARCH", "Architecture/specs/ayre-jarvis-split-v1.md",
     "Spec for splitting AYRE from JARVIS as co-equal streams.", "Record the split design.",
     ["architecture", "ayre"]),
    ("ARCH-AYR-SPEC-0002", "AYRE Loop", "ARCH", "Architecture/specs/ayre-loop-v1.md",
     "Spec for the AYRE reflection loop.", "Define the reflection cycle.", ["architecture", "ayre"]),
    ("ARCH-GPT-SPEC-0001", "Custom GPT Instructions", "ARCH", "Architecture/specs/jarvis-custom-gpt-instructions.md",
     "Instruction spec for the JARVIS custom GPT.", "Align external GPT behavior.", ["architecture", "gpt"]),
    ("ARCH-FLOW-SPEC-0001", "Throughput Posture", "ARCH", "Architecture/specs/throughput-posture.md",
     "Spec for system throughput posture.", "Set performance/throughput stance.", ["architecture", "throughput"]),
    # Implementation (JIP series anchor)
    ("IMPL-JIP-SPEC-0608", "JIP-0608 Series", "IMPL", "Implementation/Active/JIP-0608-ReadMe",
     "JGPP v3 implementation packet series (JIP-0608-*).", "Track the evolving implementation stream.",
     ["implementation", "jip"]),
    # Projects (each a node)
    ("PROJ-COS-BIO-0001", "CodeOS", "PROJ", "Projects/CodeOSProjectBio",
     "CodeOS project.", "Project node bio.", ["project", "codeos"]),
    ("PROJ-JPL-BIO-0001", "JPL", "PROJ", "Projects/JPL/JPLBio",
     "JPL project (JARVIS Programming Language).", "Project node bio.", ["project", "jpl"]),
    ("PROJ-GEN-BIO-0001", "Genesis", "PROJ", "Projects/Genesis/GenesisBio",
     "Genesis project.", "Project node bio.", ["project", "genesis"]),
    ("PROJ-DEO-BIO-0001", "Deoxys", "PROJ", "Projects/Deoxys/ProjectBio",
     "Deoxys project.", "Project node bio.", ["project", "deoxys"]),
    ("PROJ-LEG-BIO-0001", "Legion", "PROJ", "Projects/Legion/LegionBio",
     "Legion project.", "Project node bio.", ["project", "legion"]),
    ("PROJ-NAR-BIO-0001", "Naruto", "PROJ", "Projects/Naruto/NarutoBio",
     "Naruto project.", "Project node bio.", ["project", "naruto"]),
    ("PROJ-PAC-BIO-0001", "Pachinko Bounce", "PROJ", "pachinko-bounce",
     "Pachinko Bounce game (Godot, RGB encoding).", "Project node bio.", ["project", "pachinko", "game"]),
    # Connectors
    ("CONN-MSB-CORE-0001", "MCP-Supabase Connector", "CONN", "Connectors/JarvisMCPSupabase/JMCPSB-0001",
     "JARVIS MCP-to-Supabase connector.", "Bridge MCP to Supabase.", ["connector", "mcp", "supabase"]),
    ("CONN-OTH-LOG-0001", "Other Connectors", "CONN", "Connectors/OtherConnectors/OCLog-0001",
     "Log of other/auxiliary connectors.", "Track additional connectors.", ["connector"]),
    # Audit reviews
    ("AUD-SYS-REVW-0001", "Jarvis System Review", "AUD", "Audit/JarvisSystemReview-0001-060826",
     "System review (2026-06-08).", "Recorded architecture review.", ["audit", "review"]),
    ("AUD-OPUS-REVW-0001", "Opus 4.8 Audit", "AUD", "Audit/2026-05-29_opus48_audit.md",
     "Opus 4.8 audit (2026-05-29).", "Recorded audit.", ["audit", "review"]),
    ("AUD-FULL-REVW-0001", "Full System Audit", "AUD", "Audit/2026-06-04_full_system_audit.md",
     "Full system audit (2026-06-04).", "Recorded audit.", ["audit", "review"]),
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

    # Knowledge entries (the reorganized doc tree).
    for jnl, name, typ, loc, definition, purpose, tags in KNOWLEDGE:
        (JD_DIR / f"{jnl}.md").write_text(
            jd_entry_md(name, typ, "CANON", jnl, definition, purpose, tags, [],
                        ["PRI", "IDX"], loc))
        register(jnl, loc, tags, name, typ)

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

    print(f"seeded {len(SUBSTRATE)} substrate + {len(GOD_SYSTEMS)} god-system + {len(KNOWLEDGE)} knowledge JD entries")
    print(f"LAL: {len(address_registry)} addresses, {len(tag_index)} tags")


if __name__ == "__main__":
    main()
