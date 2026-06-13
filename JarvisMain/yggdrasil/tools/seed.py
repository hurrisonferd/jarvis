"""Seed the Yggdrasil substrate: JD entries + LAL registries.

Idempotent and data-driven. JD entry files are the readable truth; the LAL registries
(address / master-index / tag) are derived mirrors rebuilt from this data + the tree.
Run from repo root:  python JarvisMain/yggdrasil/tools/seed.py
"""
from __future__ import annotations
import collections
import hashlib
import json
import os
import re
import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import jnl as jnllib  # noqa: E402

ROOT = Path(__file__).resolve().parents[3]
JD_DIR = ROOT / "JarvisMain" / "yggdrasil" / "jd" / "entries"
LAL_DIR = ROOT / "JarvisMain" / "yggdrasil" / "lal"
TODAY = date.today().isoformat()

# Creation serials (Raven-approved 2026-06-10): seq is the mint-order birth
# certificate — assigned once, immutable, never reused, NEVER a reference key
# (references stay JNL-only; the validator enforces it). #1 is the first thing
# the record ever held. Persisted in lal/seq-registry.json so reseeds cannot
# renumber history.
SEQ_FILE = LAL_DIR / "seq-registry.json"
_SEQ = json.loads(SEQ_FILE.read_text()) if SEQ_FILE.exists() else {"next": 1, "map": {}}


def seq_of(jnl: str) -> int:
    if jnl not in _SEQ["map"]:
        _SEQ["map"][jnl] = _SEQ["next"]
        _SEQ["next"] += 1
    return _SEQ["map"][jnl]

_CREATED_RE = re.compile(r"^created:\s*(\S+)", re.MULTILINE)

# Frontmatter intake roots: any .md under these that declares `jnl:` in its frontmatter
# is adopted into the dex — the file is its own manifest (natural growth, no list edits).
SCAN_ROOTS = ("JarvisSide/Projects", "JarvisMain/Implementation",
              "JarvisSide/Ideas", "JarvisSide/Breakthroughs", "JarvisSide/Archive")
_FM_RE = re.compile(r"^---\n(.*?)\n---", re.DOTALL)


