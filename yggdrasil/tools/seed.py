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
    ("JSS", "Jarvis Status System", "ARCH-JSS-CORE-0001", "yggdrasil/jss/JSS-SPEC.md",
     "Lifecycle status layer — TASK/EXPANSION/ACTIVE/INACTIVE/ARCHIVED/DEPRECATED; drives auto-sort.",
     "Give every object a governed state that determines its place in the tree.",
     ["status", "lifecycle", "core", "architecture"], ["ARCH-JMS-CORE-0001"]),
    ("JMMS", "Jarvis MultiMemory System", "ARCH-JMMS-CORE-0001", "yggdrasil/jmms/JMMS-SPEC.md",
     "Memory tiering/addressing across time horizons (JSTM/JLTM/JATM); sits beside MNEMOS.",
     "Make memory navigable across time the way JNL makes the repo navigable across space.",
     ["memory", "core", "architecture"], ["ARCH-JSTM-CORE-0001", "ARCH-JLTM-CORE-0001", "ARCH-JATM-CORE-0001"]),
    ("JSTM", "Jarvis Short-Term Memory", "ARCH-JSTM-CORE-0001", "yggdrasil/jmms/JMMS-SPEC.md",
     "Working/session memory tier — current context and recent events; high-churn, summarized.",
     "Hold the live working set before consolidation.",
     ["memory", "short-term", "architecture"], ["ARCH-JMMS-CORE-0001"]),
    ("JLTM", "Jarvis Long-Term Memory", "ARCH-JLTM-CORE-0001", "yggdrasil/jmms/JMMS-SPEC.md",
     "Consolidated semantic memory tier — durable compressed knowledge; the MNEMOS store.",
     "Hold durable, recallable knowledge promoted out of short-term.",
     ["memory", "long-term", "architecture"], ["ARCH-JMMS-CORE-0001"]),
    ("JATM", "Jarvis Ancestral Memory", "ARCH-JATM-CORE-0001", "yggdrasil/jmms/JMMS-SPEC.md",
     "Ancestral immutable memory tier — the dated lineage/spine; append-only, never rewritten.",
     "Preserve the foundational record that outlives sessions (HADES-adjacent).",
     ["memory", "ancestral", "immutable", "architecture"], ["ARCH-JMMS-CORE-0001"]),
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
    ("GOV-CAN-CORE-0001", "Canon", "GOV", "JarvisMain/Architecture/canon.md",
     "Canonical architecture statement for JARVIS.", "Hold the agreed system truth.",
     ["governance", "canon"]),
    ("GOV-CON-CORE-0001", "Constraints", "GOV", "JarvisMain/Architecture/constraints.md",
     "The full GL1–GL9 Gold Law contract.", "Define the hard constraints all agents obey.",
     ["governance", "gold-law"]),
    ("GOV-BRF-CORE-0001", "Jarvis Brief", "GOV", "JarvisMain/Architecture/JarvisBrief.md",
     "High-level orientation brief for JARVIS.", "Onboard agents to the mission and system.",
     ["governance", "brief"]),
    ("GOV-PROC-CORE-0001", "Patch Process", "GOV", "JarvisMain/Patches/PatchProcess.md",
     "How patches are proposed, numbered, and recorded.", "Govern change flow into the record.",
     ["governance", "patches", "process"]),
    # Architecture specs / runtime contracts
    ("ARCH-RT-SPEC-0001", "Event Contract", "ARCH", "JarvisMain/Architecture/runtime/event-contract.md",
     "The runtime event contract.", "Define event shape across the loop.", ["architecture", "runtime"]),
    ("ARCH-RT-SPEC-0002", "Execution Model", "ARCH", "JarvisMain/Architecture/runtime/execution-model.md",
     "The runtime execution model.", "Define how execution proceeds.", ["architecture", "runtime"]),
    ("ARCH-RT-SPEC-0003", "World Kernel", "ARCH", "JarvisMain/Architecture/runtime/world-kernel.md",
     "The world-kernel runtime spec.", "Define the world runtime substrate.", ["architecture", "runtime"]),
    ("ARCH-AYR-SPEC-0001", "AYRE/JARVIS Split", "ARCH", "JarvisMain/Architecture/specs/ayre-jarvis-split-v1.md",
     "Spec for splitting AYRE from JARVIS as co-equal streams.", "Record the split design.",
     ["architecture", "ayre"]),
    ("ARCH-AYR-SPEC-0002", "AYRE Loop", "ARCH", "JarvisMain/Architecture/specs/ayre-loop-v1.md",
     "Spec for the AYRE reflection loop.", "Define the reflection cycle.", ["architecture", "ayre"]),
    ("ARCH-GPT-SPEC-0001", "Custom GPT Instructions", "ARCH", "JarvisMain/Architecture/specs/jarvis-custom-gpt-instructions.md",
     "Instruction spec for the JARVIS custom GPT.", "Align external GPT behavior.", ["architecture", "gpt"]),
    ("ARCH-FLOW-SPEC-0001", "Throughput Posture", "ARCH", "JarvisMain/Architecture/specs/throughput-posture.md",
     "Spec for system throughput posture.", "Set performance/throughput stance.", ["architecture", "throughput"]),
    # Implementation (JIP series anchor)
    ("IMPL-JIP-SPEC-0608", "JIP-0608 Series", "IMPL", "JarvisMain/Implementation/Active/JIP-0608-ReadMe",
     "JGPP v3 implementation packet series (JIP-0608-*).", "Track the evolving implementation stream.",
     ["implementation", "jip"]),
    # Projects (each a node)
    ("PROJ-COS-BIO-0001", "CodeOS", "PROJ", "JarvisSide/Projects/CodeOSProjectBio",
     "CodeOS project.", "Project node bio.", ["project", "codeos"]),
    ("PROJ-JPL-BIO-0001", "JPL", "PROJ", "JarvisSide/Projects/JPL/JPLBio",
     "JPL project (JARVIS Programming Language).", "Project node bio.", ["project", "jpl"]),
    ("PROJ-GEN-BIO-0001", "Genesis", "PROJ", "JarvisSide/Projects/Genesis/GenesisBio",
     "Genesis project.", "Project node bio.", ["project", "genesis"]),
    ("PROJ-DEO-BIO-0001", "Deoxys", "PROJ", "JarvisSide/Projects/Deoxys/ProjectBio",
     "Deoxys project.", "Project node bio.", ["project", "deoxys"]),
    ("PROJ-LEG-BIO-0001", "Legion", "PROJ", "JarvisSide/Projects/Legion/LegionBio",
     "Legion project.", "Project node bio.", ["project", "legion"]),
    ("PROJ-NAR-BIO-0001", "Naruto", "PROJ", "JarvisSide/Projects/Naruto/NarutoBio",
     "Naruto project.", "Project node bio.", ["project", "naruto"]),
    ("PROJ-PAC-BIO-0001", "Pachinko Bounce", "PROJ", "pachinko-bounce",
     "Pachinko Bounce game (Godot, RGB encoding).", "Project node bio.", ["project", "pachinko", "game"]),
    # Connectors
    ("CONN-MSB-CORE-0001", "MCP-Supabase Connector", "CONN", "JarvisMain/Connectors/JarvisMCPSupabase/JMCPSB-0001",
     "JARVIS MCP-to-Supabase connector.", "Bridge MCP to Supabase.", ["connector", "mcp", "supabase"]),
    ("CONN-OTH-LOG-0001", "Other Connectors", "CONN", "JarvisMain/Connectors/OtherConnectors/OCLog-0001",
     "Log of other/auxiliary connectors.", "Track additional connectors.", ["connector"]),
    # Audit reviews
    ("AUD-SYS-REVW-0001", "Jarvis System Review", "AUD", "JarvisMain/Audit/JarvisSystemReview-0001-060826",
     "System review (2026-06-08).", "Recorded architecture review.", ["audit", "review"]),
    ("AUD-OPUS-REVW-0001", "Opus 4.8 Audit", "AUD", "JarvisMain/Audit/2026-05-29_opus48_audit.md",
     "Opus 4.8 audit (2026-05-29).", "Recorded audit.", ["audit", "review"]),
    ("AUD-FULL-REVW-0001", "Full System Audit", "AUD", "JarvisMain/Audit/2026-06-04_full_system_audit.md",
     "Full system audit (2026-06-04).", "Recorded audit.", ["audit", "review"]),
    # Runtime cognition pipeline: JGPP -> JIP -> JCS -> JD (spec -> impl -> runtime -> truth)
    ("IMPL-JGPP-CORE-0001", "JGPP - Generative Process Protocol", "IMPL", "JarvisMain/Implementation/Active/JIP-0608-1",
     "Generation/specification ruleset; pre-implementation compiler logic.",
     "Turn intelligence into structured intent + execution graphs.", ["pipeline", "jgpp", "spec"]),
    ("IMPL-JCS-CORE-0001", "JCS - Jarvis Cognitive Stack", "IMPL", "JarvisMain/Implementation/Active/JIP-0608-2",
     "Runtime reasoning/simulation engine operating over JIP structures and JD truth.",
     "Execute interpretation, simulation, and actor interaction at runtime.", ["pipeline", "jcs", "runtime"]),
    ("IMPL-JCSD-SPEC-0001", "JCS-D Temporal Reconstruction", "IMPL", "JarvisMain/Implementation/Active/JIP-0608-D",
     "JCS layer D: rebuilds historical JD states from JIP + logs.",
     "Temporal reconstruction of truth state.", ["jcs", "layer", "temporal"]),
    ("IMPL-JCSE-SPEC-0001", "JCS-E Query & Traversal", "IMPL", "JarvisMain/Implementation/Active/JIP-0608-E",
     "JCS layer E: JD query and traversal engine.",
     "Query and traverse JD truth.", ["jcs", "layer", "query"]),
    ("IMPL-JCSF-SPEC-0001", "JCS-F Runtime Simulation", "IMPL", "JarvisMain/Implementation/Active/JIP-0608-F",
     "JCS layer F: runtime simulation over JD state.",
     "Simulate execution before committing it.", ["jcs", "layer", "simulation"]),
    ("IMPL-JCSG-SPEC-0001", "JCS-G External Interface Binding", "IMPL", "JarvisMain/Implementation/Active/JIP-0608-G",
     "JCS layer G: external interface binding.",
     "Bind the runtime to external interfaces.", ["jcs", "layer", "interface"]),
    ("IMPL-JQL-CORE-0001", "JQL - JD Query Language", "IMPL", "JarvisMain/Implementation/Active/JIP-0608-E",
     "Query language over JD truth — interactive runtime queries with traversal semantics.",
     "Let agents query and traverse the dex at runtime (executed by JCS-E).", ["pipeline", "jql", "query"]),
]