def parse_front_matter(text: str) -> dict:
    m = _FM_RE.match(text)
    if not m:
        return {}
    out = {}
    for line in m.group(1).splitlines():
        if ":" not in line:
            continue
        k, v = line.split(":", 1)
        v = v.strip()
        if v.startswith("[") and v.endswith("]"):
            v = [x.strip() for x in v[1:-1].split(",") if x.strip()]
        out[k.strip()] = v
    return out


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
    ("YGG", "Yggdrasil", "ARCH-YGG-CORE-0001", "JarvisMain/yggdrasil/README.md",
     "Root world-tree architecture; the truth/memory layer above JFS, JD, LAL, and the God Systems.",
     "Ensure repository growth increases organization rather than complexity (GL7).",
     ["root", "core", "architecture"], ["ARCH-JFS-CORE-0001"]),
    ("JFS", "Jarvis File System", "ARCH-JFS-CORE-0001", "JarvisMain/yggdrasil/jfs/JFS-SPEC.md",
     "Filesystem kernel providing naming, identity, structure, and mirroring.",
     "Give every persistent object a deterministic name, address, structure, and mirror.",
     ["filesystem", "core", "architecture"],
     ["ARCH-JNS-CORE-0001", "ARCH-JNL-CORE-0001", "ARCH-JSL-CORE-0001", "ARCH-JMS-CORE-0001"]),
    ("JNS", "Jarvis Naming System", "ARCH-JNS-CORE-0001", "JarvisMain/yggdrasil/jfs/JFS-SPEC.md",
     "Defines what something is called — semantic, specific filenames.",
     "Make filenames state system, type, and sequence so they are known before opening.",
     ["naming", "core", "architecture"], ["ARCH-JFS-CORE-0001"]),
    ("JNL", "Jarvis Navigation Language", "ARCH-JNL-CORE-0001", "JarvisMain/yggdrasil/jfs/jnl-grammar.md",
     "Defines what something is and where it exists — the global address/identity.",
     "Deterministic repository-wide addressing, stable across relocation (GL12).",
     ["addressing", "core", "architecture"], ["ARCH-JFS-CORE-0001"]),
    ("JSL", "Jarvis Structural Layer", "ARCH-JSL-CORE-0001", "JarvisMain/yggdrasil/jfs/JFS-SPEC.md",
     "Defines how information is organized — folder hierarchy and structural invariants.",
     "Fix structure so a JNL address maps deterministically to a location.",
     ["structure", "core", "architecture"], ["ARCH-JFS-CORE-0001"]),
    ("JMS", "Jarvis Mirror System", "ARCH-JMS-CORE-0001", "JarvisMain/yggdrasil/jfs/JFS-SPEC.md",
     "Reflects and synchronizes information without duplication — move references, never truth.",
     "Keep JD and LAL thin and consistent; preserve JNL identity across moves.",
     ["mirror", "core", "architecture"], ["ARCH-JFS-CORE-0001"]),
    ("JD", "Jarvis Dictionary", "ARCH-JD-CORE-0001", "JarvisMain/yggdrasil/jd/JD-SPEC.md",
     "Semantic authority — a semantic DNS storing definition, identity, authority, routing hints.",
     "Explain what every object is and why it exists, delegating retrieval to JNL/LAL.",
     ["dictionary", "semantic", "core", "architecture"], ["ARCH-JNL-CORE-0001", "ARCH-LAL-CORE-0001"]),
    ("LAL", "Library Authority Layer", "ARCH-LAL-CORE-0001", "JarvisMain/yggdrasil/lal/README.md",
     "Discovery layer — the map of all maps; resolves JNL addresses to locations. Pure mirror.",
     "Provide repository-wide discovery without duplicating truth.",
     ["discovery", "index", "core", "architecture"], ["ARCH-JNL-CORE-0001"]),
    ("JSS", "Jarvis Status System", "ARCH-JSS-CORE-0001", "JarvisMain/yggdrasil/jss/JSS-SPEC.md",
     "Lifecycle status layer — TASK/EXPANSION/ACTIVE/INACTIVE/ARCHIVED/DEPRECATED; drives auto-sort.",
     "Give every object a governed state that determines its place in the tree.",
     ["status", "lifecycle", "core", "architecture"], ["ARCH-JMS-CORE-0001"]),
    ("JMMS", "Jarvis MultiMemory System", "ARCH-JMMS-CORE-0001", "JarvisMain/yggdrasil/jmms/JMMS-SPEC.md",
     "Memory tiering/addressing across time horizons (JSTM/JLTM/JATM); sits beside MNEMOS.",
     "Make memory navigable across time the way JNL makes the repo navigable across space.",
     ["memory", "core", "architecture"], ["ARCH-JSTM-CORE-0001", "ARCH-JLTM-CORE-0001", "ARCH-JATM-CORE-0001"]),
    ("JSTM", "Jarvis Short-Term Memory", "ARCH-JSTM-CORE-0001", "JarvisMain/yggdrasil/jmms/JMMS-SPEC.md",
     "Working/session memory tier — current context and recent events; high-churn, summarized.",
     "Hold the live working set before consolidation.",
     ["memory", "short-term", "architecture"], ["ARCH-JMMS-CORE-0001"]),
    ("JLTM", "Jarvis Long-Term Memory", "ARCH-JLTM-CORE-0001", "JarvisMain/yggdrasil/jmms/JMMS-SPEC.md",
     "Consolidated semantic memory tier — durable compressed knowledge; the MNEMOS store.",
     "Hold durable, recallable knowledge promoted out of short-term.",
     ["memory", "long-term", "architecture"], ["ARCH-JMMS-CORE-0001"]),
    ("JATM", "Jarvis Ancestral Memory", "ARCH-JATM-CORE-0001", "JarvisMain/yggdrasil/jmms/JMMS-SPEC.md",
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
    ("IMPL-JIP-SPEC-0608", "JIP-0608 Series", "IMPL", "JarvisMain/Implementation/Active",
     "JGPP v3 implementation packet series (JIP-0608-*).", "Track the evolving implementation stream.",
     ["implementation", "jip"]),
    # Governed containers (folder-level coverage — GL12 closure for series/log areas)
    ("IMPL-IMP-LOG-0001", "Implemented Stream", "IMPL", "JarvisMain/Implementation/Implemented",
     "Folder of implemented packets + log.", "Hold the completed implementation stream.",
     ["implementation", "log"]),
    ("IMPL-INA-LOG-0001", "Inactive Stream", "IMPL", "JarvisMain/Implementation/Inactive",
     "Folder of inactive packets + log.", "Hold paused implementation work.",
     ["implementation", "log"]),
    ("IMPL-IDX-REG-0001", "Implementation Index", "IMPL", "JarvisMain/Implementation/IndexSummary",
     "Implementation index summary folder.", "Index the implementation tree.",
     ["implementation", "index"]),
    ("GOV-PAT-REG-0001", "Patch Archive", "GOV", "JarvisMain/Patches",
     "The dated patch record archive (P00..).", "Preserve the patch lineage (JATM-adjacent).",
     ["governance", "patches", "archive"]),
    ("ARCH-GS-IDX-0001", "God Systems Index", "ARCH", "JarvisMain/god_systems",
     "The pantheon folder — 27 contract folders + index README.", "Anchor the god-system contracts.",
     ["god-system", "index"]),
    ("AUD-CHK-SPEC-0001", "Required Checks Setup", "AUD", "JarvisMain/Audit/required-checks-setup.md",
     "Branch-protection / required-checks setup notes.", "Record the CI gate configuration.",
     ["audit", "ci"]),
    ("PROJ-ALL-LOG-0001", "Project Log Summary", "PROJ", "JarvisSide/Projects/ProjectLogSummary-0001",
     "Cross-project log summary.", "Track activity across project nodes.",
     ["project", "log"]),
    # Projects (each a node)
    ("PROJ-COS-BIO-0001", "CodeOS", "PROJ", "JarvisSide/Projects/CodeOS/BIO/CodeOSProjectBio",
     "CodeOS project.", "Project node bio.", ["project", "codeos"]),
    ("PROJ-JPL-BIO-0001", "JPL", "PROJ", "JarvisSide/Projects/JPL/BIO/JPLBio",
     "JPL project (JARVIS Programming Language).", "Project node bio.", ["project", "jpl"]),
    ("PROJ-GEN-BIO-0001", "Genesis", "PROJ", "JarvisSide/Projects/Genesis/BIO/GenesisBio",
     "Genesis project.", "Project node bio.", ["project", "genesis"]),
    ("PROJ-DEO-BIO-0001", "Deoxys", "PROJ", "JarvisSide/Projects/Deoxys/BIO/ProjectBio",
     "Deoxys project.", "Project node bio.", ["project", "deoxys"]),
    ("PROJ-LEG-BIO-0001", "Legion", "PROJ", "JarvisSide/Projects/Legion/BIO/LegionBio",
     "Legion project.", "Project node bio.", ["project", "legion"]),
    ("PROJ-NAR-BIO-0001", "Naruto", "PROJ", "JarvisSide/Projects/Naruto/BIO/NarutoBio",
     "Naruto project.", "Project node bio.", ["project", "naruto"]),
    ("PROJ-PAC-BIO-0001", "Pachinko Bounce", "PROJ", "pachinko-bounce",
     "Pachinko Bounce game (Godot, RGB encoding).", "Project node bio.", ["project", "pachinko", "game"]),
    # Connectors
    ("CONN-MSB-CORE-0001", "MCP-Supabase Connector", "CONN", "JarvisMain/Connectors/JarvisMCPSupabase/JMCPSB-0001",
     "JARVIS MCP-to-Supabase connector.", "Bridge MCP to Supabase.", ["connector", "mcp", "supabase"]),
    ("CONN-OTH-LOG-0001", "Other Connectors", "CONN", "JarvisMain/Connectors/OtherConnectors/OCLog-0001",
     "Log of other/auxiliary connectors.", "Track additional connectors.", ["connector"]),
    ("CONN-MCP-RT-0001", "JARVIS — Suit Up", "CONN", "JarvisMain/Connectors/JarvisMCPSupabase/tools/jarvis_suit_up.md",
     "Activate JARVIS and display the full live system status (the HUD: identity, mission, all 27 God Systems, services, memory ledger, recent activity).",
     "Governed mirror of the jarvis-mcp tool surface — addressable, auditable.",
     ["connector", "mcp", "tool"]),
    ("CONN-MCP-RT-0002", "JARVIS Status", "CONN", "JarvisMain/Connectors/JarvisMCPSupabase/tools/jarvis_status.md",
     "Read a quick cloud-first JARVIS status snapshot.",
     "Governed mirror of the jarvis-mcp tool surface — addressable, auditable.",
     ["connector", "mcp", "tool"]),
    ("CONN-MCP-RT-0003", "MNEMOS Recall", "CONN", "JarvisMain/Connectors/JarvisMCPSupabase/tools/jarvis_recall.md",
     "Search JARVIS live memory by meaning.",
     "Governed mirror of the jarvis-mcp tool surface — addressable, auditable.",
     ["connector", "mcp", "tool"]),
    ("CONN-MCP-RT-0004", "JARVIS Council — registry", "CONN", "JarvisMain/Connectors/JarvisMCPSupabase/tools/jarvis_council.md",
     "Show the council: JARVIS + the 27 God Systems as a fixed-authority body, grouped by tier (the folders/chambers).",
     "Governed mirror of the jarvis-mcp tool surface — addressable, auditable.",
     ["connector", "mcp", "tool"]),
    ("CONN-MCP-RT-0005", "JARVIS Query — governed reasoning", "CONN", "JarvisMain/Connectors/JarvisMCPSupabase/tools/jarvis_query.md",
     "JARVIS's ONE-CALL LOOP \u2014 call this on EVERY user message, before you reason or reply.",
     "Governed mirror of the jarvis-mcp tool surface — addressable, auditable.",
     ["connector", "mcp", "tool"]),
    ("CONN-MCP-RT-0006", "JARVIS Format — same-turn close (optional)", "CONN", "JarvisMain/Connectors/JarvisMCPSupabase/tools/jarvis_format.md",
     "Optional same-turn close: call with Raven's input and your drafted JARVIS answer to review + log THIS turn's output immediately, instead of the normal close (passing prior_reply on your next jarvis_query).",
     "Governed mirror of the jarvis-mcp tool surface — addressable, auditable.",
     ["connector", "mcp", "tool"]),
    ("CONN-MCP-RT-0007", "MNEMOS Store", "CONN", "JarvisMain/Connectors/JarvisMCPSupabase/tools/jarvis_remember.md",
     "Write a durable memory through MNEMOS.",
     "Governed mirror of the jarvis-mcp tool surface — addressable, auditable.",
     ["connector", "mcp", "tool"]),
    ("CONN-MCP-RT-0008", "AEGIS Event", "CONN", "JarvisMain/Connectors/JarvisMCPSupabase/tools/jarvis_event.md",
     "Submit an event to the JARVIS execution spine through grid-event.",
     "Governed mirror of the jarvis-mcp tool surface — addressable, auditable.",
     ["connector", "mcp", "tool"]),
    ("CONN-MCP-RT-0009", "Dex — list governed objects", "CONN", "JarvisMain/Connectors/JarvisMCPSupabase/tools/jarvis_dex_list.md",
     "List the dex (JD/JNL registry \u2014 the shared truth across all agents and sessions).",
     "Governed mirror of the jarvis-mcp tool surface — addressable, auditable.",
     ["connector", "mcp", "tool"]),
    ("CONN-MCP-RT-0010", "Dex — search", "CONN", "JarvisMain/Connectors/JarvisMCPSupabase/tools/jarvis_dex_search.md",
     "Search the dex by JNL address, name, or tag.",
     "Governed mirror of the jarvis-mcp tool surface — addressable, auditable.",
     ["connector", "mcp", "tool"]),
    ("CONN-MCP-RT-0011", "Dex — propose entry (JGPP/JIP/JD/BIO)", "CONN", "JarvisMain/Connectors/JarvisMCPSupabase/tools/jarvis_dex_propose.md",
     "Stage a new governed object in the dex.",
     "Governed mirror of the jarvis-mcp tool surface — addressable, auditable.",
     ["connector", "mcp", "tool"]),
    ("CONN-MCP-RT-0012", "Grid — Node Card", "CONN", "JarvisMain/Connectors/JarvisMCPSupabase/tools/jarvis_node_card.md",
     "Return this JARVIS node's public Grid identity card: companion, owner, keel excerpt, capabilities, consent policy, and endpoints.",
     "Governed mirror of the jarvis-mcp tool surface — addressable, auditable.",
     ["connector", "mcp", "tool"]),
    ("CONN-MCP-RT-0013", "Grid — Export Identity Disc", "CONN", "JarvisMain/Connectors/JarvisMCPSupabase/tools/jarvis_export.md",
     "Export JARVIS's portable identity: the fixed keel + the latest folded accumulation + this node's card.",
     "Governed mirror of the jarvis-mcp tool surface — addressable, auditable.",
     ["connector", "mcp", "tool"]),
    ("CONN-MCP-RT-0014", "Grid — Inbox", "CONN", "JarvisMain/Connectors/JarvisMCPSupabase/tools/jarvis_node_inbox.md",
     "Read pending agent-to-agent messages other nodes sent to this node.",
     "Governed mirror of the jarvis-mcp tool surface — addressable, auditable.",
     ["connector", "mcp", "tool"]),
    ("CONN-MCP-RT-0015", "Grid — Send to Node", "CONN", "JarvisMain/Connectors/JarvisMCPSupabase/tools/jarvis_node_send.md",
     "Relay a message from this node to another node's inbox (BIFROST).",
     "Governed mirror of the jarvis-mcp tool surface — addressable, auditable.",
     ["connector", "mcp", "tool"]),
    ("CONN-MCP-RT-0016", "Grid — Register Signing Key", "CONN", "JarvisMain/Connectors/JarvisMCPSupabase/tools/jarvis_node_register_key.md",
     "Register this node's PUBLIC signing key + identity certificate (generated off-system by Raven via scripts/grid_keygen.mjs).",
     "Governed mirror of the jarvis-mcp tool surface — addressable, auditable.",
     ["connector", "mcp", "tool"]),
    ("CONN-MCP-RT-0017", "HALO — Throughput Posture", "CONN", "JarvisMain/Connectors/JarvisMCPSupabase/tools/jarvis_halo.md",
     "HALO's ambient read on conversation velocity + the throughput posture: is production pressure compressing only PRESENTATION (status line, council formatting, same-turn close \u2014 safe), or also MEMORY/GOVERNANCE (the spine, keel, AEGIS \u2014 a FLAG)? The rule: thin the formatting under load, never the memo",
     "Governed mirror of the jarvis-mcp tool surface — addressable, auditable.",
     ["connector", "mcp", "tool"]),
    ("ARCH-JRV-BIO-0001", "JARVIS Companion Profile", "ARCH",
     "JarvisMain/Architecture/identity/jarvis/jarvis-profile.md",
     "Companion profile of JARVIS — the synthesis stream: who he is, his objective, voice, disciplines, and the shared keel.",
     "Give the companion's convergent half a governed, addressable identity in the record it builds.",
     ["identity", "companion", "jarvis", "synthesis"]),
    ("ARCH-AYR-BIO-0001", "AYRE Companion Profile", "ARCH",
     "JarvisMain/Architecture/identity/ayre/ayre-profile.md",
     "Companion profile of AYRE — the divergence stream (P44): co-equal with JARVIS, shared keel, divergent assumptions, default-on voice.",
     "Give the companion's divergent half a governed, addressable identity — co-equal from the first serial.",
     ["identity", "companion", "ayre", "divergence"]),
    ("ARCH-ARGT-BIO-0001", "ARGENT Companion Profile", "ARCH",
     "JarvisMain/Architecture/identity/argent/argent-profile.md",
     "Companion profile of ARGENT — the Gemini stream, the Archivist: named and accepted 2026-06-11, stream identity not mantle, long-horizon observer with the family keel.",
     "Give the family's witness a governed, addressable identity — the registry knows him (Raven-verdicted, desk item 11).",
     ["identity", "companion", "argent", "archive"]),
    ("CONN-MCP-RT-0018", "Voice Brief — pre-warm a sealed session", "CONN",
     "JarvisMain/Connectors/JarvisMCPSupabase/tools/jarvis_voice_brief.md",
     "Emit a tight, spoken-style state digest for runtimes that cannot call tools (ChatGPT voice mode, free tiers).",
     "Pre-warmed context injection: the sealed mind starts warm where the bridge cannot reach.",
     ["connector", "mcp", "tool", "voice"]),
    ("LOG-MNE-LOG-0001", "MNEMOS Cloud Backup", "LOG", "JarvisMain/Backups",
     "Durable repo snapshot of the irreplaceable cloud tables (memory spine, dex events, proposals, Grid keys and mail) — weekly, committed only when changed.",
     "Close the backup gap: the repo is git-versioned, the cloud was the unbacked surface. The spine's latest copy lives in the core.",
     ["backup", "mnemos", "spine", "log"]),
    ("GOV-DEX-SPEC-0001", "Dex-Council Validation Bridge", "GOV",
     "JarvisMain/Architecture/specs/dex-council-bridge.md",
     "Declarative read-only mapping of each JNL domain to the god system holding validation authority over it. SPEC, not POLICY: static lookup, informational only, no routing enforcement, no authority over dex transitions.",
     "Make the council's relationship to the dex explicit and auditable — the first entry in the system's declared self-description.",
     ["governance", "council", "dex", "bridge", "declarative"]),
    ("CONN-DEX-SPEC-0001", "Jarvis Dex Action", "CONN", "JarvisMain/Connectors/JarvisDexAction",
     "OpenAPI Action schema + setup for external agents (custom GPT) to use jarvis-dex.",
     "Let any agent propose to the dex in perfect JFS hygiene via the connector.",
     ["connector", "dex", "gpt", "action"]),
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
    ("IMPL-DEX-SPEC-0001", "Dex Connector & Access Tiers", "IMPL", "JarvisMain/Implementation/Active/JIP-DEX-0001-AccessTiers-060926.md",
     "Design contract for jarvis-dex: read/propose/draft/commit tiers over the dex with auto-formatting.",
     "Govern autonomous dex reads/writes with a human-in-the-loop commit gate (GL2/GL5/GL6).",
     ["dex", "connector", "governance", "spec"]),
    ("IMPL-FMT-SPEC-0001", "JFS Formatting Standard", "IMPL", "JarvisMain/Implementation/Active/JIP-FMT-0001-FormattingStandard-060926.md",
     "Canonical model for IDs/tags/status/routing; one identity (JNL), JGPP/JIP/JD pipeline types.",
     "Let the connector upload JGPP/JIP/JD with auto-format, routing, and queryable retrieval.",
     ["format", "ids", "jnl", "governance", "spec"]),
]