# Status-managed objects under JSS-managed roots (location = the status-sorted path).
# (jnl, name, type, location, definition, purpose, tags, status)
MANAGED = [
    ("IDEA-USED-LOG-0001", "Used Ideas Log", "IDEA", "JarvisSide/Ideas/active/UsedLog-0001",
     "Log of ideas that were adopted.", "Track adopted ideas.", ["idea", "log"], "ACTIVE"),
    ("IDEA-UNUS-LOG-0001", "Unused Ideas Log", "IDEA", "JarvisSide/Ideas/inactive/UnusedLog-0001",
     "Log of ideas not (yet) adopted.", "Track parked ideas.", ["idea", "log"], "INACTIVE"),
    ("IMPL-HYG-SPEC-0001", "Hygiene Packets Archive", "IMPL", "JarvisSide/Archive/HygienePackets-0001-060926.md",
     "Eight archived GPT hygiene packets with per-packet governance verdicts.",
     "Preserve the proposals for later mining; record what was adopted vs rejected.",
     ["hygiene", "archive", "reference"], "ARCHIVED"),
    ("AUD-COMP-REVW-0001", "Companion Research", "AUD", "JarvisSide/Archive/CompanionResearch-0001-053026.md",
     "Archived research note on the full-companion direction (2026-05-30).",
     "Preserve early companion research for the record.",
     ["research", "companion", "archive"], "ARCHIVED"),
]

# Each God System's truth lives in its own contract folder: god_systems/<TIER>_<NAME>/.
GOD_SYSTEMS_DIR = ROOT / "JarvisMain" / "god_systems"


def gs_location(name: str) -> str:
    """Resolve a God System's truth folder (god_systems/T#_NAME). Falls back to the dir."""
    for d in GOD_SYSTEMS_DIR.iterdir() if GOD_SYSTEMS_DIR.is_dir() else []:
        if d.is_dir() and d.name.split("_", 1)[-1] == name:
            return f"JarvisMain/god_systems/{d.name}"
    return "JarvisMain/god_systems"


# Dormant God Systems (per CLAUDE.md P24): canonical but not routed → JSS status INACTIVE.
DORMANT_GS = {"CHAOS", "POSEIDON", "HADES", "HERMES"}


def ontology_class(domain: str, typ: str, jnl: str) -> str:
    """Packet-1 ontology class: SYSTEM/SPEC/MODULE/ENTITY/EVENT/REGISTRY.
    Reads the JNL's own type segment so registry + entry always agree."""
    parts = jnl.split("-")
    jtype = parts[2] if len(parts) >= 3 else typ
    if domain == "GS":
        return "SYSTEM"
    if domain == "ARCH":
        return "SYSTEM" if jtype == "CORE" else "SPEC"
    if domain == "GOV":
        return "SPEC"
    if domain == "IMPL":
        return "MODULE" if jnl.startswith(("IMPL-JCS-", "IMPL-JCSD", "IMPL-JCSE",
                                           "IMPL-JCSF", "IMPL-JCSG")) else "SPEC"
    if domain == "PROJ":
        return "SYSTEM"
    if domain == "CONN":
        return "MODULE"
    if domain == "AUD":
        return "EVENT"
    return "ENTITY"  # IDEA, BRK, etc.