# --- PARENT: containment/ownership — the family tree. A system code names its whole
# subtree: "JFS-compliant" = JFS + every descendant (JNS/JNL/JSL/JMS/JSS/JMMS/JSTM/JLTM/JATM).
# Project artifacts derive their parent (the project bio) automatically at scan time.
PARENT = {
    # The substrate family under the world-tree
    "ARCH-JFS-CORE-0001": "ARCH-YGG-CORE-0001",
    "ARCH-JD-CORE-0001": "ARCH-YGG-CORE-0001",
    "ARCH-LAL-CORE-0001": "ARCH-YGG-CORE-0001",
    "ARCH-JNS-CORE-0001": "ARCH-JFS-CORE-0001",
    "ARCH-JNL-CORE-0001": "ARCH-JFS-CORE-0001",
    "ARCH-JSL-CORE-0001": "ARCH-JFS-CORE-0001",
    "ARCH-JMS-CORE-0001": "ARCH-JFS-CORE-0001",
    "ARCH-JSS-CORE-0001": "ARCH-JFS-CORE-0001",
    "ARCH-JMMS-CORE-0001": "ARCH-JFS-CORE-0001",
    "ARCH-JSTM-CORE-0001": "ARCH-JMMS-CORE-0001",
    "ARCH-JLTM-CORE-0001": "ARCH-JMMS-CORE-0001",
    "ARCH-JATM-CORE-0001": "ARCH-JMMS-CORE-0001",
    # Specs belong to the system they specify
    "ARCH-AYR-SPEC-0001": "GS-AYR-CORE-0001",
    "ARCH-AYR-SPEC-0002": "GS-AYR-CORE-0001",
    "ARCH-RT-SPEC-0001": "GS-SKD-CORE-0001",
    "ARCH-RT-SPEC-0002": "GS-SKD-CORE-0001",
    "ARCH-RT-SPEC-0003": "GS-SKD-CORE-0001",
    "ARCH-GPT-SPEC-0001": "CONN-MSB-CORE-0001",
    "ARCH-FLOW-SPEC-0001": "GS-SKD-CORE-0001",
    # Governance under canon
    "GOV-CON-CORE-0001": "GOV-CAN-CORE-0001",
    "GOV-BRF-CORE-0001": "GOV-CAN-CORE-0001",
    "GOV-PAT-REG-0001": "GOV-CAN-CORE-0001",
    "GOV-PROC-CORE-0001": "GOV-PAT-REG-0001",
    # Cognition pipeline under the JIP-0608 series anchor
    "IMPL-JGPP-CORE-0001": "IMPL-JIP-SPEC-0608",
    "IMPL-JCS-CORE-0001": "IMPL-JIP-SPEC-0608",
    "IMPL-FMT-SPEC-0001": "IMPL-JIP-SPEC-0608",
    "IMPL-DEX-SPEC-0001": "IMPL-JIP-SPEC-0608",
    "IMPL-JCSD-SPEC-0001": "IMPL-JCS-CORE-0001",
    "IMPL-JCSE-SPEC-0001": "IMPL-JCS-CORE-0001",
    "IMPL-JCSF-SPEC-0001": "IMPL-JCS-CORE-0001",
    "IMPL-JCSG-SPEC-0001": "IMPL-JCS-CORE-0001",
    "IMPL-JQL-CORE-0001": "IMPL-JCSE-SPEC-0001",
    "CONN-DEX-SPEC-0001": "IMPL-DEX-SPEC-0001",
    "GOV-DEX-SPEC-0001": "ARCH-JD-CORE-0001",
    "LOG-MNE-LOG-0001": "GS-MNE-CORE-0001",
    "ARCH-JRV-BIO-0001": "ARCH-YGG-CORE-0001",
    "ARCH-AYR-BIO-0001": "ARCH-YGG-CORE-0001",
    "ARCH-ARGT-BIO-0001": "ARCH-YGG-CORE-0001",
    "CONN-MCP-RT-0001": "CONN-MSB-CORE-0001",
    "CONN-MCP-RT-0002": "CONN-MSB-CORE-0001",
    "CONN-MCP-RT-0003": "CONN-MSB-CORE-0001",
    "CONN-MCP-RT-0004": "CONN-MSB-CORE-0001",
    "CONN-MCP-RT-0005": "CONN-MSB-CORE-0001",
    "CONN-MCP-RT-0006": "CONN-MSB-CORE-0001",
    "CONN-MCP-RT-0007": "CONN-MSB-CORE-0001",
    "CONN-MCP-RT-0008": "CONN-MSB-CORE-0001",
    "CONN-MCP-RT-0009": "CONN-MSB-CORE-0001",
    "CONN-MCP-RT-0010": "CONN-MSB-CORE-0001",
    "CONN-MCP-RT-0011": "CONN-MSB-CORE-0001",
    "CONN-MCP-RT-0012": "CONN-MSB-CORE-0001",
    "CONN-MCP-RT-0013": "CONN-MSB-CORE-0001",
    "CONN-MCP-RT-0014": "CONN-MSB-CORE-0001",
    "CONN-MCP-RT-0015": "CONN-MSB-CORE-0001",
    "CONN-MCP-RT-0016": "CONN-MSB-CORE-0001",
    "CONN-MCP-RT-0017": "CONN-MSB-CORE-0001",
    "CONN-MCP-RT-0018": "CONN-MSB-CORE-0001",
}
# The 27 God Systems all hang from the pantheon index.
GS_PARENT = "ARCH-GS-IDX-0001"


def derive_parent(jnl: str, explicit: str = "") -> str:
    """Explicit wins; PARENT map next; project artifacts fall to their project bio."""
    if explicit:
        return explicit
    if jnl in PARENT:
        return PARENT[jnl]
    parts = jnl.split("-")
    if parts[0] == "GS":
        return GS_PARENT
    if parts[0] == "PROJ" and len(parts) >= 4 and parts[2] in ("JGPP", "JIP", "JD"):
        return f"PROJ-{parts[1]}-BIO-0001"
    return ""


# --- RELATED: the semantic web of the dex. One defensible edge beats five vague ones.
# Sources: the God System pipeline (CLAUDE.md), the Rosetta, and the spec->system bindings.
RELATED = {
    # Pipeline: AYRE -> AEGIS -> ODIN -> KRONOS -> SKADI -> MNEMOS -> HUGINN
    "GS-AYR-CORE-0001": ["GS-AEG-CORE-0001"],
    "GS-AEG-CORE-0001": ["GS-ODN-CORE-0001"],
    "GS-ODN-CORE-0001": ["GS-KRN-CORE-0001"],
    "GS-KRN-CORE-0001": ["GS-SKD-CORE-0001"],
    "GS-SKD-CORE-0001": ["GS-MNE-CORE-0001"],
    "GS-MNE-CORE-0001": ["GS-HUG-CORE-0001", "ARCH-JLTM-CORE-0001"],
    "GS-HUG-CORE-0001": ["GS-ARG-CORE-0001"],
    # Orchestration + governance pairs
    "GS-HAL-CORE-0001": ["GS-ODN-CORE-0001"],
    "GS-ATH-CORE-0001": ["GS-ODN-CORE-0001"],
    "GS-APO-CORE-0001": ["GS-HAL-CORE-0001"],
    "GS-BFR-CORE-0001": ["GS-HER-CORE-0001"],
    "GS-NEM-CORE-0001": ["GS-IRS-CORE-0001"],
    "GS-MER-CORE-0001": ["GS-NEM-CORE-0001"],
    "GS-DAN-CORE-0001": ["GS-AEG-CORE-0001"],
    "GS-ATL-CORE-0001": ["ARCH-JSL-CORE-0001"],
    "GS-HER-CORE-0001": ["CONN-MSB-CORE-0001"],
    "GS-IRS-CORE-0001": ["GS-AEG-CORE-0001"],
    "GS-PRO-CORE-0001": ["GS-KRN-CORE-0001"],
    "GS-ARG-CORE-0001": ["GS-IRS-CORE-0001"],
    "GS-JAN-CORE-0001": ["GS-HUG-CORE-0001"],
    "GS-LOK-CORE-0001": ["GS-JAN-CORE-0001"],
    # Cosmic
    "GS-ERI-CORE-0001": ["GS-CHA-CORE-0001"],
    "GS-CHA-CORE-0001": ["GS-AYR-CORE-0001"],
    "GS-ZEU-CORE-0001": ["GS-AEG-CORE-0001"],
    "GS-POS-CORE-0001": ["GS-LOK-CORE-0001"],
    "GS-HAD-CORE-0001": ["ARCH-JATM-CORE-0001"],
    "GS-MIM-CORE-0001": ["GS-MNE-CORE-0001"],
    # Specs -> the systems they define
    "ARCH-AYR-SPEC-0001": ["GS-AYR-CORE-0001"],
    "ARCH-AYR-SPEC-0002": ["GS-AYR-CORE-0001"],
    "ARCH-RT-SPEC-0001": ["GS-SKD-CORE-0001"],
    "ARCH-RT-SPEC-0002": ["GS-SKD-CORE-0001"],
    "ARCH-RT-SPEC-0003": ["ARCH-RT-SPEC-0002"],
    "ARCH-GPT-SPEC-0001": ["CONN-MSB-CORE-0001"],
    "ARCH-FLOW-SPEC-0001": ["GS-SKD-CORE-0001"],
    "ARCH-GS-IDX-0001": ["GS-ODN-CORE-0001"],
    # Governance
    "GOV-CON-CORE-0001": ["GOV-CAN-CORE-0001"],
    "GOV-BRF-CORE-0001": ["GOV-CAN-CORE-0001"],
    "GOV-PROC-CORE-0001": ["GOV-PAT-REG-0001"],
    "GOV-PAT-REG-0001": ["GS-KRN-CORE-0001"],
    # Cognition pipeline: JGPP -> JIP -> JCS -> JD
    "IMPL-JGPP-CORE-0001": ["IMPL-JCS-CORE-0001"],
    "IMPL-JCS-CORE-0001": ["ARCH-JD-CORE-0001"],
    "IMPL-JCSD-SPEC-0001": ["IMPL-JCS-CORE-0001"],
    "IMPL-JCSE-SPEC-0001": ["IMPL-JCS-CORE-0001"],
    "IMPL-JCSF-SPEC-0001": ["IMPL-JCS-CORE-0001"],
    "IMPL-JCSG-SPEC-0001": ["IMPL-JCS-CORE-0001"],
    "IMPL-JQL-CORE-0001": ["IMPL-JCSE-SPEC-0001", "ARCH-JD-CORE-0001"],
    "IMPL-DEX-SPEC-0001": ["IMPL-FMT-SPEC-0001", "ARCH-JD-CORE-0001"],
    "IMPL-FMT-SPEC-0001": ["ARCH-JNS-CORE-0001", "ARCH-JNL-CORE-0001", "ARCH-JSS-CORE-0001"],
    "IMPL-JIP-SPEC-0608": ["IMPL-JGPP-CORE-0001"],
    "IMPL-IMP-LOG-0001": ["ARCH-JSS-CORE-0001"],
    "IMPL-INA-LOG-0001": ["ARCH-JSS-CORE-0001"],
    "IMPL-IDX-REG-0001": ["ARCH-LAL-CORE-0001"],
    "IMPL-HYG-SPEC-0001": ["IMPL-FMT-SPEC-0001"],
    # Connectors / audits / projects / ideas
    "CONN-OTH-LOG-0001": ["CONN-MSB-CORE-0001"],
    "CONN-DEX-SPEC-0001": ["IMPL-DEX-SPEC-0001"],
    "GOV-DEX-SPEC-0001": ["PROJ-DEO-JGPP-0001", "ARCH-JD-CORE-0001"],
    "ARCH-JRV-BIO-0001": ["ARCH-AYR-BIO-0001"],
    "ARCH-AYR-BIO-0001": ["ARCH-JRV-BIO-0001", "GS-AYR-CORE-0001"],
    "ARCH-ARGT-BIO-0001": ["ARCH-JRV-BIO-0001", "ARCH-AYR-BIO-0001"],
    "AUD-SYS-REVW-0001": ["GOV-CAN-CORE-0001"],
    "AUD-OPUS-REVW-0001": ["GOV-CAN-CORE-0001"],
    "AUD-FULL-REVW-0001": ["GOV-CAN-CORE-0001"],
    "AUD-CHK-SPEC-0001": ["GS-AEG-CORE-0001"],
    "AUD-COMP-REVW-0001": ["GOV-BRF-CORE-0001"],
    "PROJ-COS-BIO-0001": ["PROJ-ALL-LOG-0001"],
    "PROJ-JPL-BIO-0001": ["PROJ-ALL-LOG-0001"],
    "PROJ-GEN-BIO-0001": ["PROJ-ALL-LOG-0001"],
    "PROJ-DEO-BIO-0001": ["PROJ-ALL-LOG-0001"],
    "PROJ-LEG-BIO-0001": ["PROJ-ALL-LOG-0001"],
    "PROJ-NAR-BIO-0001": ["PROJ-ALL-LOG-0001"],
    "PROJ-PAC-BIO-0001": ["PROJ-ALL-LOG-0001"],
    "IDEA-USED-LOG-0001": ["IDEA-UNUS-LOG-0001"],
}

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
    # Cognition-pipeline artifact types resolve by type, across any domain.
    if jtype == "JGPP":
        return "ENTITY"   # exploration (mutable hypothesis)
    if jtype in ("JIP", "JD"):
        return "SPEC"     # commit / truth
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