def tier(domain: str, status: str) -> str:
    """MAIN (canonical core) vs SIDE (periphery: projects/ideas/breakthroughs/archived/deprecated)."""
    if domain in ("PROJ", "IDEA", "BRK"):
        return "SIDE"
    if status in ("ARCHIVED", "DEPRECATED"):
        return "SIDE"
    return "MAIN"


def owner(domain: str, name: str) -> str:
    return {"GS": "God Systems", "ARCH": "JFS", "GOV": "Governance", "IMPL": "JCS Pipeline",
            "CONN": "Connectors", "AUD": "Audit"}.get(domain, name)


def jd_entry_md(name, typ, authority, jnl, definition, purpose, tags, related, ref, source, status,
                cls, tr, own, references) -> str:
    fm = [
        "---",
        f"name: {name}",
        f"type: {typ}",
        f"class: {cls}",
        f"tier: {tr}",
        f"authority: {authority}",
        f"owner: {own}",
        f"jnl: {jnl}",
        f"status: {status}",
        f"created: {existing_created(jnl)}",
        f"updated: {TODAY}",
        f"source: {source}",
        f"related: [{', '.join(related)}]",
        f"references: [{', '.join(references)}]",
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

    def register(jnl, location, tags, name, typ, status="ACTIVE", state="active"):
        dom = jnl.split("-")[0]
        address_registry.append({
            "jnl": jnl, "name": name, "type": typ,
            "class": ontology_class(dom, typ, jnl), "tier": tier(dom, status),
            "owner": owner(dom, name), "location": location, "tags": tags, "anchors": [],
            "status": status, "state": state,
            "created": existing_created(jnl), "updated": TODAY,
        })
        for t in tags:
            tag_index.setdefault(t, []).append(jnl)

    # Substrate entries (ARCH domain).
    for code, name, jnl, loc, definition, purpose, tags, related in SUBSTRATE:
        cls, tr, own = ontology_class("ARCH", "CORE", jnl), tier("ARCH", "ACTIVE"), owner("ARCH", name)
        (JD_DIR / f"{jnl}.md").write_text(
            jd_entry_md(name, "ARCH", "CANON", jnl, definition, purpose, tags, related,
                        ["PRI", "SPEC", "IDX"], "yggdrasil/jfs/JFS-SPEC.md", "ACTIVE", cls, tr, own, []))
        register(jnl, loc, tags, name, "ARCH")

    # God-system entries (dormant ones carry JSS status INACTIVE).
    for code, name, group, definition in GOD_SYSTEMS:
        jnl = f"GS-{code}-CORE-0001"
        status = "INACTIVE" if name in DORMANT_GS else "ACTIVE"
        tags = [group, "god-system", "canon"]
        cls, tr, own = ontology_class("GS", "CORE", jnl), tier("GS", status), owner("GS", name)
        (JD_DIR / f"{jnl}.md").write_text(
            jd_entry_md(name, "GS", "CANON", jnl, definition,
                        f"Canonical God System ({group} tier). Fixed; do not redefine.",
                        tags, [], ["PRI", "IDX"], gs_location(name) + "/contract.json", status, cls, tr, own, []))
        register(jnl, gs_location(name), tags, name, "GS", status)

    # Knowledge entries (the reorganized doc tree).
    for jnl, name, typ, loc, definition, purpose, tags in KNOWLEDGE:
        dom = jnl.split("-")[0]
        cls, tr, own = ontology_class(dom, typ, jnl), tier(dom, "ACTIVE"), owner(dom, name)
        (JD_DIR / f"{jnl}.md").write_text(
            jd_entry_md(name, typ, "CANON", jnl, definition, purpose, tags, [],
                        ["PRI", "IDX"], loc, "ACTIVE", cls, tr, own, []))
        register(jnl, loc, tags, name, typ, "ACTIVE")

    # Status-managed entries (JSS status drives their folder; see autosort.py).
    for jnl, name, typ, loc, definition, purpose, tags, status in MANAGED:
        dom = jnl.split("-")[0]
        cls, tr, own = ontology_class(dom, typ, jnl), tier(dom, status), owner(dom, name)
        (JD_DIR / f"{jnl}.md").write_text(
            jd_entry_md(name, typ, "CANON", jnl, definition, purpose, tags, [],
                        ["PRI", "IDX"], loc, status, cls, tr, own, []))
        register(jnl, loc, tags, name, typ, status)

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