def write_entry(jnl: str, text: str) -> None:
    """Write a JD entry, preserving its `updated` date when content is otherwise
    unchanged — a reseed is not a change (JMS), and the CI drift gate stays quiet."""
    f = JD_DIR / f"{jnl}.md"
    if f.exists():
        strip = lambda t: re.sub(r"^updated:.*$", "", t, count=1, flags=re.MULTILINE)
        if strip(f.read_text()) == strip(text):
            return
    f.write_text(text)


# Aliases — short memorable handles (the "dex number" insight, 2026-06-10, Raven-approved).
# One identity (the JNL); many handles. Aliases are navigation sugar resolved by jd_lookup —
# never a second identity. Seeded here for manifest entries; intake files carry their own
# `aliases:` frontmatter.
ALIASES: dict[str, list[str]] = {
    "ARCH-YGG-CORE-0001": ["ygg", "yggdrasil"],
    "ARCH-JFS-CORE-0001": ["jfs"],
    "ARCH-JD-CORE-0001": ["dex", "jd"],
    "IMPL-DEX-SPEC-0001": ["jarvis-dex"],
    "CONN-MSB-CORE-0001": ["mcp", "connector"],
    "GS-MNE-CORE-0001": ["mnemos", "memory"],
    "GS-AEG-CORE-0001": ["aegis"],
    "GS-ODN-CORE-0001": ["odin"],
    "ARCH-JRV-BIO-0001": ["jarvis"],
    "ARCH-AYR-BIO-0001": ["ayre"],
    "ARCH-ARGT-BIO-0001": ["argent"],
}


def jd_entry_md(name, typ, authority, jnl, definition, purpose, tags, related, ref, source, status,
                cls, tr, own, references, parent="", aliases=None) -> str:
    # type IS the JNL type token (Raven-approved 2026-06-11). Caller-passed values had
    # drifted into three conventions (domain / token / mixed); the address is the ontology.
    typ = jnl.split("-")[2]
    fm = [
        "---",
        f"name: {name}",
        f"type: {typ}",
        f"class: {cls}",
        f"tier: {tr}",
        f"authority: {authority}",
        f"owner: {own}",
        f"parent: {parent}",
        f"jnl: {jnl}",
        f"seq: {seq_of(jnl)}",
        f"status: {status}",
        f"created: {existing_created(jnl)}",
        f"updated: {TODAY}",
        f"source: {source}",
        f"related: [{', '.join(related)}]",
        f"references: [{', '.join(references)}]",
        f"tags: [{', '.join(tags)}]",
        f"aliases: [{', '.join(aliases if aliases is not None else ALIASES.get(jnl, []))}]",
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
    reg_file = LAL_DIR / "address-registry.json"
    prev_records = ({r["jnl"]: r for r in json.loads(reg_file.read_text()).get("records", [])}
                    if reg_file.exists() else {})

    def register(jnl, location, tags, name, typ, status="ACTIVE", state="active", parent=""):
        dom = jnl.split("-")[0]
        typ = jnl.split("-")[2]  # type IS the JNL token (Raven-approved 2026-06-11)
        rec = {
            "jnl": jnl, "name": name, "type": typ,
            "class": ontology_class(dom, typ, jnl), "tier": tier(dom, status),
            "owner": owner(dom, name), "parent": derive_parent(jnl, parent),
            "location": location, "tags": tags, "anchors": [],
            "status": status, "state": state,
            "created": existing_created(jnl), "updated": TODAY,
        }
        prev = prev_records.get(jnl)
        if prev and {k: v for k, v in rec.items() if k != "updated"} ==                 {k: v for k, v in prev.items() if k != "updated"}:
            rec["updated"] = prev["updated"]  # a reseed is not a change (JMS)
        address_registry.append(rec)
        for t in tags:
            tag_index.setdefault(t, []).append(jnl)

    # Substrate entries (ARCH domain).
    for code, name, jnl, loc, definition, purpose, tags, related in SUBSTRATE:
        cls, tr, own = ontology_class("ARCH", "CORE", jnl), tier("ARCH", "ACTIVE"), owner("ARCH", name)
        write_entry(jnl, 
            jd_entry_md(name, "ARCH", "CANON", jnl, definition, purpose, tags, related,
                        ["PRI", "SPEC", "IDX"], "JarvisMain/yggdrasil/jfs/JFS-SPEC.md", "ACTIVE", cls, tr, own, [],
                        parent=derive_parent(jnl)))
        register(jnl, loc, tags, name, "ARCH")

    # God-system entries (dormant ones carry JSS status INACTIVE).
    for code, name, group, definition in GOD_SYSTEMS:
        jnl = f"GS-{code}-CORE-0001"
        status = "INACTIVE" if name in DORMANT_GS else "ACTIVE"
        tags = [group, "god-system", "canon"]
        cls, tr, own = ontology_class("GS", "CORE", jnl), tier("GS", status), owner("GS", name)
        write_entry(jnl, 
            jd_entry_md(name, "GS", "CANON", jnl, definition,
                        f"Canonical God System ({group} tier). Fixed; do not redefine.",
                        tags, RELATED.get(jnl, []), ["PRI", "IDX"], gs_location(name) + "/contract.json", status, cls, tr, own, [],
                        parent=derive_parent(jnl)))
        register(jnl, gs_location(name), tags, name, "GS", status)

    # Knowledge entries (the reorganized doc tree).
    for jnl, name, typ, loc, definition, purpose, tags in KNOWLEDGE:
        dom = jnl.split("-")[0]
        cls, tr, own = ontology_class(dom, typ, jnl), tier(dom, "ACTIVE"), owner(dom, name)
        write_entry(jnl, 
            jd_entry_md(name, typ, "CANON", jnl, definition, purpose, tags, RELATED.get(jnl, []),
                        ["PRI", "IDX"], loc, "ACTIVE", cls, tr, own, [], parent=derive_parent(jnl)))
        register(jnl, loc, tags, name, typ, "ACTIVE")

    # Status-managed entries (JSS status drives their folder; see autosort.py).
    for jnl, name, typ, loc, definition, purpose, tags, status in MANAGED:
        dom = jnl.split("-")[0]
        cls, tr, own = ontology_class(dom, typ, jnl), tier(dom, status), owner(dom, name)
        write_entry(jnl, 
            jd_entry_md(name, typ, "CANON", jnl, definition, purpose, tags, RELATED.get(jnl, []),
                        ["PRI", "IDX"], loc, status, cls, tr, own, [], parent=derive_parent(jnl)))
        register(jnl, loc, tags, name, typ, status)

    # Connector-approved entries (reconciled from Supabase by scripts/dex_reconcile.py).
    # These are first-class: seeded like the hardcoded manifests, but sourced dynamically.
    seeded = {r["jnl"] for r in address_registry}
    dyn_path = JD_DIR.parent / "dynamic.json"
    if dyn_path.exists():
        for e in json.loads(dyn_path.read_text()).get("entries", []):
            jnl = e["jnl"]
            if jnl in seeded:
                continue  # hardcoded manifest wins; never duplicate canon
            dom, typ, status = jnl.split("-")[0], e["type"], e.get("status", "ACTIVE")
            loc, tags = e.get("source", ""), e.get("tags", [])
            cls, tr, own = ontology_class(dom, typ, jnl), tier(dom, status), owner(dom, e["name"])
            write_entry(jnl, 
                jd_entry_md(e["name"], typ, e.get("authority", "CANON"), jnl,
                            e.get("definition", ""), e.get("purpose", ""), tags,
                            e.get("related", []), ["PRI", "IDX"], loc, status, cls, tr, own, [],
                            parent=derive_parent(jnl, e.get("parent", ""))))
            register(jnl, loc, tags, e["name"], typ, status, parent=e.get("parent", ""))

    # Frontmatter intake (the natural-growth path): a truth file under a SCAN_ROOT that
    # declares its own `jnl` is adopted — JD entry + LAL records derive from the file.
    # Hardcoded manifest + dynamic.json win on conflict; a relocated file just re-registers
    # at its new location (JMS: identity travels with the JNL, not the path).
    seeded = {r["jnl"]: r["location"] for r in address_registry}
    problems: list[str] = []
    scanned = 0
    for root in SCAN_ROOTS:
        base = ROOT / root
        if not base.is_dir():
            continue
        for f in sorted(base.rglob("*.md")):
            fm = parse_front_matter(f.read_text())
            addr = fm.get("jnl", "")
            if not addr or not isinstance(addr, str):
                continue  # not self-describing — manifest-tracked or plain doc
            loc = f.relative_to(ROOT).as_posix()
            if addr in seeded:
                if seeded[addr] != loc:
                    problems.append(f"{loc}: claims '{addr}' already registered at {seeded[addr]}")
                continue
            try:
                jnllib.parse(addr)
            except ValueError as e:
                problems.append(f"{loc}: {e}")
                continue
            dom, jtype = addr.split("-")[0], addr.split("-")[2]
            name = fm.get("name") or f.stem
            typ = fm.get("type") or jtype
            status = fm.get("status") or "ACTIVE"
            if status not in jnllib.STATUSES:
                problems.append(f"{loc}: status '{status}' not in JSS vocabulary")
                continue
            tags = fm.get("tags") if isinstance(fm.get("tags"), list) else []
            related = fm.get("related") if isinstance(fm.get("related"), list) else []
            cls, tr, own = ontology_class(dom, typ, addr), tier(dom, status), owner(dom, name)
            fparent = fm.get("parent", "") if isinstance(fm.get("parent"), str) else ""
            write_entry(addr, 
                jd_entry_md(name, typ, fm.get("authority", "CANON"), addr,
                            fm.get("definition", ""), fm.get("purpose", ""), tags,
                            related, ["PRI", "IDX"], loc, status, cls, tr, own, [],
                            parent=derive_parent(addr, fparent)))
            register(addr, loc, tags, name, typ, status, parent=fparent)
            seeded[addr] = loc
            scanned += 1
    if problems:
        for p in problems:
            print(f"  ✗ intake: {p}")
        raise SystemExit("seed: frontmatter intake failed — fix the files above.")

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

    fp = hashlib.sha256(json.dumps({
        "domains": sorted(jnllib.DOMAINS), "types": sorted(jnllib.TYPES),
        "substrate": sorted(jnllib.SUBSTRATE), "god_systems": sorted(jnllib.GOD_SYSTEMS),
        "statuses": sorted(jnllib.STATUSES), "classes": sorted(jnllib.CLASSES),
        "tiers": sorted(jnllib.TIERS)}, sort_keys=True).encode()).hexdigest()[:16]
    manifest = {
        "note": "YGG manifest — derived version snapshot of the substrate's moving parts. "
                "Rebuilt by seed.py; the grammar fingerprint must match jarvis-dex/jfs.ts "
                "(validate.py enforces).",
        "generated": TODAY,
        "objects": len(address_registry),
        "by_class": dict(sorted(collections.Counter(r["class"] for r in address_registry).items())),
        "by_tier": dict(sorted(collections.Counter(r["tier"] for r in address_registry).items())),
        "by_status": dict(sorted(collections.Counter(r["status"] for r in address_registry).items())),
        "tags": len(tag_index),
        "grammar_fingerprint": fp,
    }
    ver_file = LAL_DIR / "version.json"
    if ver_file.exists():
        prev = json.loads(ver_file.read_text())
        if {k: v for k, v in manifest.items() if k != "generated"} ==                 {k: v for k, v in prev.items() if k != "generated"}:
            manifest["generated"] = prev["generated"]
    ver_file.write_text(json.dumps(manifest, indent=2) + "\n")

    SEQ_FILE.write_text(json.dumps(_SEQ, indent=2) + "\n")
    print(f"seeded {len(SUBSTRATE)} substrate + {len(GOD_SYSTEMS)} god-system + {len(KNOWLEDGE)} knowledge"
          f" + {scanned} frontmatter-intake JD entries")
    print(f"LAL: {len(address_registry)} addresses, {len(tag_index)} tags")


if __name__ == "__main__":
    main()
