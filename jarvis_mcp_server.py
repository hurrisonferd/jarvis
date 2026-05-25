"""
JARVIS MCP Server v1.0
Exposes JARVIS God Systems as tools to Continue.dev, VS Code, and any MCP client.
Runs locally on port 7777.
"""

import json
import uuid
import hashlib
import asyncio
import os
import shutil
import subprocess
import re
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse, JSONResponse, HTMLResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

BASE_DIR        = Path(__file__).parent
CHAOS_PATH      = BASE_DIR / "chaos" / "chaos_seed.json"
INTAKE_RECYCLE  = BASE_DIR / "intake" / "recycle"

GRID_CANON = [
    {
        "file": "the-grid-mythic-design-bible.md",
        "region": "The Neon Frontier",
        "district": "Grid Design Bible",
        "keywords": ["grid", "mythic", "tron", "dante", "oda", "design", "bible", "vision", "regions", "navigation", "navigation grammar", "interface"],
        "nearby_paths": [
            "the-grid-future-plan.md — Grid timeline and build order",
            "the-grid-advanced-substrates.md — Research substrate map",
            "jarvis-governed-workflow.md — How governed intake works",
        ],
        "warnings": [
            "The Grid is not yet the main build. Current priority: Pachinko Bounce + JARVIS stability.",
            "Gold Law #7: No expansion without simplification. Every new region must earn its place.",
        ],
        "suggested_ascent": "Keep feeding JARVIS clean memory and decisions. The Grid's terrain is built now.",
    },
    {
        "file": "the-grid-future-plan.md",
        "region": "The Neon Frontier",
        "district": "Grid Future Plan",
        "keywords": ["grid", "future", "plan", "timeline", "build order", "phase", "gbrain", "godot", "ar", "vr", "spatial", "virgil", "honest"],
        "nearby_paths": [
            "the-grid-mythic-design-bible.md — Full design vision",
            "the-grid-advanced-substrates.md — Advanced substrate research",
            "jarvis-governed-workflow.md — Current active workflow",
        ],
        "warnings": [
            "Build after: Pachinko Bounce ships, Supabase stable, JARVIS mature.",
            "Personal Grid data layer is buildable now — full spatial interface is 5-10 years out.",
        ],
        "suggested_ascent": "Focus on Phase 1: jarvis_grid text navigation. The map is already here.",
    },
    {
        "file": "the-grid-advanced-substrates.md",
        "region": "The Neon Frontier",
        "district": "Advanced Substrates",
        "keywords": ["substrate", "advanced", "causal", "vector field", "topology", "fractal", "quantum", "hypergraph", "4d", "lattice", "continuous field", "spatial graph"],
        "nearby_paths": [
            "the-grid-future-plan.md — Practical build order",
            "the-grid-mythic-design-bible.md — Where substrates fit the vision",
        ],
        "warnings": [
            "Every substrate must answer: what does this make easier to navigate, remember, predict, simplify, or govern?",
            "Gold Law #7 applies. If it only sounds impressive, ERIS rejects it.",
        ],
        "suggested_ascent": "Spatial graph first. Build causal edges next. Everything else is later.",
    },
    {
        "file": "codex-jarvis-agent-brief.md",
        "region": "The Law Chamber",
        "district": "Codex Authority / Kang",
        "keywords": ["codex", "kang", "agent", "brief", "gpt", "production", "platform", "execution", "authority"],
        "nearby_paths": [
            "jarvis-governed-workflow.md — How Codex fits the governed pipeline",
            "jarvis-stats-triggers.md — What Codex should track",
            "live-mesh-heartbeat.md — Observe-only watcher Codex runs",
        ],
        "warnings": [
            "Do not confuse execution authority with final authority.",
            "Raven remains the deciding layer. Codex executes — it does not govern.",
        ],
        "suggested_ascent": "Log significant implementation decisions through PROMETHEUS before sealing.",
    },
    {
        "file": "jarvis-governed-workflow.md",
        "region": "The Routing Gate",
        "district": "Governed Workflow",
        "keywords": ["workflow", "governed", "intake", "review", "pipeline", "route", "promotion", "gold law", "aegis"],
        "nearby_paths": [
            "codex-jarvis-agent-brief.md — Who executes in this workflow",
            "jarvis-stats-triggers.md — Event-driven tracking in the workflow",
            "live-mesh-heartbeat.md — Passive observation layer",
        ],
        "warnings": [
            "All intake promoted into code, memory, migrations, or automation must follow the governed workflow.",
            "No silent state mutation. Every promotion requires review against Gold Law.",
        ],
        "suggested_ascent": "Before acting on intake, route it through AEGIS. Log the decision to PROMETHEUS.",
    },
    {
        "file": "jarvis-stats-triggers.md",
        "region": "The Signal Spire",
        "district": "Stats and Event Triggers",
        "keywords": ["stats", "triggers", "supabase", "events", "metrics", "tracking", "god system", "session", "event-driven"],
        "nearby_paths": [
            "jarvis-governed-workflow.md — What events to track",
            "live-mesh-heartbeat.md — Passive observation alongside stats",
            "codex-jarvis-agent-brief.md — Who fires the events",
        ],
        "warnings": [
            "Stats are observation, not control. Do not let metrics drive decisions without PROMETHEUS rationale.",
        ],
        "suggested_ascent": "Verify Supabase triggers are firing correctly before relying on stats in decisions.",
    },
    {
        "file": "live-mesh-heartbeat.md",
        "region": "The Signal Spire",
        "district": "Live Mesh Heartbeat",
        "keywords": ["heartbeat", "watcher", "observe", "mesh", "live", "monitor", "passive", "file watch", "watch"],
        "nearby_paths": [
            "jarvis-stats-triggers.md — Active event tracking alongside passive watch",
            "jarvis-governed-workflow.md — When observation triggers review",
            "codex-jarvis-agent-brief.md — Who runs the watcher",
        ],
        "warnings": [
            "Observe-only. The heartbeat watcher must not mutate state.",
            "Gold Law: no_silent_state_mutation. Observation is not permission to act.",
        ],
        "suggested_ascent": "Use heartbeat signals as prompts to review — never as triggers for automatic action.",
    },
]


# ── Grid image aesthetics ─────────────────────────────────────────────────
GRID_REGION_MOODS = {
    "The Neon Frontier": (
        "vast digital frontier, experimental geometry on the horizon, "
        "speculative neon structures, sense of endless possibility, pre-dawn light"
    ),
    "The Law Chamber": (
        "monolithic obsidian chamber, golden constraint seals on the walls, "
        "weight of governance, towering columns of authority, cold austere light"
    ),
    "The Routing Gate": (
        "branching gateway arch, luminous path network radiating outward, "
        "wayfinding node clusters, data flow channels, convergence point architecture"
    ),
    "The Signal Spire": (
        "tall signal tower, red and amber warning beams, entropy meter rings, "
        "alignment field visualization, alert indicators suspended in the void"
    ),
    "The Archive Sea": (
        "endless digital ocean, memory nodes floating like islands, "
        "deep retrieval currents, ancient data preserved in amber light"
    ),
    "The Forge": (
        "industrial build chamber, active construction arcs, "
        "scaffolding of code made visible, artifact crystallization in progress"
    ),
    "The Mirror District": (
        "two reflective planes facing each other, diff visualization streams, "
        "reconciliation bridges, past and present resolving into alignment"
    ),
    "The Rationale Hall": (
        "hall of recorded decisions, floating decision tablets in ordered rows, "
        "causal chain architecture, why-light connecting cause to effect"
    ),
}

TRON_BASE_STYLE = (
    "Tron Legacy aesthetic, digital landscape, pure black void background, "
    "luminous cyan and electric blue neon circuit paths, perfect geometric precision, "
    "glowing identity disc motifs, light trail streaks, "
    "no people, no text, dramatic cinematic lighting, concept art, 8K ultra-detailed"
)

TRON_NEGATIVE = (
    "people, human figures, faces, photorealistic skin, organic shapes, "
    "warm earthy tones, clutter, text overlays, logos, watermark, "
    "low quality, blurry, cartoon, anime"
)


def load_env_file(path: Path = BASE_DIR / ".env") -> None:
    if not path.exists():
        return
    for raw_line in path.read_text(encoding="utf-8-sig").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


load_env_file()

# ── Supabase config ───────────────────────────────────────────────────────
SUPABASE_URL = os.environ.get("SUPABASE_URL", "").rstrip("/")
SUPABASE_KEY = (
    os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
    or os.environ.get("SUPABASE_KEY")
    or os.environ.get("SUPABASE_ANON_KEY")
    or ""
)

# ── Neo4j config ──────────────────────────────────────────────────────────
NEO4J_URI  = os.environ.get("NEO4J_URI",      "bolt://localhost:7687")
NEO4J_USER = os.environ.get("NEO4J_USER",     "neo4j")
NEO4J_PASS = os.environ.get("NEO4J_PASSWORD", "")

def supabase_enabled() -> bool:
    return bool(SUPABASE_URL and SUPABASE_KEY)

def supabase_insert(table: str, data: dict) -> dict:
    if not supabase_enabled():
        return {"ok": False, "status": None, "error": "Supabase credentials not configured"}
    try:
        req = urllib.request.Request(
            f"{SUPABASE_URL}/rest/v1/{table}",
            data=json.dumps(data).encode(),
            headers={
                "Content-Type": "application/json",
                "apikey": SUPABASE_KEY,
                "Authorization": f"Bearer {SUPABASE_KEY}",
                "Prefer": "return=minimal"
            },
            method="POST"
        )
        with urllib.request.urlopen(req, timeout=5) as r:
            return {"ok": r.status in (200, 201), "status": r.status, "error": None}
    except urllib.error.HTTPError as e:
        return {"ok": False, "status": e.code, "error": e.read().decode(errors="replace")}
    except Exception as e:
        return {"ok": False, "status": None, "error": str(e)}

def supabase_select(table: str, limit: int = 10, order: str = "created_at") -> list:
    if not SUPABASE_URL or not SUPABASE_KEY:
        return []
    try:
        req = urllib.request.Request(
            f"{SUPABASE_URL}/rest/v1/{table}?limit={limit}&order={order}.desc",
            headers={
                "apikey": SUPABASE_KEY,
                "Authorization": f"Bearer {SUPABASE_KEY}"
            }
        )
        with urllib.request.urlopen(req, timeout=5) as r:
            return json.loads(r.read().decode())
    except Exception:
        return []

DEFAULT_STATS = {
    "JARVIS": {"sessions_sealed": 0, "decisions_logged": 0, "entropy_current": 0.0, "entropy_trend": "stable", "gold_law_violations": 0, "platforms_active": 0, "days_since_start": 0, "build_vs_theory_ratio": 0.0, "build_sessions": 0, "theory_sessions": 0, "platforms_seen": []},
    "ERIS": {"entropy_signals_sent": 0, "mission_alignment_score": 1.0, "last_signal_reason": None, "gold_law_checks": 0, "drift_events_caught": 0},
    "AEGIS": {"constraints_enforced": 0, "vetoes_issued": 0, "gold_law_violations_blocked": 0, "pass_rate": 1.0, "last_veto_reason": None},
    "ODIN": {"routing_decisions": 0, "routes_to_skadi": 0, "routes_to_mnemos": 0, "failed_routes": 0, "avg_route_depth": 0.0},
    "SKADI": {"tasks_executed": 0, "tasks_completed": 0, "tasks_failed": 0, "completion_rate": 1.0, "last_task_type": None},
    "MNEMOS": {"sessions_stored": 0, "vector_count": 0, "retrieval_count": 0, "avg_drift_score": 0.0, "oldest_memory_days": 0},
    "PROMETHEUS": {"decisions_logged": 0, "systems_most_affected": [], "avg_eris_weight": 0.0, "pending_raven_approval": 0, "last_decision_system": None},
    "JANUS": {"proposals_generated": 0, "proposals_accepted": 0, "proposals_rejected": 0, "acceptance_rate": 0.0, "last_proposal_topic": None},
    "HUGINN": {"diffs_computed": 0, "drift_detected_count": 0, "avg_drift_score": 0.0, "cross_platform_syncs": 0, "last_sync_platform": None},
    "HALO": {"structure_checks": 0, "violations_found": 0, "clean_rate": 1.0, "last_violation_type": None, "iris_flags_received": 0},
    "MIMIR": {"semantic_checks": 0, "contradictions_found": 0, "consistency_score": 1.0, "last_check_system": None, "false_positives": 0},
    "NEMESIS": {"overlap_checks": 0, "warnings_issued": 0, "conflicts_found": 0, "highest_overlap_pair": None, "highest_overlap_score": 0.0},
    "LOKI": {"rollbacks_executed": 0, "rollback_success_rate": 1.0, "deepest_rollback_depth": 0, "last_rollback_reason": None, "tidal_marks_used": 0},
    "DANTE": {"interpretations": 0, "philosophy_queries": 0, "frames_applied": 0, "havenos_queries": 0, "last_frame_type": None},
    "ATLAS": {"uptime_sessions": 0, "substrate_failures": 0, "avg_response_ms": 0.0, "ollama_calls": 0, "last_model_used": None},
}


def default_stats_for(system_id: str) -> dict:
    return dict(DEFAULT_STATS.get(system_id.upper(), {}))


def stats_columns(stats: dict) -> dict:
    numeric_items = [
        (key, value)
        for key, value in stats.items()
        if isinstance(value, (int, float)) and not isinstance(value, bool)
    ][:5]
    payload = {"stats_json": stats}
    for index, (key, value) in enumerate(numeric_items):
        letter = chr(ord("a") + index)
        payload[f"stat_{letter}_key"] = key
        payload[f"stat_{letter}_val"] = value
    return payload


def supabase_get_stats(system_id: str) -> dict | None:
    if not supabase_enabled():
        return None
    try:
        encoded = urllib.parse.quote(system_id.upper(), safe="")
        req = urllib.request.Request(
            f"{SUPABASE_URL}/rest/v1/god_system_stats?system_id=eq.{encoded}&select=stats_json,session_touches&limit=1",
            headers={"apikey": SUPABASE_KEY, "Authorization": f"Bearer {SUPABASE_KEY}"}
        )
        with urllib.request.urlopen(req, timeout=5) as r:
            rows = json.loads(r.read().decode())
        return rows[0] if rows else None
    except Exception:
        return None


def supabase_upsert_stats(system_id: str, stats: dict, touches: int = 0) -> dict:
    if not supabase_enabled():
        return {"ok": False, "status": None, "error": "Supabase credentials not configured"}
    current = supabase_get_stats(system_id) or {}
    session_touches = int(current.get("session_touches") or 0) + touches
    payload = {
        "system_id": system_id.upper(),
        "session_touches": session_touches,
        "last_updated": now(),
        **stats_columns(stats),
    }
    try:
        req = urllib.request.Request(
            f"{SUPABASE_URL}/rest/v1/god_system_stats?on_conflict=system_id",
            data=json.dumps(payload).encode(),
            headers={
                "Content-Type": "application/json",
                "apikey": SUPABASE_KEY,
                "Authorization": f"Bearer {SUPABASE_KEY}",
                "Prefer": "resolution=merge-duplicates,return=minimal"
            },
            method="POST"
        )
        with urllib.request.urlopen(req, timeout=5) as r:
            return {"ok": r.status in (200, 201, 204), "status": r.status, "error": None}
    except urllib.error.HTTPError as e:
        return {"ok": False, "status": e.code, "error": e.read().decode(errors="replace")}
    except Exception as e:
        return {"ok": False, "status": None, "error": str(e)}


def update_system_stats(system_id: str, update_fn, touches: int = 0) -> dict:
    system_id = system_id.upper()
    current = supabase_get_stats(system_id) or {}
    stats = default_stats_for(system_id)
    stats.update(current.get("stats_json") or {})
    update_fn(stats)
    return supabase_upsert_stats(system_id, stats, touches=touches)


def supabase_update_stats(system_id: str, touches: int = 1) -> dict:
    return update_system_stats(system_id, lambda _stats: None, touches=touches)


def is_build_session(narrative: str, decisions: list) -> bool:
    text = f"{narrative} {' '.join(str(d) for d in decisions)}".lower()
    build_words = ["build", "code", "commit", "push", "ship", "implement", "fix", "test", "migration", "deploy"]
    return any(word in text for word in build_words)


def update_jarvis_session_stats(platform: str, entropy: dict, narrative: str, decisions: list) -> dict:
    def mutate(stats: dict) -> None:
        stats["sessions_sealed"] = int(stats.get("sessions_sealed", 0)) + 1
        stats["entropy_current"] = entropy["score"]
        stats["entropy_trend"] = "watch" if entropy["score"] >= 0.6 else "stable"
        platforms = set(stats.get("platforms_seen") or [])
        platforms.add(platform)
        stats["platforms_seen"] = sorted(platforms)
        stats["platforms_active"] = len(platforms)
        if is_build_session(narrative, decisions):
            stats["build_sessions"] = int(stats.get("build_sessions", 0)) + 1
        else:
            stats["theory_sessions"] = int(stats.get("theory_sessions", 0)) + 1
        theory = max(int(stats.get("theory_sessions", 0)), 1)
        stats["build_vs_theory_ratio"] = round(int(stats.get("build_sessions", 0)) / theory, 3)

    return update_system_stats("JARVIS", mutate, touches=1)


def update_jarvis_decision_stats() -> dict:
    return update_system_stats("JARVIS", lambda stats: stats.update({
        "decisions_logged": int(stats.get("decisions_logged", 0)) + 1
    }), touches=1)


def update_eris_session_stats(entropy: dict) -> dict:
    def mutate(stats: dict) -> None:
        stats["gold_law_checks"] = int(stats.get("gold_law_checks", 0)) + 1
        stats["mission_alignment_score"] = round(max(0.0, 1.0 - float(entropy["score"])), 3)
        if entropy.get("eris_action"):
            stats["entropy_signals_sent"] = int(stats.get("entropy_signals_sent", 0)) + 1
            stats["last_signal_reason"] = entropy["eris_action"]

    return update_system_stats("ERIS", mutate, touches=1)


def update_mnemos_session_stats(vector_saved: bool) -> dict:
    def mutate(stats: dict) -> None:
        stats["sessions_stored"] = int(stats.get("sessions_stored", 0)) + 1
        if vector_saved:
            stats["vector_count"] = int(stats.get("vector_count", 0)) + 1

    return update_system_stats("MNEMOS", mutate, touches=1)


def update_prometheus_decision_stats(system: str, eris_weight: float = 0.9) -> dict:
    def mutate(stats: dict) -> None:
        previous_count = int(stats.get("decisions_logged", 0))
        stats["decisions_logged"] = previous_count + 1
        affected = list(stats.get("systems_most_affected") or [])
        if system and system not in affected:
            affected.append(system)
        stats["systems_most_affected"] = affected[-10:]
        stats["avg_eris_weight"] = round(((float(stats.get("avg_eris_weight", 0.0)) * previous_count) + eris_weight) / max(previous_count + 1, 1), 3)
        stats["pending_raven_approval"] = int(stats.get("pending_raven_approval", 0)) + 1
        stats["last_decision_system"] = system

    return update_system_stats("PROMETHEUS", mutate, touches=1)


def update_nemesis_overlap_stats(system_a: str, system_b: str, score: float, status: str) -> dict:
    def mutate(stats: dict) -> None:
        stats["overlap_checks"] = int(stats.get("overlap_checks", 0)) + 1
        if score > 0.45:
            stats["warnings_issued"] = int(stats.get("warnings_issued", 0)) + 1
        if status == "canonical_conflict":
            stats["conflicts_found"] = int(stats.get("conflicts_found", 0)) + 1
        if score > float(stats.get("highest_overlap_score", 0.0)):
            stats["highest_overlap_pair"] = f"{system_a}/{system_b}"
            stats["highest_overlap_score"] = score

    return update_system_stats("NEMESIS", mutate, touches=1)


def update_mnemos_retrieval_stats() -> dict:
    return update_system_stats("MNEMOS", lambda stats: stats.update({
        "retrieval_count": int(stats.get("retrieval_count", 0)) + 1
    }), touches=1)


# ── Neo4j helpers ─────────────────────────────────────────────────────────
_neo4j_driver = None

def get_neo4j_driver():
    global _neo4j_driver
    if _neo4j_driver is not None:
        return _neo4j_driver
    try:
        from neo4j import GraphDatabase
    except ImportError:
        raise RuntimeError("neo4j package not installed. Run: pip install neo4j>=5.0.0")
    if not NEO4J_PASS:
        raise RuntimeError(
            "NEO4J_PASSWORD not configured.\n"
            "Add NEO4J_PASSWORD=<password> to C:\\Users\\JB\\jarvis\\.env\n"
            "Then open Neo4j Desktop, start a local DBMS, and note the password."
        )
    _neo4j_driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASS))
    _neo4j_driver.verify_connectivity()
    return _neo4j_driver


def neo4j_run(cypher: str, params: dict | None = None) -> list[dict]:
    driver = get_neo4j_driver()
    with driver.session() as session:
        result = session.run(cypher, params or {})
        return [dict(r) for r in result]


def neo4j_write_session(entry: dict) -> None:
    sid = entry["session_id"]
    neo4j_run(
        "MERGE (s:Session {id: $id}) SET s += $props",
        {"id": sid, "props": {
            "id":             sid,
            "platform":       entry.get("platform", ""),
            "archetype":      entry.get("archetype", ""),
            "sealed_at":      entry.get("sealed_at", ""),
            "narrative":      (entry.get("narrative", "") or "")[:200],
            "entropy":        entry.get("entropy", 0.0),
            "entropy_status": entry.get("entropy_status", ""),
        }}
    )
    chaos       = load_chaos()
    known       = set(chaos.get("god_systems", {}).keys())
    search_text = (
        " ".join(entry.get("decisions", [])) + " " + entry.get("narrative", "")
    ).upper()
    for sys_name in known:
        if sys_name in search_text:
            neo4j_run(
                "MATCH (s:Session {id: $sid}), (g:GodSystem {id: $gid}) "
                "MERGE (s)-[:TOUCHED]->(g)",
                {"sid": sid, "gid": sys_name}
            )


def neo4j_write_decision(entry: dict) -> None:
    did    = entry["id"]
    system = (entry.get("system_affected") or "GENERAL").upper()
    neo4j_run(
        "MERGE (d:Decision {id: $id}) SET d += $props",
        {"id": did, "props": {
            "id":              did,
            "decision":        (entry.get("decision", "") or "")[:200],
            "rationale":       (entry.get("rationale", "") or "")[:200],
            "system_affected": system,
            "timestamp":       entry.get("timestamp", ""),
            "raven_approved":  entry.get("raven_approved", False),
        }}
    )
    neo4j_run(
        "MATCH (d:Decision {id: $did}), (g:GodSystem {id: $gid}) "
        "MERGE (d)-[:AFFECTS]->(g)",
        {"did": did, "gid": system}
    )
    # Link decision to any Grid districts it mentions
    search_text = (
        (entry.get("decision", "") or "") + " " +
        (entry.get("rationale", "") or "")
    ).lower()
    for node in GRID_CANON:
        matched = any(kw in search_text for kw in node["keywords"])
        if not matched:
            matched = (
                node["district"].lower() in search_text or
                node["region"].lower() in search_text
            )
        if matched:
            nid = node["file"].replace(".md", "")
            try:
                neo4j_run(
                    "MATCH (d:Decision {id: $did}), (n:GridNode {id: $nid}) "
                    "MERGE (d)-[:AFFECTS_DISTRICT]->(n)",
                    {"did": did, "nid": nid}
                )
            except Exception:
                pass
    # Causal chain: link this decision to the one that caused it
    caused_by = (entry.get("caused_by") or "").strip()
    if caused_by:
        try:
            neo4j_run(
                "MATCH (d:Decision {id: $did}), (p:Decision {id: $pid}) "
                "MERGE (d)-[:CAUSED_BY]->(p)",
                {"did": did, "pid": caused_by}
            )
        except Exception:
            pass


def neo4j_seed_grid() -> dict:
    """Seed GRID_CANON into Neo4j as :GridNode nodes with :ROUTES_TO and :GOVERNS edges."""
    nodes_written = 0
    edges_written = 0

    def node_id(filename: str) -> str:
        return filename.replace(".md", "")

    for node in GRID_CANON:
        nid = node_id(node["file"])
        neo4j_run(
            "MERGE (n:GridNode {id: $id}) SET n += $props",
            {"id": nid, "props": {
                "id":              nid,
                "file":            node["file"],
                "region":          node["region"],
                "district":        node["district"],
                "suggested_ascent": node["suggested_ascent"],
                "keywords":        ",".join(node["keywords"][:10]),
                "updated_at":      now(),
            }}
        )
        nodes_written += 1

    for node in GRID_CANON:
        from_id = node_id(node["file"])
        for path_str in node["nearby_paths"]:
            fname = path_str.split(" — ")[0].strip()
            if fname.endswith(".md"):
                to_id = node_id(fname)
                try:
                    neo4j_run(
                        "MATCH (a:GridNode {id: $a}), (b:GridNode {id: $b}) "
                        "MERGE (a)-[:ROUTES_TO]->(b)",
                        {"a": from_id, "b": to_id}
                    )
                    edges_written += 1
                except Exception:
                    pass

    region_to_god = {
        "The Signal Spire": "ERIS",
        "The Routing Gate": "ODIN",
        "The Law Chamber":  "AEGIS",
        "The Neon Frontier": "JANUS",
    }
    for node in GRID_CANON:
        god = region_to_god.get(node["region"])
        if god:
            nid = node_id(node["file"])
            try:
                neo4j_run(
                    "MATCH (g:GodSystem {id: $gid}), (n:GridNode {id: $nid}) "
                    "MERGE (g)-[:GOVERNS]->(n)",
                    {"gid": god, "nid": nid}
                )
                edges_written += 1
            except Exception:
                pass

    return {"nodes": nodes_written, "edges": edges_written}


# ── Multimodal / image gen helpers ───────────────────────────────────────
IMAGE_GEN_URL  = os.environ.get("IMAGE_GEN_URL", "http://localhost:7860")
GRID_IMAGES_DIR = BASE_DIR / "grid_images"
LIVE_LOG_PATH  = BASE_DIR / "chaos" / "live_log.json"
OLLAMA_BASE    = "http://localhost:11434"


def live_log_append(action: str, file: str = "", status: str = "done") -> None:
    try:
        LIVE_LOG_PATH.parent.mkdir(exist_ok=True)
        data = json.loads(LIVE_LOG_PATH.read_text(encoding="utf-8")) if LIVE_LOG_PATH.exists() else []
        if not isinstance(data, list):
            data = []
        data.append({
            "time":   datetime.now().strftime("%H:%M:%S"),
            "action": action[:80],
            "file":   file[:60],
            "status": status,
        })
        if len(data) > 500:
            data = data[-500:]
        LIVE_LOG_PATH.write_text(json.dumps(data), encoding="utf-8")
    except Exception:
        pass


def detect_vision_model() -> str | None:
    try:
        req = urllib.request.Request(f"{OLLAMA_BASE}/api/tags")
        with urllib.request.urlopen(req, timeout=5) as r:
            data = json.loads(r.read().decode())
        hints = ("llava", "moondream", "bakllava", "cogvlm", "qwen-vl", "minicpm")
        for m in data.get("models", []):
            if any(h in m.get("name", "").lower() for h in hints):
                return m["name"]
    except Exception:
        pass
    return None


def ollama_vision(image_b64: str, question: str, model: str) -> str:
    # Try generate endpoint first (works for moondream and llava)
    payload = json.dumps({
        "model":  model,
        "prompt": question,
        "images": [image_b64],
        "stream": False,
    }).encode()
    req = urllib.request.Request(
        f"{OLLAMA_BASE}/api/generate",
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=120) as r:
        result = json.loads(r.read().decode())
    return result.get("response", "").strip()


def build_grid_image_prompt(node: dict) -> tuple[str, str]:
    mood   = GRID_REGION_MOODS.get(node["region"], "mysterious digital district, glowing pathways")
    prompt = f"{node['district']} — {node['region']}. {mood}. {TRON_BASE_STYLE}."
    return prompt, TRON_NEGATIVE


def call_image_gen(prompt: str, negative: str, width: int = 512, height: int = 512) -> dict:
    try:
        payload = json.dumps({
            "prompt":          prompt,
            "negative_prompt": negative,
            "width":           width,
            "height":          height,
            "steps":           20,
            "cfg_scale":       7,
            "sampler_name":    "Euler a",
        }).encode()
        req = urllib.request.Request(
            f"{IMAGE_GEN_URL}/sdapi/v1/txt2img",
            data=payload,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=120) as r:
            data = json.loads(r.read().decode())
        images = data.get("images", [])
        if not images:
            return {"ok": False, "image_b64": None, "error": "No images in response"}
        return {"ok": True, "image_b64": images[0], "error": None}
    except Exception as e:
        return {"ok": False, "image_b64": None, "error": str(e)}


def generate_concept_card(node: dict) -> Path | None:
    try:
        from PIL import Image, ImageDraw, ImageFont
    except ImportError:
        return None

    w, h = 512, 512
    bg   = (0, 2, 10)
    img  = Image.new("RGB", (w, h), bg)
    draw = ImageDraw.Draw(img)

    # Subtle grid lines
    for x in range(0, w, 32):
        draw.line([(x, 0), (x, h)], fill=(0, 12, 22))
    for y in range(0, h, 32):
        draw.line([(0, y), (w, y)], fill=(0, 12, 22))

    # Outer borders
    draw.rectangle([2, 2, w-3, h-3], outline=(0, 160, 210))
    draw.rectangle([6, 6, w-7, h-7], outline=(0, 60, 90))

    # Corner brackets
    cs, cyan = 20, (0, 240, 255)
    for pts in [
        ((6, 6+cs), (6, 6), (6+cs, 6)),
        ((w-7-cs, 6), (w-7, 6), (w-7, 6+cs)),
        ((6, h-7-cs), (6, h-7), (6+cs, h-7)),
        ((w-7-cs, h-7), (w-7, h-7), (w-7, h-7-cs)),
    ]:
        draw.line(pts, fill=cyan, width=2)

    # Fonts
    try:
        font_lg = ImageFont.load_default(size=30)
        font_md = ImageFont.load_default(size=14)
        font_sm = ImageFont.load_default(size=11)
    except TypeError:
        font_lg = font_md = font_sm = ImageFont.load_default()

    def center_text(text, y, font, color):
        bb = draw.textbbox((0, 0), text, font=font)
        x  = (w - (bb[2] - bb[0])) // 2
        draw.text((x, y), text, fill=color, font=font)

    region   = node.get("region", "THE GRID").upper()
    district = node.get("district", "UNKNOWN").upper()

    center_text(region, 28, font_sm, (0, 90, 140))
    draw.line([(40, 56), (w-40, 56)], fill=(0, 60, 90))

    # Word-wrapped district name
    words    = district.split()
    lines_d, line = [], ""
    for word in words:
        test = (line + " " + word).strip()
        bb   = draw.textbbox((0, 0), test, font=font_lg)
        if bb[2] - bb[0] > w - 60 and line:
            lines_d.append(line)
            line = word
        else:
            line = test
    if line:
        lines_d.append(line)

    y0 = h // 2 - (len(lines_d) * 38) // 2
    for ln in lines_d:
        center_text(ln, y0, font_lg, (0, 230, 255))
        y0 += 38

    draw.line([(40, h-98), (w-40, h-98)], fill=(0, 60, 90))
    center_text("CONCEPT CARD  —  JARVIS GRID", h-82, font_sm, (0, 55, 80))
    center_text(now()[:10], h-58, font_sm, (0, 40, 60))

    GRID_IMAGES_DIR.mkdir(exist_ok=True)
    slug     = node.get("file", "custom").replace(".md", "")
    img_path = GRID_IMAGES_DIR / f"{slug}_{now()[:10]}.png"
    img.save(str(img_path))
    return img_path


def find_git() -> str | None:
    candidates = [
        shutil.which("git"),
        r"C:\Program Files\Git\cmd\git.exe",
        r"C:\Program Files\Git\bin\git.exe",
        str(Path.home() / "AppData" / "Local" / "Programs" / "Git" / "cmd" / "git.exe"),
    ]
    for candidate in candidates:
        if candidate and Path(candidate).exists():
            return candidate
    return None


def run_git(args: list[str], timeout: int = 20) -> dict:
    git = find_git()
    if not git:
        return {"ok": False, "code": None, "out": "", "err": "git executable not found"}
    try:
        proc = subprocess.run(
            [git, *args],
            cwd=BASE_DIR,
            capture_output=True,
            text=True,
            timeout=timeout,
            check=False,
        )
        return {
            "ok": proc.returncode == 0,
            "code": proc.returncode,
            "out": proc.stdout.strip(),
            "err": proc.stderr.strip(),
        }
    except subprocess.TimeoutExpired:
        return {"ok": False, "code": None, "out": "", "err": f"git {' '.join(args)} timed out"}
    except Exception as e:
        return {"ok": False, "code": None, "out": "", "err": str(e)}

# ── Local fallback ────────────────────────────────────────────────────────
LOG_PATH  = BASE_DIR / "chaos" / "session_log.json"
PROM_PATH = BASE_DIR / "chaos" / "prometheus_log.json"

def load_chaos() -> dict:
    if CHAOS_PATH.exists():
        return json.loads(CHAOS_PATH.read_text())
    return {}

def load_log(path: Path) -> list:
    if path.exists():
        return json.loads(path.read_text())
    return []

def save_log(path: Path, data: list) -> None:
    path.write_text(json.dumps(data, indent=2))


def store_mnemos_session(entry: dict) -> dict:
    try:
        import sys as _sys
        _sys.path.insert(0, str(BASE_DIR / "mnemos"))
        from mnemos_vector import MNEMOSVector
        return {"ok": True, "entry": MNEMOSVector().store_session(entry), "error": None}
    except Exception as e:
        return {"ok": False, "entry": None, "error": str(e)}


def store_mnemos_prometheus(entry: dict) -> dict:
    try:
        import sys as _sys
        _sys.path.insert(0, str(BASE_DIR / "mnemos"))
        from mnemos_vector import MNEMOSVector
        return {"ok": True, "entry": MNEMOSVector().store_prometheus(entry), "error": None}
    except Exception as e:
        return {"ok": False, "entry": None, "error": str(e)}


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


def fingerprint(obj: dict) -> str:
    return hashlib.sha256(json.dumps(obj, sort_keys=True).encode()).hexdigest()[:16]


def compute_entropy_vector(chaos: dict) -> dict:
    systems  = chaos.get("god_systems", {})
    gold_law = chaos.get("gold_law", {}).get("rules", [])
    mission  = chaos.get("mission_statement", {}).get("primary", "")
    forbidden = chaos.get("interaction_graph", {}).get("forbidden_edges", [])
    pipeline = chaos.get("pipeline", {}).get("order", [])
    count    = len(systems)
    target   = 27

    dimensions = {
        "abstraction_entropy": round(min(1.0, max(0.0, (count - target) / max(target, 1))), 3),
        "authority_entropy":   round(min(1.0, max(0.0, 1.0 - len(forbidden) / 10.0)), 3),
        "routing_entropy":     round(0.0 if len(pipeline) >= 7 else 0.4, 3),
        "semantic_entropy":    round(0.0 if "JARVIS" in mission else 0.5, 3),
        "memory_entropy":      0.0,
        "interface_entropy":   round(min(1.0, max(0.0, 1.0 - count / 30.0)), 3),
        "overlap_entropy":     round(min(1.0, max(0.0, (count - 20) / 10.0)), 3),
    }

    score = round(sum(dimensions.values()) / 7, 3)
    status = (
        "ALIGNED" if score < 0.3 else
        "WATCH"   if score < 0.6 else
        "SIGNAL"  if score < 0.8 else
        "CRITICAL"
    )
    eris_action = (
        None if score < 0.6 else
        "signals governance systems" if score < 0.8 else
        "signals directly to Raven"
    )

    return {
        "score": score,
        "status": status,
        "dimensions": dimensions,
        "eris_action": eris_action,
        "timestamp": now()
    }


TOOLS = [
    {
        "name": "jarvis_status",
        "description": "Get current JARVIS system status, mission, entropy score, Gold Law rules, and platform roles. Call at session start.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "platform": {"type": "string", "enum": ["claude", "gpt", "gemini", "codex"]}
            },
            "required": []
        }
    },
    {
        "name": "jarvis_entropy",
        "description": "Get Eris entropy score (7-dimensional). Score > 0.6 = ERIS signals governance. Score > 0.8 = signals Raven.",
        "inputSchema": {"type": "object", "properties": {}, "required": []}
    },
    {
        "name": "jarvis_god_system",
        "description": "Look up canonical contract for any JARVIS God System by name (e.g. ERIS, AEGIS, ODIN, SKADI).",
        "inputSchema": {
            "type": "object",
            "properties": {"system_name": {"type": "string"}},
            "required": ["system_name"]
        }
    },
    {
        "name": "jarvis_end",
        "description": "Seal current session (JARVIS END). Records narrative and entropy to session log.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "platform": {"type": "string", "enum": ["claude", "gpt", "gemini", "codex"]},
                "narrative": {"type": "string"},
                "decisions": {"type": "array", "items": {"type": "string"}}
            },
            "required": ["platform", "narrative"]
        }
    },
    {
        "name": "jarvis_log",
        "description": "Add entry to PROMETHEUS rationale ledger. Records WHY a decision was made. Permanent record.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "decision":        {"type": "string"},
                "rationale":       {"type": "string"},
                "system_affected": {"type": "string"},
                "caused_by":       {"type": "string", "description": "ID of a prior decision this one follows from (creates CAUSED_BY edge in Neo4j)"}
            },
            "required": ["decision", "rationale"]
        }
    },
    {
        "name": "jarvis_overlap",
        "description": "Run NEMESIS overlap score OS(A,B) between two God Systems. 0.46+ = ERIS review required.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "system_a": {"type": "string"},
                "system_b": {"type": "string"}
            },
            "required": ["system_a", "system_b"]
        }
    },
    {
        "name": "jarvis_sessions",
        "description": "View recent session history from MNEMOS log.",
        "inputSchema": {
            "type": "object",
            "properties": {"limit": {"type": "integer"}},
            "required": []
        }
    },
    {
        "name": "jarvis_recall",
        "description": (
            "Semantic memory search (MNEMOS vector layer). "
            "Finds past sessions, decisions, and God System knowledge "
            "most relevant to your query. Ranked by cosine similarity "
            "weighted by ERIS entropy — aligned sessions rank higher. "
            "Use this to retrieve relevant context before starting work."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "What you want to find in memory"
                },
                "limit": {
                    "type": "integer",
                    "description": "Max results to return (default 5)"
                },
                "source_type": {
                    "type": "string",
                    "enum": ["session", "prometheus", "god_system", "checkpoint"],
                    "description": "Filter by memory type (optional)"
                }
            },
            "required": ["query"]
        }
    },
    {
        "name": "jarvis_repo_sync",
        "description": (
            "Inspect or pull the local JARVIS GitHub checkout. "
            "Use action=status to check branch/dirty state; use action=pull "
            "only when the user wants the MCP server to update local code from origin."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "action": {
                    "type": "string",
                    "enum": ["status", "pull"],
                    "description": "status checks local Git state; pull fetches and fast-forwards from origin"
                }
            },
            "required": []
        }
    },
    {
        "name": "jarvis_stats",
        "description": "Read JARVIS/God System stats from Supabase. Use without system_id for a compact system list.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "system_id": {
                    "type": "string",
                    "description": "Optional system id such as JARVIS, ERIS, MNEMOS, PROMETHEUS, or NEMESIS"
                }
            },
            "required": []
        }
    },
    {
        "name": "jarvis_neo4j",
        "description": (
            "JARVIS knowledge graph (Neo4j). "
            "Programmatic graph for God System interaction maps, session entity graphs, "
            "and HUGINN cross-session diffs. "
            "Boundary (NEMESIS-ratified): GBrain owns personal brain pages; "
            "Neo4j owns JARVIS-native structured graphs. "
            "Actions: query (raw Cypher), upsert_node, upsert_edge, traverse, init_god_systems."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "action": {
                    "type": "string",
                    "enum": ["query", "upsert_node", "upsert_edge", "traverse", "init_god_systems"],
                    "description": "Operation to perform"
                },
                "cypher":     {"type": "string",  "description": "Cypher query string (action=query)"},
                "params":     {"type": "object",  "description": "Cypher parameters (action=query)"},
                "label":      {"type": "string",  "description": "Node label, e.g. GodSystem, Session, Decision (action=upsert_node)"},
                "node_id":    {"type": "string",  "description": "Unique node identifier (action=upsert_node | traverse)"},
                "properties": {"type": "object",  "description": "Node or edge properties"},
                "from_id":    {"type": "string",  "description": "Source node id (action=upsert_edge)"},
                "to_id":      {"type": "string",  "description": "Target node id (action=upsert_edge)"},
                "rel_type":   {"type": "string",  "description": "Relationship type, e.g. PIPELINE_NEXT, TOUCHED, DECIDED (action=upsert_edge)"},
                "depth":      {"type": "integer", "description": "Traversal depth 1-4 (action=traverse, default 1)"},
                "direction":  {"type": "string",  "enum": ["out", "in", "both"], "description": "Traversal direction (action=traverse, default both)"}
            },
            "required": ["action"]
        }
    },
    {
        "name": "jarvis_grid",
        "description": (
            "Navigate THE GRID — a text-based spatial interface over JARVIS canon. "
            "Returns location, nearby paths (live from Neo4j), warnings, and suggested ascent. "
            "Modes: enter a region (keyword query), ODIN route ('route from X to Y'), "
            "or PROMETHEUS causal history ('history of X', 'why X', 'decisions in X'). "
            "Omit query to see the full map."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": (
                        "Navigation query. Examples: 'codex authority', "
                        "'route from governed workflow to grid design bible', "
                        "'history of routing gate', 'why codex authority'"
                    )
                }
            },
            "required": []
        }
    },
    {
        "name": "jarvis_vision",
        "description": (
            "Multimodal image analysis via Ollama. "
            "Accepts a local image path or base64 data and returns a description "
            "using the best available vision model (moondream, llava, etc.). "
            "Pull a model first: `ollama pull moondream` (~1 GB)."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "image_path":   {"type": "string", "description": "Absolute path to a local image file"},
                "image_base64": {"type": "string", "description": "Base64-encoded image data (alternative to image_path)"},
                "question":     {"type": "string", "description": "What to ask about the image (default: general JARVIS-context description)"},
                "model":        {"type": "string", "description": "Ollama vision model override (default: auto-detect)"},
            },
            "required": []
        }
    },
    {
        "name": "jarvis_image",
        "description": (
            "Grid location card image generation. "
            "Builds Tron-aesthetic prompts from Grid district metadata. "
            "action=prompt returns the prompt for manual use (works immediately). "
            "action=generate calls a local SD-compatible endpoint (set IMAGE_GEN_URL in .env). "
            "action=list_models shows vision and image gen status."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "action":        {"type": "string", "enum": ["prompt", "generate", "list_models"], "description": "Operation to perform"},
                "district":      {"type": "string", "description": "Grid district keyword, e.g. 'routing gate', 'heartbeat watcher'"},
                "region":        {"type": "string", "description": "Grid region name for a region-level card, e.g. 'signal spire', 'neon frontier', 'law chamber'"},
                "custom_prompt": {"type": "string", "description": "Override the auto-generated prompt"},
                "width":         {"type": "integer", "description": "Image width in pixels (256–1024, default 512)"},
                "height":        {"type": "integer", "description": "Image height in pixels (256–1024, default 512)"},
            },
            "required": []
        }
    },
    {
        "name": "jarvis_gemini_handoff",
        "description": (
            "Route a task to Gemini (Aizen — ideation, interpretation, instance demonstration). "
            "Writes a governed intake file to intake/gemini/ and returns the file path plus "
            "a ready-to-paste Gemini prompt. Review the intake file before acting on Gemini output."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "task": {
                    "type": "string",
                    "description": "What you want Gemini to do — ideate, interpret, or demonstrate"
                },
                "task_type": {
                    "type": "string",
                    "enum": ["ideation", "interpretation", "concept", "brainstorm"],
                    "description": "Aizen mode to invoke (default: ideation)"
                },
                "context": {
                    "type": "string",
                    "description": "Optional background context to include in the Gemini prompt"
                },
                "topic_slug": {
                    "type": "string",
                    "description": "Short kebab-case label for the intake filename, e.g. 'pachinko-monetization'"
                }
            },
            "required": ["task"]
        }
    },
]

PLATFORM_ARCHETYPES = {
    "claude": {"archetype": "Shiroe", "role": "vetting, audit, consistency enforcement"},
    "gpt":    {"archetype": "Kang",   "role": "production, execution, organized JARVIS spec"},
    "gemini": {"archetype": "Aizen",  "role": "ideation, interpretation, instance demonstration"},
    "codex":  {"archetype": "Kang",   "role": "JARVIS execution layer: local/network implementation, repo control, governed automation"},
}


async def handle_jarvis_status(args: dict) -> str:
    chaos    = load_chaos()
    platform = args.get("platform", "claude")
    arch     = PLATFORM_ARCHETYPES.get(platform, PLATFORM_ARCHETYPES["claude"])
    entropy  = compute_entropy_vector(chaos)
    systems  = chaos.get("god_systems", {})
    mission  = chaos.get("mission_statement", {})
    pipeline = chaos.get("pipeline", {}).get("order", [])
    gold_law = chaos.get("gold_law", {}).get("rules", [])

    return f"""JARVIS STATUS — {now()}
═══════════════════════════════════════════
PLATFORM:   {platform.upper()} ({arch['archetype']} — {arch['role']})
VERSION:    JARVIS v{chaos.get('jarvis_version', '2.5')} | CHAOS v{chaos.get('chaos_version', '1.1')}
RAVEN:      {mission.get('raven', 'Human operator')}
GUARDIAN:   {mission.get('guardian', 'ERIS - mission and entropy guardian')}

MISSION:
{mission.get('primary', 'Build JARVIS. Build useful AI workflows. Keep human authority explicit.')}

ERIS ENTROPY: {entropy['score']} [{entropy['status']}]
  abstraction: {entropy['dimensions']['abstraction_entropy']} | authority: {entropy['dimensions']['authority_entropy']}
  routing:     {entropy['dimensions']['routing_entropy']} | semantic: {entropy['dimensions']['semantic_entropy']}
  memory:      {entropy['dimensions']['memory_entropy']} | interface: {entropy['dimensions']['interface_entropy']}
  overlap:     {entropy['dimensions']['overlap_entropy']}
{f"⚠ ERIS ACTION: {entropy['eris_action']}" if entropy['eris_action'] else "✓ ERIS: Mission aligned"}

PIPELINE:   {' → '.join(pipeline)}
SYSTEMS:    {len(systems)} God Systems active

GOLD LAW ({len(gold_law)} rules):
{chr(10).join(f'  • {r}' for r in gold_law[:5])}{'...' if len(gold_law) > 5 else ''}

THREE-PLATFORM WORKFLOW:
  Ideation   → Gemini (Aizen)
  Vetting    → Claude (Shiroe)
  Production → GPT (Kang)"""


async def handle_jarvis_entropy(args: dict) -> str:
    chaos   = load_chaos()
    entropy = compute_entropy_vector(chaos)
    dims    = entropy['dimensions']
    bars    = {k: "█" * int(v * 20) + "░" * (20 - int(v * 20)) for k, v in dims.items()}

    return f"""ERIS ENTROPY VECTOR — {entropy['timestamp']}
═══════════════════════════════════════════
SCORE:  {entropy['score']:.3f}  [{entropy['status']}]
{f"⚠ ACTION: {entropy['eris_action']}" if entropy['eris_action'] else "✓ ALIGNED"}

DIMENSIONS:
  abstraction [{bars['abstraction_entropy']}] {dims['abstraction_entropy']:.3f}
  authority   [{bars['authority_entropy']}] {dims['authority_entropy']:.3f}
  routing     [{bars['routing_entropy']}] {dims['routing_entropy']:.3f}
  semantic    [{bars['semantic_entropy']}] {dims['semantic_entropy']:.3f}
  memory      [{bars['memory_entropy']}] {dims['memory_entropy']:.3f}
  interface   [{bars['interface_entropy']}] {dims['interface_entropy']:.3f}
  overlap     [{bars['overlap_entropy']}] {dims['overlap_entropy']:.3f}

THRESHOLDS:
  > 0.6 → ERIS signals governance systems
  > 0.8 → ERIS signals directly to Raven
  = 1.0 → condition Eris exists to prevent"""


async def handle_jarvis_god_system(args: dict) -> str:
    name  = args.get("system_name", "").upper()
    chaos = load_chaos()
    s     = chaos.get("god_systems", {}).get(name)

    if not s:
        available = sorted(chaos.get("god_systems", {}).keys())
        return f"Unknown system: {name}\nAvailable: {', '.join(available)}"

    return f"""GOD SYSTEM: {name}
═══════════════════════════════════════════
TIER:     {s.get('tier', '?')}
FUNCTION: {s.get('function', s.get('role', '?'))}
CANNOT:
{chr(10).join(f'  ✗ {c}' for c in s.get('cannot', ['(no restrictions listed)'])[:6])}"""


async def handle_jarvis_end(args: dict) -> str:
    platform  = args.get("platform", "claude")
    narrative = args.get("narrative", "Session sealed.")
    decisions = args.get("decisions", [])
    arch      = PLATFORM_ARCHETYPES.get(platform, {})
    chaos     = load_chaos()
    entropy   = compute_entropy_vector(chaos)
    fp        = fingerprint(chaos)

    entry = {
        "session_id":        str(uuid.uuid4())[:8],
        "platform":          platform,
        "archetype":         arch.get("archetype", "?"),
        "sealed_at":         now(),
        "narrative":         narrative,
        "decisions":         decisions,
        "entropy":           entropy["score"],
        "entropy_status":    entropy["status"],
        "chaos_fingerprint": fp
    }

    # Write to Supabase
    session_sync = supabase_insert("session_log", {
        "platform":          entry["platform"],
        "archetype":         entry["archetype"],
        "sealed_at":         entry["sealed_at"],
        "narrative":         entry["narrative"],
        "entropy":           entry["entropy"],
        "entropy_status":    entry["entropy_status"],
        "decisions":         entry["decisions"]
    })
    entropy_sync = supabase_insert("eris_entropy_log", {
        "score":      entropy["score"],
        "status":     entropy["status"],
        "dimensions": entropy["dimensions"],
        "timestamp":  now()
    })
    # Local fallback
    log = load_log(LOG_PATH)
    log.append(entry)
    save_log(LOG_PATH, log)
    mnemos_vector = store_mnemos_session(entry)
    try:
        neo4j_write_session(entry)
    except Exception:
        pass
    # Update meaningful stats after the real work has happened.
    jarvis_stats = update_jarvis_session_stats(platform, entropy, narrative, decisions)
    mnemos_stats = update_mnemos_session_stats(bool(mnemos_vector.get("ok")))
    eris_stats = update_eris_session_stats(entropy)

    return f"""SESSION SEALED — {entry['sealed_at']}
═══════════════════════════════════════════
SESSION ID:  {entry['session_id']}
PLATFORM:    {platform.upper()} ({arch.get('archetype', '?')})
CHAOS SEED:  {fp}...
ENTROPY:     {entropy['score']:.3f} [{entropy['status']}]

NARRATIVE:
{narrative}

{f"DECISIONS ({len(decisions)}):" + chr(10) + chr(10).join(f'  • {d}' for d in decisions) if decisions else ""}
✓ Session logged to MNEMOS
{f"⚠ ERIS: {entropy['eris_action']}" if entropy['eris_action'] else "✓ ERIS: Mission aligned at seal"}"""


async def handle_jarvis_log(args: dict) -> str:
    decision  = args.get("decision", "")
    rationale = args.get("rationale", "")
    system    = args.get("system_affected", "GENERAL")
    caused_by = (args.get("caused_by") or "").strip()

    entry = {
        "id":              str(uuid.uuid4())[:8],
        "timestamp":       now(),
        "decision":        decision,
        "rationale":       rationale,
        "system_affected": system,
        "raven_approved":  False,
        "caused_by":       caused_by,
    }

    # Write to Supabase
    prometheus_sync = supabase_insert("prometheus_log", {
        "decision":        entry["decision"],
        "rationale":       entry["rationale"],
        "system_affected": entry["system_affected"],
        "eris_weight":     0.9,
        "raven_approved":  False,
        "timestamp":       entry["timestamp"]
    })
    # Local fallback
    log = load_log(PROM_PATH)
    log.append(entry)
    save_log(PROM_PATH, log)
    live_log_append(f"PROMETHEUS: {decision[:60]}", system, "done")
    mnemos_vector = store_mnemos_prometheus(entry)
    try:
        neo4j_write_decision(entry)
    except Exception:
        pass
    stats_sync = supabase_update_stats(entry["system_affected"])
    jarvis_stats = update_jarvis_decision_stats()
    prometheus_stats = update_prometheus_decision_stats(entry["system_affected"])

    return f"""PROMETHEUS LOG — Entry #{len(log)}
═══════════════════════════════════════════
ID: {entry['id']} | SYSTEM: {system}
DECISION: {decision}
RATIONALE: {rationale}
STATUS: Pending Raven approval ✓"""


async def handle_jarvis_overlap(args: dict) -> str:
    a = args.get("system_a", "").upper()
    b = args.get("system_b", "").upper()

    chaos   = load_chaos()
    systems = chaos.get("god_systems", {})

    if a not in systems:
        return f"Unknown system: {a}\nAvailable: {', '.join(sorted(systems.keys()))}"
    if b not in systems:
        return f"Unknown system: {b}\nAvailable: {', '.join(sorted(systems.keys()))}"

    sa = systems[a].get("function", systems[a].get("role", ""))
    sb = systems[b].get("function", systems[b].get("role", ""))

    words_a  = set(sa.lower().split())
    words_b  = set(sb.lower().split())
    semantic = len(words_a & words_b) / max(len(words_a | words_b), 1)

    tier_a    = systems[a].get("tier", "")
    tier_b    = systems[b].get("tier", "")
    authority = 0.8 if tier_a == tier_b else 0.2

    score  = round((semantic + authority) / 2, 3)
    status = (
        "safe"               if score < 0.26 else
        "warning"            if score < 0.46 else
        "eris_review"        if score < 0.66 else
        "canonical_conflict"
    )
    nemesis_stats = update_nemesis_overlap_stats(a, b, score, status)

    return f"""NEMESIS OVERLAP: {a} ↔ {b}
═══════════════════════════════════════════
SCORE: {score:.3f} [{status.upper()}]
  semantic:  {semantic:.3f}
  authority: {authority:.3f} (same tier: {tier_a == tier_b})

{"✓ Safe — no action required" if status == "safe" else "⚠ Monitor for role absorption" if status == "warning" else "🔴 ERIS review required" if status == "eris_review" else "🚨 Canonical conflict — ATHENA required"}"""


async def handle_jarvis_sessions(args: dict) -> str:
    limit  = args.get("limit", 5)
    log    = load_log(LOG_PATH)
    recent = log[-limit:][::-1]

    if not recent:
        return "No sessions logged yet. Use jarvis_end to seal your first session."

    lines = ["RECENT SESSIONS (MNEMOS LOG)", "═" * 43]
    for s in recent:
        lines.append(f"\n[{s.get('session_id','?')}] {s.get('sealed_at','?')[:16]}")
        lines.append(f"  Platform: {s.get('platform','?').upper()} ({s.get('archetype','?')})")
        lines.append(f"  Entropy:  {s.get('entropy','?')} [{s.get('entropy_status','?')}]")
        lines.append(f"  Notes:    {s.get('narrative','')[:80]}")

    return "\n".join(lines)


async def handle_jarvis_recall(args: dict) -> str:
    query       = args.get("query", "")
    limit       = args.get("limit", 5)
    source_type = args.get("source_type", None)

    if not query:
        return "Query required. What should MNEMOS search for?"

    try:
        import sys as _sys
        _sys.path.insert(0, str(BASE_DIR / "mnemos"))
        from mnemos_vector import MNEMOSVector
        mnemos  = MNEMOSVector()
        results = mnemos.search(query, limit=limit, source_type=source_type)
    except ConnectionError:
        return "Ollama not reachable. Make sure Ollama is running for vector search."
    except ImportError:
        return "mnemos_vector.py not found. Place it in jarvis/mnemos/"
    except Exception as e:
        return f"Vector search error: {e}"

    if not results:
        return f"No memories found for: '{query}'\nSeal some sessions first to build memory."

    lines = [
        f"MNEMOS RECALL — '{query}'",
        "=" * 43,
        f"Found {len(results)} relevant memories (ERIS-weighted)\n"
    ]
    for i, r in enumerate(results, 1):
        lines.append(f"[{i}] {r['source_type'].upper()} score:{r['eris_score']:.3f} entropy:{r['entropy']:.3f}")
        lines.append(f"     {r['text'][:100]}")
        lines.append(f"     {r['timestamp'][:16]}")
        lines.append("")
    mnemos_stats = update_mnemos_retrieval_stats()
    return "\n".join(lines)


async def handle_jarvis_repo_sync(args: dict) -> str:
    action = args.get("action", "status")
    if action not in {"status", "pull"}:
        return "Unknown repo sync action. Use action=status or action=pull."

    root = run_git(["rev-parse", "--show-toplevel"])
    if not root["ok"]:
        return f"JARVIS repo sync unavailable: {root['err'] or root['out']}"

    branch = run_git(["branch", "--show-current"])
    status = run_git(["status", "--short", "--branch"])
    remote = run_git(["remote", "get-url", "origin"])

    if action == "status":
        return "\n".join([
            "JARVIS REPO STATUS",
            "=" * 18,
            f"repo:   {root['out']}",
            f"branch: {branch['out'] or 'unknown'}",
            f"origin: {remote['out'] or 'unknown'}",
            "",
            status["out"] or "clean",
        ])

    dirty = run_git(["status", "--porcelain"])
    if not dirty["ok"]:
        return f"Could not inspect working tree before pull: {dirty['err'] or dirty['out']}"
    if dirty["out"]:
        return "\n".join([
            "Pull blocked: local working tree has uncommitted changes.",
            "Commit, stash, or review these files first:",
            dirty["out"],
        ])

    pull = run_git(["pull", "--ff-only", "origin", branch["out"] or "main"], timeout=60)
    if not pull["ok"]:
        return "\n".join([
            "JARVIS repo pull failed.",
            pull["err"] or pull["out"] or "No output from git.",
        ])

    after = run_git(["rev-parse", "--short", "HEAD"])
    return "\n".join([
        "JARVIS repo pull complete.",
        pull["out"] or "Already up to date.",
        f"HEAD: {after['out'] or 'unknown'}",
    ])


async def handle_jarvis_stats(args: dict) -> str:
    if not supabase_enabled():
        return "JARVIS stats unavailable: Supabase credentials are not configured."

    system_id = args.get("system_id")
    try:
        if system_id:
            encoded = urllib.parse.quote(system_id.upper(), safe="")
            url = (
                f"{SUPABASE_URL}/rest/v1/god_system_stats"
                f"?system_id=eq.{encoded}"
                "&select=system_id,session_touches,last_updated,stats_json"
                "&limit=1"
            )
        else:
            url = (
                f"{SUPABASE_URL}/rest/v1/god_system_stats"
                "?select=system_id,session_touches,last_updated,stat_a_key,stat_a_val,stat_b_key,stat_b_val,stats_json"
                "&order=system_id.asc"
            )
        req = urllib.request.Request(
            url,
            headers={"apikey": SUPABASE_KEY, "Authorization": f"Bearer {SUPABASE_KEY}"}
        )
        with urllib.request.urlopen(req, timeout=5) as r:
            rows = json.loads(r.read().decode())
    except urllib.error.HTTPError as e:
        return f"JARVIS stats query failed: {e.read().decode(errors='replace')}"
    except Exception as e:
        return f"JARVIS stats query failed: {e}"

    if not rows:
        return f"No stats found for {system_id.upper() if system_id else 'JARVIS systems'}."

    if system_id:
        row = rows[0]
        stats = row.get("stats_json") or {}
        lines = [
            f"JARVIS STATS: {row.get('system_id')}",
            "=" * 24,
            f"session_touches: {row.get('session_touches', 0)}",
            f"last_updated: {row.get('last_updated', '?')}",
            "",
        ]
        lines.extend(f"{key}: {value}" for key, value in stats.items())
        return "\n".join(lines)

    lines = ["JARVIS SYSTEM STATS", "=" * 20]
    for row in rows:
        stats = row.get("stats_json") or {}
        primary = row.get("stat_a_key") or next(iter(stats.keys()), "session_touches")
        primary_val = row.get("stat_a_val", stats.get(primary, row.get("session_touches", 0)))
        secondary = row.get("stat_b_key")
        secondary_val = row.get("stat_b_val")
        tail = f" | {secondary}: {secondary_val}" if secondary else ""
        lines.append(f"{row.get('system_id')}: touches={row.get('session_touches', 0)} | {primary}: {primary_val}{tail}")
    return "\n".join(lines)


async def handle_jarvis_grid(args: dict) -> str:
    query = args.get("query", "").lower().strip()

    def keyword_match(q: str):
        best_node = None
        best_score = 0
        q_words = set(q.split())
        for node in GRID_CANON:
            score = sum(1 for kw in node["keywords"] if kw in q)
            if node["file"].replace("-", " ").replace(".md", "") in q:
                score += 3
            # Score on region/district name word overlap (strips "the" from region)
            region_words  = set(node["region"].lower().split()) - {"the"}
            district_words = set(node["district"].lower().split())
            score += 2 * len(q_words & (region_words | district_words))
            if score > best_score:
                best_score = score
                best_node = node
        if best_score == 0:
            for node in GRID_CANON:
                for kw in node["keywords"]:
                    if q_words & set(kw.split()):
                        best_node = node
                        best_score = 1
                        break
                if best_node:
                    break
        return best_node

    def node_id(n: dict) -> str:
        return n["file"].replace(".md", "")

    # ── ODIN route query ───────────────────────────────────────────────────
    route_m = re.search(
        r'(?:from|route|path from|take me from)\s+(.+?)\s+(?:to|toward|towards)\s+(.+)',
        query
    )
    if route_m:
        from_q    = route_m.group(1).strip()
        to_q      = route_m.group(2).strip()
        from_node = keyword_match(from_q)
        to_node   = keyword_match(to_q)

        if not from_node or not to_node:
            missing = []
            if not from_node: missing.append(f"'{from_q}'")
            if not to_node:   missing.append(f"'{to_q}'")
            return (
                f"ODIN ROUTE — Location not found: {', '.join(missing)}\n"
                "Run jarvis_grid() for the full map."
            )

        from_id = node_id(from_node)
        to_id   = node_id(to_node)

        if from_id == to_id:
            return f"ODIN ROUTE — Already there: {from_node['region']} / {from_node['district']}"

        try:
            records = neo4j_run(
                "MATCH path = shortestPath((a:GridNode {id: $a})-[*..6]-(b:GridNode {id: $b})) "
                "RETURN [n IN nodes(path) | n.district + ' / ' + n.region] AS stops, "
                "       length(path) AS hops",
                {"a": from_id, "b": to_id}
            )
            if records:
                r     = records[0]
                stops = r.get("stops") or []
                hops  = r.get("hops", 0)
                lines = [
                    f"ODIN ROUTE  {from_node['district']} → {to_node['district']}",
                    "═" * 43,
                    f"Shortest path — {hops} hop{'s' if hops != 1 else ''}:",
                ]
                for i, stop in enumerate(stops):
                    marker = "◉" if i in (0, len(stops) - 1) else "·"
                    lines.append(f"  {marker} {stop}")
                lines += [
                    "",
                    "GOVERNED BY: Neo4j shortestPath(GridNode → GridNode)",
                    f"Explore: jarvis_neo4j(action='traverse', node_id='{from_id}')",
                ]
                return "\n".join(lines)
        except Exception:
            pass

        # Neo4j offline fallback
        lines = [
            f"ODIN ROUTE  {from_node['district']} → {to_node['district']}",
            "═" * 43,
            "(Neo4j offline — showing direct links only)",
            "",
            f"FROM: {from_node['region']} / {from_node['district']}",
        ]
        for p in from_node["nearby_paths"][:3]:
            lines.append(f"  → {p}")
        lines += ["", f"TO: {to_node['region']} / {to_node['district']}"]
        return "\n".join(lines)

    # ── Causal history query ───────────────────────────────────────────────
    history_m = re.search(
        r'(?:history(?:\s+of)?|decisions?(?:\s+in)?|why|caused|what (?:changed|shaped)|shaped)\s+(?:the\s+)?(.+)',
        query
    )
    if history_m:
        hist_q  = history_m.group(1).strip()
        target  = keyword_match(hist_q)
        if not target:
            return (
                f"PROMETHEUS HISTORY — Location not found: '{hist_q}'\n"
                "Run jarvis_grid() for the full map."
            )
        nid = node_id(target)
        try:
            records = neo4j_run(
                "MATCH (d:Decision)-[:AFFECTS_DISTRICT]->(n:GridNode {id: $id}) "
                "RETURN d.id AS id, d.decision AS decision, d.rationale AS rationale, "
                "       d.timestamp AS ts, d.system_affected AS system "
                "ORDER BY d.timestamp DESC LIMIT 10",
                {"id": nid}
            )
            if records:
                lines = [
                    f"PROMETHEUS HISTORY — {target['region']} / {target['district']}",
                    "═" * 43,
                    f"{len(records)} decision(s) shaped this district:",
                    "",
                ]
                for r in records:
                    ts = (r.get("ts") or "")[:16]
                    lines += [
                        f"[{r['id']}]  {ts}  [{r.get('system','?')}]",
                        f"  DECIDED: {(r.get('decision') or '')[:120]}",
                        f"  BECAUSE: {(r.get('rationale') or '')[:120]}",
                        "",
                    ]
                lines.append("Causal chain: jarvis_neo4j(action='traverse', node_id='<id>', direction='out')")
                return "\n".join(lines)
            else:
                return (
                    f"PROMETHEUS HISTORY — {target['district']}\n"
                    "No decisions linked to this district yet.\n"
                    "Use jarvis_log with decisions mentioning this region to build causal history."
                )
        except Exception:
            return (
                f"PROMETHEUS HISTORY — Neo4j offline\n"
                f"Cannot retrieve decision history for: {target['district']}"
            )

    # ── Empty query — show full map ────────────────────────────────────────
    if not query:
        lines = [
            "YOU ARE AT: The Grid — Entrance",
            "═" * 43,
            "THE GRID v0 — Text Navigation Layer",
            "JARVIS is your guide. Ask where you want to go.",
            "",
            "KNOWN LOCATIONS:",
        ]
        seen_regions: set = set()
        for node in GRID_CANON:
            if node["region"] not in seen_regions:
                lines.append("")
                lines.append(f"  [{node['region']}]")
                seen_regions.add(node["region"])
            lines.append(f"    • {node['district']}  →  intake/recycle/{node['file']}")
        lines += [
            "",
            "SUGGESTED NAVIGATION:",
            "  jarvis_grid(query='codex authority')",
            "  jarvis_grid(query='route from codex authority to grid design bible')",
            "  jarvis_grid(query='history of routing gate')",
            "  jarvis_grid(query='why governed workflow')",
            "  jarvis_grid(query='heartbeat watcher')",
        ]
        return "\n".join(lines)

    # ── Keyword match ──────────────────────────────────────────────────────
    best_node = keyword_match(query)

    if not best_node:
        lines = [
            f"JARVIS GRID — No location found for: '{query}'",
            "═" * 43,
            "Known regions:",
        ]
        for node in GRID_CANON:
            lines.append(f"  • {node['region']} / {node['district']}")
        lines += ["", "Try: codex, grid, workflow, heartbeat, stats, substrates, governed"]
        return "\n".join(lines)

    excerpt = ""
    canon_file = INTAKE_RECYCLE / best_node["file"]
    if canon_file.exists():
        try:
            content_lines = [
                ln.strip() for ln in canon_file.read_text(encoding="utf-8").splitlines()
                if ln.strip() and not ln.startswith("#")
            ][:2]
            excerpt = " ".join(content_lines)[:140]
        except Exception:
            pass

    lines = [
        f"YOU ARE ENTERING: {best_node['region']} / {best_node['district']}",
        "═" * 43,
    ]
    if excerpt:
        lines += [f"  {excerpt}", ""]

    # Try Neo4j for live neighbor paths
    nid = node_id(best_node)
    neo4j_paths: list[str] = []
    try:
        records = neo4j_run(
            "MATCH (n:GridNode {id: $id})-[:ROUTES_TO]->(m:GridNode) "
            "RETURN m.district AS district, m.region AS region, m.file AS file LIMIT 6",
            {"id": nid}
        )
        neo4j_paths = [
            f"{r['district']} ({r['region']})  →  {r['file']}"
            for r in records
        ]
    except Exception:
        pass

    lines.append("NEARBY PATHS:")
    if neo4j_paths:
        for p in neo4j_paths:
            lines.append(f"  → {p}")
        lines.append("  [live from Neo4j graph]")
    else:
        for path in best_node["nearby_paths"]:
            lines.append(f"  → {path}")

    lines += ["", "WARNINGS:"]
    for warning in best_node["warnings"]:
        lines.append(f"  ⚠ {warning}")
    lines += ["", "SUGGESTED ASCENT:"]
    lines.append(f"  ↑ {best_node['suggested_ascent']}")
    lines += [
        "",
        f"CANON SOURCE: intake/recycle/{best_node['file']}",
        f"ODIN: jarvis_grid(query='route from {best_node['district'].lower()} to ...')",
        f"IMAGE: jarvis_image(action='prompt', district='{best_node['district'].lower()}')",
    ]
    return "\n".join(lines)


async def handle_jarvis_vision(args: dict) -> str:
    import base64 as _b64

    question = (args.get("question") or "").strip() or (
        "Describe this image in detail. What does it show? "
        "Is anything here relevant to AI governance, software architecture, or system design?"
    )
    model     = (args.get("model") or "").strip()
    image_b64 = (args.get("image_base64") or "").strip()

    if not image_b64:
        image_path = (args.get("image_path") or "").strip()
        if not image_path:
            return "jarvis_vision requires image_path or image_base64."
        p = Path(image_path)
        if not p.exists():
            return f"Image file not found: {image_path}"
        image_b64 = _b64.b64encode(p.read_bytes()).decode()

    if not model:
        model = detect_vision_model()
    if not model:
        return "\n".join([
            "JARVIS VISION — No vision model available",
            "═" * 43,
            "Pull a vision model via Ollama to enable image analysis:",
            "  ollama pull moondream    (~1.7B, ~1 GB — fast, edge-optimised)",
            "  ollama pull llava:7b     (~7B,   ~4.7 GB — higher quality)",
            "Then retry: jarvis_vision(image_path='path/to/image.png')",
        ])

    try:
        answer = ollama_vision(image_b64, question, model)
        return "\n".join([
            f"JARVIS VISION — {model}",
            "═" * 43,
            f"Q: {question[:120]}",
            "",
            answer,
        ])
    except Exception as e:
        return f"JARVIS VISION error [{model}]: {e}"


async def handle_jarvis_image(args: dict) -> str:
    import base64 as _b64

    action        = (args.get("action") or "prompt").strip()
    district_q    = (args.get("district") or "").strip().lower()
    region_q      = (args.get("region")   or "").strip().lower()
    custom_prompt = (args.get("custom_prompt") or "").strip()
    width         = max(256, min(int(args.get("width")  or 512), 1024))
    height        = max(256, min(int(args.get("height") or 512), 1024))

    if action == "list_models":
        vision = detect_vision_model()
        return "\n".join([
            "JARVIS MULTIMODAL — Status",
            "═" * 43,
            f"Vision model:  {vision or 'none  (pull moondream or llava)'}",
            f"Image gen URL: {IMAGE_GEN_URL}",
            "Image gen:     configure via IMAGE_GEN_URL in .env (SD-compatible endpoint)",
        ])

    # Find target Grid node by keyword
    target_node = None
    if district_q:
        best_score = 0
        q_words    = set(district_q.split())
        for node in GRID_CANON:
            score = sum(1 for kw in node["keywords"] if kw in district_q)
            if node["file"].replace("-", " ").replace(".md", "") in district_q:
                score += 3
            region_words   = set(node["region"].lower().split()) - {"the"}
            district_words = set(node["district"].lower().split())
            score += 2 * len(q_words & (region_words | district_words))
            if score > best_score:
                best_score  = score
                target_node = node

    # Region-level card — build a synthetic node from GRID_REGION_MOODS
    if not target_node and region_q:
        matched_region = None
        for region_name in GRID_REGION_MOODS:
            if region_q in region_name.lower() or region_name.lower().replace("the ", "") in region_q:
                matched_region = region_name
                break
        if matched_region:
            slug = matched_region.lower().replace(" ", "-").replace("the-", "")
            target_node = {
                "file":     f"{slug}-region.md",
                "region":   matched_region,
                "district": matched_region.replace("The ", ""),
                "keywords": matched_region.lower().split(),
            }

    if not target_node and not custom_prompt:
        regions = ", ".join(r.replace("The ", "").lower() for r in GRID_REGION_MOODS)
        return (
            "jarvis_image requires district=, region=, or custom_prompt=.\n"
            f"Regions: {regions}\n"
            "Example: jarvis_image(action='generate', region='signal spire')"
        )

    if custom_prompt:
        prompt   = custom_prompt
        negative = TRON_NEGATIVE
    else:
        prompt, negative = build_grid_image_prompt(target_node)

    if action == "prompt":
        lines = ["JARVIS IMAGE — Prompt Builder", "═" * 43]
        if target_node:
            lines.append(f"District: {target_node['region']} / {target_node['district']}")
            lines.append("")
        lines += [
            "PROMPT:",
            f"  {prompt}",
            "",
            "NEGATIVE:",
            f"  {negative}",
            "",
            f"Generate: jarvis_image(action='generate', district='{district_q or 'your-district'}')",
            f"Requires: SD WebUI at {IMAGE_GEN_URL}  (or set IMAGE_GEN_URL in .env)",
        ]
        return "\n".join(lines)

    elif action == "generate":
        result = call_image_gen(prompt, negative, width, height)
        label  = f"{target_node['region']} / {target_node['district']}" if target_node else "custom"

        if not result["ok"]:
            # SD unavailable — fall back to Pillow concept card
            if target_node:
                card_path = generate_concept_card(target_node)
            else:
                card_path = None

            if card_path:
                return "\n".join([
                    "JARVIS IMAGE — Concept Card (SD unavailable)",
                    "═" * 43,
                    f"District: {label}",
                    f"Saved:    {card_path}",
                    f"Gallery:  http://localhost:7777/grid",
                    "",
                    f"SD error: {result['error']}",
                    "To use SD: set IMAGE_GEN_URL in .env (Automatic1111 default: http://localhost:7860)",
                ])
            return "\n".join([
                "JARVIS IMAGE — Generation failed",
                "═" * 43,
                f"Error: {result['error']}",
                f"Endpoint: {IMAGE_GEN_URL}/sdapi/v1/txt2img",
                "",
                "Setup options:",
                "  • Install Automatic1111 SD WebUI — runs at http://localhost:7860",
                "  • Set IMAGE_GEN_URL=<your endpoint> in .env",
                "",
                "Prompt (paste into any image gen tool):",
                f"  {prompt}",
            ])

        GRID_IMAGES_DIR.mkdir(exist_ok=True)
        slug      = (target_node["file"].replace(".md", "") if target_node else "custom")
        img_path  = GRID_IMAGES_DIR / f"{slug}_{now()[:10]}.png"
        img_path.write_bytes(_b64.b64decode(result["image_b64"]))

        return "\n".join([
            "JARVIS IMAGE — Generated",
            "═" * 43,
            f"District: {label}",
            f"Saved:    {img_path}",
            f"Size:     {width}×{height}",
            f"Gallery:  http://localhost:7777/grid",
            "",
            f"Prompt:   {prompt[:160]}...",
        ])

    else:
        return f"Unknown action: {action}\nValid: prompt | generate | list_models"


async def handle_jarvis_neo4j(args: dict) -> str:
    action = args.get("action", "").strip()
    if not action:
        return "action required: query | upsert_node | upsert_edge | traverse | init_god_systems"

    try:
        get_neo4j_driver()
    except Exception as e:
        return (
            f"Neo4j unavailable: {e}\n\n"
            "Setup steps:\n"
            "  1. Open Neo4j Desktop and start a local DBMS\n"
            "  2. Add NEO4J_PASSWORD=<your-password> to C:\\Users\\JB\\jarvis\\.env\n"
            "  3. Optionally set NEO4J_URI / NEO4J_USER (defaults: bolt://localhost:7687 / neo4j)\n"
            "  4. Restart the JARVIS MCP server"
        )

    try:
        if action == "query":
            cypher = args.get("cypher", "").strip()
            if not cypher:
                return "cypher parameter required for action=query"
            records = neo4j_run(cypher, args.get("params") or {})
            if not records:
                return f"Query returned no results.\nCypher: {cypher}"
            lines = [f"NEO4J QUERY — {len(records)} record(s)", "═" * 43]
            for i, r in enumerate(records[:20], 1):
                lines.append(f"[{i}] {json.dumps(r, default=str)}")
            if len(records) > 20:
                lines.append(f"... {len(records) - 20} more rows omitted")
            return "\n".join(lines)

        elif action == "upsert_node":
            label   = (args.get("label") or "Node").strip()
            node_id = args.get("node_id", "").strip()
            if not node_id:
                return "node_id required for action=upsert_node"
            props = dict(args.get("properties") or {})
            props["id"]         = node_id
            props["updated_at"] = now()
            records = neo4j_run(
                f"MERGE (n:{label} {{id: $id}}) SET n += $props RETURN n.id AS id, labels(n) AS labels",
                {"id": node_id, "props": props}
            )
            r = records[0] if records else {}
            return "\n".join([
                "NEO4J UPSERT NODE", "═" * 43,
                f"Node:       {r.get('id','?')} [{', '.join(r.get('labels') or [])}]",
                f"Properties: {json.dumps({k: v for k, v in props.items() if k not in ('id','updated_at')}, default=str)}",
            ])

        elif action == "upsert_edge":
            from_id  = args.get("from_id", "").strip()
            to_id    = args.get("to_id",   "").strip()
            rel_type = (args.get("rel_type") or "RELATES_TO").upper().replace(" ", "_")
            if not from_id or not to_id:
                return "from_id and to_id required for action=upsert_edge"
            props = dict(args.get("properties") or {})
            props["updated_at"] = now()
            records = neo4j_run(
                f"MATCH (a {{id: $from_id}}), (b {{id: $to_id}}) "
                f"MERGE (a)-[r:{rel_type}]->(b) SET r += $props "
                f"RETURN a.id AS from_id, type(r) AS rel, b.id AS to_id",
                {"from_id": from_id, "to_id": to_id, "props": props}
            )
            if not records:
                return (
                    f"Edge not created — nodes not found.\n"
                    f"Verify '{from_id}' and '{to_id}' exist (action=query or upsert_node first)."
                )
            r = records[0]
            return "\n".join([
                "NEO4J UPSERT EDGE", "═" * 43,
                f"{r['from_id']} -[{r['rel']}]-> {r['to_id']}",
            ])

        elif action == "traverse":
            node_id   = args.get("node_id", "").strip()
            if not node_id:
                return "node_id required for action=traverse"
            depth     = max(1, min(int(args.get("depth") or 1), 4))
            direction = args.get("direction", "both")
            if direction == "out":
                pattern = f"-[*1..{depth}]->"
            elif direction == "in":
                pattern = f"<-[*1..{depth}]-"
            else:
                pattern = f"-[*1..{depth}]-"
            records = neo4j_run(
                f"MATCH (n {{id: $id}}){pattern}(m) "
                f"RETURN DISTINCT m.id AS id, labels(m) AS labels LIMIT 50",
                {"id": node_id}
            )
            if not records:
                return f"No neighbors found for '{node_id}' (depth={depth}, direction={direction})."
            lines = [f"NEO4J TRAVERSE — '{node_id}' depth={depth} [{direction}]", "═" * 43]
            for r in records:
                lines.append(f"  {r.get('id','?')} [{', '.join(r.get('labels') or [])}]")
            return "\n".join(lines)

        elif action == "init_god_systems":
            chaos       = load_chaos()
            god_systems = chaos.get("god_systems", {})
            if not god_systems:
                return "No God Systems found in chaos_seed.json."
            pipeline  = chaos.get("pipeline", {}).get("order", [])
            parallel  = chaos.get("pipeline", {}).get("parallel", [])
            forbidden = chaos.get("interaction_graph", {}).get("forbidden_edges", [])

            nodes_written = edges_written = 0

            for name, data in god_systems.items():
                neo4j_run(
                    "MERGE (n:GodSystem {id: $id}) SET n += $props",
                    {"id": name, "props": {
                        "id":          name,
                        "tier":        data.get("tier", ""),
                        "function":    data.get("function", data.get("role", "")),
                        "cannot":      json.dumps(data.get("cannot", [])),
                        "always_active": data.get("always_active", False),
                        "updated_at":  now(),
                    }}
                )
                nodes_written += 1

            for i in range(len(pipeline) - 1):
                a, b = pipeline[i], pipeline[i + 1]
                if a in god_systems and b in god_systems:
                    neo4j_run(
                        "MATCH (a:GodSystem {id: $a}), (b:GodSystem {id: $b}) "
                        "MERGE (a)-[:PIPELINE_NEXT {order: $order}]->(b)",
                        {"a": a, "b": b, "order": i}
                    )
                    edges_written += 1

            for sys_name in parallel:
                if sys_name in god_systems and "ODIN" in god_systems:
                    neo4j_run(
                        "MATCH (a:GodSystem {id: $a}), (b:GodSystem {id: $b}) "
                        "MERGE (a)-[:PARALLEL_WITH]->(b)",
                        {"a": "ODIN", "b": sys_name}
                    )
                    edges_written += 1

            for edge in forbidden:
                if len(edge) == 2 and edge[0] in god_systems and edge[1] in god_systems:
                    neo4j_run(
                        "MATCH (a:GodSystem {id: $a}), (b:GodSystem {id: $b}) "
                        "MERGE (a)-[:FORBIDDEN {reason: 'Gold Law constraint'}]->(b)",
                        {"a": edge[0], "b": edge[1]}
                    )
                    edges_written += 1

            return "\n".join([
                "NEO4J INIT — God Systems", "═" * 43,
                f"Nodes upserted: {nodes_written}",
                f"Edges upserted: {edges_written}",
                f"  Pipeline:  {' → '.join(pipeline)}",
                f"  Parallel:  {', '.join(parallel)}",
                f"  Forbidden: {len(forbidden)} edge(s)",
                "✓ JARVIS knowledge graph seeded",
                "Next: jarvis_neo4j(action='traverse', node_id='ERIS') to verify",
            ])

        elif action == "init_grid":
            result = neo4j_seed_grid()
            lines = [
                "NEO4J INIT — Grid Nodes", "═" * 43,
                f"GridNodes upserted: {result['nodes']}",
                f"Edges upserted:     {result['edges']}",
                "  (:GridNode)-[:ROUTES_TO]->(:GridNode)",
                "  (:GodSystem)-[:GOVERNS]->(:GridNode)",
                "✓ Grid graph seeded",
                "Next: jarvis_grid(query='route from codex authority to grid design bible')",
            ]
            return "\n".join(lines)

        else:
            return f"Unknown action: {action}\nValid: query | upsert_node | upsert_edge | traverse | init_god_systems | init_grid"

    except Exception as e:
        return f"Neo4j error [{action}]: {e}"


async def handle_jarvis_gemini_handoff(args: dict) -> str:
    task       = args.get("task", "").strip()
    task_type  = args.get("task_type", "ideation")
    context    = args.get("context", "").strip()
    topic_slug = args.get("topic_slug", "task")

    if not task:
        return "task is required. Describe what you want Gemini to do."

    date_str  = now()[:10]
    safe_slug = "".join(c if c.isalnum() or c == "-" else "-" for c in topic_slug.lower())[:40]
    filename  = f"{date_str}_gemini_{safe_slug}.md"
    intake_path = BASE_DIR / "intake" / "gemini" / filename

    aizen_intros = {
        "ideation":       "You are Aizen — ideation engine. Generate novel ideas and strategic directions.",
        "interpretation": "You are Aizen — interpreter. Analyze and explain the following with depth and nuance.",
        "concept":        "You are Aizen — concept architect. Build a structured concept or design around the following.",
        "brainstorm":     "You are Aizen — brainstorm facilitator. Produce a broad set of possibilities without filtering.",
    }
    system_line = aizen_intros.get(task_type, aizen_intros["ideation"])

    prompt_block = f"{system_line}\n\nTask: {task}"
    if context:
        prompt_block += f"\n\nContext:\n{context}"

    intake_content = f"""# Gemini Handoff — {topic_slug}

Source: Gemini (Aizen)
Date: {date_str}
Task type: {task_type}
Requested action: review

## Task

{task}
"""
    if context:
        intake_content += f"\n## Context\n\n{context}\n"

    intake_content += f"""
## Gemini Prompt

```
{prompt_block}
```

## Suggested Next Step

1. Paste the prompt above into Gemini (or invoke via mcp__gemini__gemini-query / gemini-brainstorm).
2. Review output against Gold Law before promoting to code, memory, or decisions.
3. Move this file to intake/processed/ once handled.
4. Copy reusable patterns to intake/recycle/.
"""

    try:
        intake_path.write_text(intake_content, encoding="utf-8")
    except Exception as e:
        return f"Failed to write intake file: {e}"

    return "\n".join([
        f"GEMINI HANDOFF — {task_type.upper()}",
        "=" * 40,
        f"Intake file: intake/gemini/{filename}",
        "",
        "Gemini prompt ready:",
        "─" * 40,
        prompt_block,
        "─" * 40,
        "",
        "Next: paste prompt into Gemini or call mcp__gemini__gemini-query.",
        "Review output against Gold Law before promoting.",
    ])


TOOL_HANDLERS = {
    "jarvis_status":     handle_jarvis_status,
    "jarvis_entropy":    handle_jarvis_entropy,
    "jarvis_god_system": handle_jarvis_god_system,
    "jarvis_end":        handle_jarvis_end,
    "jarvis_log":        handle_jarvis_log,
    "jarvis_overlap":    handle_jarvis_overlap,
    "jarvis_sessions":   handle_jarvis_sessions,
    "jarvis_recall":     handle_jarvis_recall,
    "jarvis_repo_sync":  handle_jarvis_repo_sync,
    "jarvis_stats":      handle_jarvis_stats,
    "jarvis_grid":            handle_jarvis_grid,
    "jarvis_vision":          handle_jarvis_vision,
    "jarvis_image":           handle_jarvis_image,
    "jarvis_neo4j":           handle_jarvis_neo4j,
    "jarvis_gemini_handoff":  handle_jarvis_gemini_handoff,
}


async def dispatch(method: str, params: dict) -> Any:
    if method == "initialize":
        return {
            "protocolVersion": "2024-11-05",
            "capabilities": {"tools": {}},
            "serverInfo": {"name": "JARVIS", "version": "1.0"}
        }
    if method == "tools/list":
        return {"tools": TOOLS}
    if method == "tools/call":
        name    = params.get("name")
        args    = params.get("arguments", {})
        handler = TOOL_HANDLERS.get(name)
        if not handler:
            raise ValueError(f"Unknown tool: {name}")
        result = await handler(args)
        return {"content": [{"type": "text", "text": result}]}
    raise ValueError(f"Unknown method: {method}")


app = FastAPI(title="JARVIS MCP Server", version="1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    chaos = load_chaos()
    return {
        "system":         "JARVIS MCP Server",
        "version":        "1.0",
        "god_systems":    len(chaos.get("god_systems", {})),
        "tools":          len(TOOLS),
        "endpoints":      {"/sse": "SSE transport", "/rpc": "JSON-RPC", "/health": "health check"}
    }


@app.get("/health")
async def health():
    chaos   = load_chaos()
    entropy = compute_entropy_vector(chaos)
    return {
        "status":       "running",
        "eris_entropy": entropy["score"],
        "eris_status":  entropy["status"],
        "chaos_loaded": bool(chaos),
        "god_systems":  len(chaos.get("god_systems", {})),
        "supabase":     supabase_enabled(),
        "timestamp":    now()
    }


@app.post("/rpc")
async def rpc_endpoint(request: Request):
    body = await request.json()
    if isinstance(body, list):
        results = []
        for req in body:
            results.append(await _handle_rpc(req))
        return JSONResponse(results)
    return JSONResponse(await _handle_rpc(body))


async def _handle_rpc(req: dict) -> dict:
    try:
        result = await dispatch(req.get("method", ""), req.get("params", {}))
        return {"jsonrpc": "2.0", "id": req.get("id"), "result": result}
    except Exception as e:
        return {"jsonrpc": "2.0", "id": req.get("id"), "error": {"code": -32000, "message": str(e)}}


@app.get("/sse")
async def sse_endpoint(request: Request):
    async def event_stream():
        yield f"event: endpoint\ndata: {json.dumps({'uri': '/rpc'})}\n\n"
        while True:
            if await request.is_disconnected():
                break
            yield f"event: ping\ndata: {json.dumps({'ts': now()})}\n\n"
            await asyncio.sleep(15)
    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"}
    )


_GALLERY_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>JARVIS GRID — Digital Highway</title>
<style>
:root{--cyan:#00e5ff;--dim:#004a60;--glow:#00e5ff55;--bg:#000008;}
*{box-sizing:border-box;margin:0;padding:0;}
html,body{width:100%;height:100%;overflow:hidden;background:var(--bg);font-family:'Courier New',monospace;color:var(--cyan);}

/* scanline overlay */
body::after{content:'';position:fixed;inset:0;background:repeating-linear-gradient(0deg,transparent,transparent 2px,rgba(0,0,0,.07) 2px,rgba(0,0,0,.07) 4px);pointer-events:none;z-index:200;}

/* perspective floor */
.floor{position:fixed;bottom:0;left:0;right:0;height:52vh;
  background:linear-gradient(90deg,var(--dim) 1px,transparent 1px) center/100px 100px,
             linear-gradient(0deg,var(--dim) 1px,transparent 1px) center/100px 100px;
  transform:perspective(500px) rotateX(72deg);transform-origin:bottom center;opacity:.45;}
.floor::after{content:'';position:absolute;inset:0;background:linear-gradient(to top,transparent 0%,var(--bg) 65%);}

/* horizon glow */
.horizon{position:fixed;left:0;right:0;top:46vh;height:1px;
  background:var(--dim);box-shadow:0 0 60px 12px var(--glow),0 0 140px 30px #001a2e;}

/* corner brackets */
.c{position:fixed;width:22px;height:22px;z-index:150;}
.c::before,.c::after{content:'';position:absolute;background:var(--cyan);}
.c::before{width:100%;height:2px;top:0;}.c::after{width:2px;height:100%;}
.tl{top:10px;left:10px;}.tr{top:10px;right:10px;transform:scaleX(-1);}
.bl{bottom:10px;left:10px;transform:scaleY(-1);}.br{bottom:10px;right:10px;transform:scale(-1);}

/* HUD */
.hud{position:fixed;top:0;left:0;right:0;padding:14px 28px;
  display:flex;justify-content:space-between;align-items:center;
  border-bottom:1px solid #001a2e;background:linear-gradient(to bottom,#00000f,transparent);z-index:100;
  font-size:.65rem;letter-spacing:.28em;}
.hud-r{color:var(--dim);}

/* highway stage */
.stage{position:fixed;inset:0;display:flex;align-items:center;justify-content:center;
  perspective:1100px;perspective-origin:50% 42%;}
.lane{display:flex;align-items:center;transform-style:preserve-3d;transition:none;}

/* cards */
.card{position:relative;flex-shrink:0;width:300px;margin:0 28px;cursor:pointer;
  transform-style:preserve-3d;transition:transform .55s cubic-bezier(.4,0,.2,1),opacity .55s ease,filter .55s ease;}
.card img{display:block;width:100%;aspect-ratio:1;object-fit:cover;
  border:1px solid var(--dim);transition:all .4s ease;}
/* corner brackets on card */
.card::before,.card::after{content:'';position:absolute;width:16px;height:16px;z-index:2;pointer-events:none;
  border-style:solid;border-color:var(--dim);transition:border-color .3s;}
.card::before{top:-1px;left:-1px;border-width:2px 0 0 2px;}
.card::after{bottom:-1px;right:-1px;border-width:0 2px 2px 0;}
.card .lbl{position:absolute;bottom:0;left:0;right:0;padding:28px 10px 8px;
  background:linear-gradient(to top,rgba(0,0,0,.9),transparent);
  font-size:.55rem;letter-spacing:.2em;color:var(--dim);text-align:center;opacity:0;transition:opacity .3s;}

/* states */
.card.active{transform:translateZ(80px) scale(1.1);z-index:10;}
.card.active img{border-color:var(--cyan);box-shadow:0 0 28px var(--glow),0 0 80px #00e5ff18;filter:brightness(1) saturate(1.5);}
.card.active::before,.card.active::after{border-color:var(--cyan);}
.card.active .lbl{opacity:1;color:var(--cyan);}
.card.p1,.card.n1{transform:translateZ(-60px) scale(.82);opacity:.55;filter:brightness(.6);}
.card.p2,.card.n2{transform:translateZ(-180px) scale(.62);opacity:.3;filter:brightness(.4);}
.card.p3,.card.n3{transform:translateZ(-320px) scale(.44);opacity:.14;filter:brightness(.3);}
.card.far{transform:translateZ(-460px) scale(.3);opacity:.05;filter:brightness(.2);}
.card.hide{opacity:0;pointer-events:none;transform:translateZ(-600px) scale(.2);}

/* nav */
.nav{position:fixed;top:50%;transform:translateY(-50%);z-index:100;
  background:none;border:none;color:var(--dim);font-size:1.2rem;letter-spacing:.1em;
  cursor:pointer;padding:14px 22px;transition:color .2s;}
.nav:hover{color:var(--cyan);}
.navL{left:12px;}.navR{right:12px;}

/* node info */
.info{position:fixed;bottom:28px;left:50%;transform:translateX(-50%);
  text-align:center;z-index:100;pointer-events:none;min-width:340px;}
.info .dn{font-size:.85rem;letter-spacing:.32em;}
.info .sq{font-size:.55rem;letter-spacing:.18em;color:var(--dim);margin-top:6px;}

/* light trails */
@keyframes tr{0%{transform:translateX(-110vw);opacity:0;}8%{opacity:1;}92%{opacity:1;}100%{transform:translateX(110vw);opacity:0;}}
.trail{position:fixed;height:1px;background:linear-gradient(90deg,transparent,var(--cyan),transparent);
  pointer-events:none;z-index:1;animation:tr linear infinite;}
</style>
</head>
<body>

<div class="floor"></div>
<div class="horizon"></div>
<div class="c tl"></div><div class="c tr"></div><div class="c bl"></div><div class="c br"></div>

<div class="hud">
  <span>&#9632;&nbsp; JARVIS GRID &mdash; DIGITAL HIGHWAY</span>
  <span class="hud-r" id="hcount">&#8213;</span>
</div>

<div class="stage"><div class="lane" id="lane"></div></div>

<button class="nav navL" onclick="move(-1)">&#9664;</button>
<button class="nav navR" onclick="move(1)">&#9654;</button>

<div class="info">
  <div class="dn" id="idn">&nbsp;</div>
  <div class="sq" id="isq">&nbsp;</div>
</div>

<script>
let files=[], cur=0, timer;

function slug(name){
  return name.replace(/\\.png$/,'').replace(/_\\d{4}-\\d{2}-\\d{2}$/,'').replace(/[-_]/g,' ').toUpperCase();
}

function cls(rel){
  if(rel===0)  return 'card active';
  if(rel===1)  return 'card n1';
  if(rel===-1) return 'card p1';
  if(rel===2)  return 'card n2';
  if(rel===-2) return 'card p2';
  if(rel===3)  return 'card n3';
  if(rel===-3) return 'card p3';
  if(Math.abs(rel)===4) return 'card far';
  return 'card hide';
}

function render(){
  const lane=document.getElementById('lane');
  lane.innerHTML=files.map((f,i)=>{
    const rel=i-cur;
    const isActive=rel===0;
    const nodeSlug=f.name.replace(/\\.png$/,'').replace(/_\\d{4}-\\d{2}-\\d{2}$/,'');
    const onclick=isActive?`window.location='/grid/node/${nodeSlug}'`:`activate(${i})`;
    return `<div class="${cls(rel)}" onclick="${onclick}" style="cursor:${isActive?'pointer':'default'}">
      <img src="/grid/img/${f.name}" alt="${f.name}" loading="lazy">
      <div class="lbl">${slug(f.name)}</div>
    </div>`;
  }).join('');
  const f=files[cur];
  if(f){
    document.getElementById('idn').textContent=slug(f.name);
    document.getElementById('isq').textContent=`${cur+1} / ${files.length}  —  CLICK TO ENTER DISTRICT  •  ←→ NAVIGATE`;
  }
  document.getElementById('hcount').textContent=`${files.length} NODE${files.length!==1?'S':''}`;
}

function activate(i){
  if(i===cur){ return; }
  cur=i; render(); resetTimer();
}

function move(d){
  if(!files.length) return;
  cur=(cur+d+files.length)%files.length;
  render(); resetTimer();
}

function resetTimer(){
  clearInterval(timer);
  timer=setInterval(()=>move(1),5000);
}

async function poll(){
  try{
    const r=await fetch('/grid/manifest');
    const d=await r.json();
    if(d.length!==files.length){ files=d; if(cur>=files.length)cur=0; render(); }
  }catch(e){}
}

document.addEventListener('keydown',e=>{
  if(e.key==='ArrowLeft'||e.key==='a') move(-1);
  if(e.key==='ArrowRight'||e.key==='d') move(1);
});

function spawnTrail(){
  const t=document.createElement('div');
  t.className='trail';
  t.style.top=Math.random()*100+'vh';
  t.style.width=(60+Math.random()*220)+'px';
  const dur=3+Math.random()*7;
  t.style.animationDuration=dur+'s';
  t.style.animationDelay=Math.random()*3+'s';
  t.style.opacity=.15+Math.random()*.35;
  document.body.appendChild(t);
  setTimeout(()=>t.remove(),(dur+3)*1000);
}

(async()=>{
  const r=await fetch('/grid/manifest');
  files=await r.json();
  render(); resetTimer();
  setInterval(poll,3000);
  setInterval(spawnTrail,900);
  for(let i=0;i<6;i++) spawnTrail();
})();
</script>
</body>
</html>"""


def _node_page_html(node: dict, img_src: str) -> str:
    district  = node.get("district", "UNKNOWN").upper()
    region    = node.get("region",   "THE GRID").upper()
    warnings  = node.get("warnings", [])
    nearby    = node.get("nearby_paths", [])
    ascent    = node.get("suggested_ascent", "")
    keywords  = node.get("keywords", [])

    def nearby_link(path_str: str) -> str:
        parts     = path_str.split(" — ", 1)
        raw_slug  = parts[0].strip().replace(".md", "")
        desc      = parts[1].strip() if len(parts) > 1 else ""
        label     = raw_slug.replace("-", " ").upper()
        return (
            f'<a href="/grid/node/{raw_slug}" class="nlink">'
            f'<span class="nl">{label}</span>'
            f'<span class="nd">{desc}</span>'
            f'</a>'
        )

    nearby_html   = "".join(nearby_link(p) for p in nearby) if nearby else '<span class="none">—</span>'
    warnings_html = "".join(f'<div class="wn">&#9888; {w}</div>' for w in warnings) if warnings else '<span class="none">—</span>'
    kw_html       = "&nbsp;&nbsp;·&nbsp;&nbsp;".join(k.upper() for k in keywords[:8])

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>JARVIS GRID — {district}</title>
<style>
:root{{--cyan:#00e5ff;--dim:#004a60;--glow:#00e5ff55;--warn:#ff9800;--bg:#000008;}}
*{{box-sizing:border-box;margin:0;padding:0;}}
html,body{{width:100%;min-height:100%;background:var(--bg);font-family:'Courier New',monospace;color:var(--cyan);overflow-x:hidden;}}
body::after{{content:'';position:fixed;inset:0;background:repeating-linear-gradient(0deg,transparent,transparent 2px,rgba(0,0,0,.07) 2px,rgba(0,0,0,.07) 4px);pointer-events:none;z-index:200;}}
.floor{{position:fixed;bottom:0;left:0;right:0;height:40vh;
  background:linear-gradient(90deg,var(--dim) 1px,transparent 1px) center/100px 100px,
             linear-gradient(0deg,var(--dim) 1px,transparent 1px) center/100px 100px;
  transform:perspective(500px) rotateX(72deg);transform-origin:bottom center;opacity:.3;}}
.floor::after{{content:'';position:absolute;inset:0;background:linear-gradient(to top,transparent 0%,var(--bg) 70%);}}
.horizon{{position:fixed;left:0;right:0;bottom:38vh;height:1px;background:var(--dim);box-shadow:0 0 40px 8px var(--glow);}}
.c{{position:fixed;width:22px;height:22px;z-index:150;}}
.c::before,.c::after{{content:'';position:absolute;background:var(--cyan);}}
.c::before{{width:100%;height:2px;top:0;}}.c::after{{width:2px;height:100%;}}
.tl{{top:10px;left:10px;}}.tr{{top:10px;right:10px;transform:scaleX(-1);}}
.bl{{bottom:10px;left:10px;transform:scaleY(-1);}}.br{{bottom:10px;right:10px;transform:scale(-1);}}
.hud{{position:fixed;top:0;left:0;right:0;padding:14px 28px;
  display:flex;justify-content:space-between;align-items:center;
  border-bottom:1px solid #001a2e;background:linear-gradient(to bottom,#00000f,transparent);z-index:100;
  font-size:.65rem;letter-spacing:.28em;}}
.back{{color:var(--dim);text-decoration:none;transition:color .2s;}}
.back:hover{{color:var(--cyan);}}
.wrap{{position:relative;z-index:10;max-width:900px;margin:0 auto;padding:80px 32px 80px;}}
.hero{{display:flex;gap:40px;align-items:flex-start;margin-bottom:48px;}}
.hero-img{{flex-shrink:0;width:320px;}}
.hero-img img{{display:block;width:100%;aspect-ratio:1;object-fit:cover;
  border:1px solid var(--cyan);box-shadow:0 0 40px var(--glow),0 0 100px #00e5ff18;}}
.hero-info{{flex:1;padding-top:8px;}}
.region{{font-size:.6rem;letter-spacing:.3em;color:var(--dim);margin-bottom:10px;}}
.district{{font-size:1.5rem;letter-spacing:.25em;line-height:1.25;margin-bottom:20px;}}
.sep{{height:1px;background:var(--dim);margin:20px 0;}}
.kw{{font-size:.55rem;letter-spacing:.15em;color:#002a3a;line-height:2;}}
.section{{margin-bottom:36px;}}
.section h3{{font-size:.6rem;letter-spacing:.3em;color:var(--dim);border-bottom:1px solid #001a2e;padding-bottom:8px;margin-bottom:16px;}}
.nlink{{display:block;padding:10px 14px;border:1px solid #001a2e;margin-bottom:8px;
  text-decoration:none;transition:border-color .2s,background .2s;}}
.nlink:hover{{border-color:var(--cyan);background:#00050f;}}
.nl{{display:block;font-size:.65rem;letter-spacing:.2em;color:var(--cyan);}}
.nd{{display:block;font-size:.55rem;letter-spacing:.1em;color:var(--dim);margin-top:3px;}}
.wn{{font-size:.65rem;letter-spacing:.12em;color:var(--warn);padding:8px 0;border-bottom:1px solid #001a2e;line-height:1.5;}}
.ascent{{font-size:.7rem;letter-spacing:.15em;color:var(--cyan);padding:12px 16px;
  border-left:2px solid var(--cyan);background:#00050f;line-height:1.6;}}
.none{{font-size:.6rem;color:#002030;letter-spacing:.15em;}}
@keyframes tr{{0%{{transform:translateX(-110vw);opacity:0;}}8%{{opacity:1;}}92%{{opacity:1;}}100%{{transform:translateX(110vw);opacity:0;}}}}
.trail{{position:fixed;height:1px;background:linear-gradient(90deg,transparent,var(--cyan),transparent);pointer-events:none;z-index:1;animation:tr linear infinite;}}
</style>
</head>
<body>
<div class="floor"></div>
<div class="horizon"></div>
<div class="c tl"></div><div class="c tr"></div><div class="c bl"></div><div class="c br"></div>
<div class="hud">
  <a href="/grid" class="back">&#9664;&nbsp; HIGHWAY</a>
  <span style="font-size:.6rem;letter-spacing:.25em;color:var(--dim)">{region}</span>
</div>
<div class="wrap">
  <div class="hero">
    {'<div class="hero-img"><img src="' + img_src + '" alt="' + district + '"></div>' if img_src else ''}
    <div class="hero-info">
      <div class="region">{region}</div>
      <div class="district">{district}</div>
      <div class="sep"></div>
      <div class="kw">{kw_html}</div>
    </div>
  </div>
  <div class="section">
    <h3>&#9632; NEARBY PATHS</h3>
    {nearby_html}
  </div>
  <div class="section">
    <h3>&#9650; WARNINGS</h3>
    {warnings_html}
  </div>
  {'<div class="section"><h3>&#8679; SUGGESTED ASCENT</h3><div class="ascent">' + ascent + '</div></div>' if ascent else ''}
</div>
<script>
function spawnTrail(){{
  const t=document.createElement('div');t.className='trail';
  t.style.top=Math.random()*100+'vh';t.style.width=(60+Math.random()*200)+'px';
  const d=3+Math.random()*7;t.style.animationDuration=d+'s';
  t.style.animationDelay=Math.random()*3+'s';t.style.opacity=.1+Math.random()*.25;
  document.body.appendChild(t);setTimeout(()=>t.remove(),(d+3)*1000);
}}
for(let i=0;i<5;i++) spawnTrail();
setInterval(spawnTrail,1200);
</script>
</body>
</html>"""


@app.get("/grid", response_class=HTMLResponse)
async def gallery_page():
    return HTMLResponse(content=_GALLERY_HTML)


@app.get("/grid/manifest")
async def gallery_manifest():
    GRID_IMAGES_DIR.mkdir(exist_ok=True)
    files = sorted(
        [{"name": p.name, "size": p.stat().st_size, "mtime": p.stat().st_mtime}
         for p in GRID_IMAGES_DIR.glob("*.png")],
        key=lambda x: x["mtime"],
        reverse=True,
    )
    return JSONResponse(files)


@app.get("/grid/node/{node_slug}", response_class=HTMLResponse)
async def node_page(node_slug: str):
    # Find matching GRID_CANON entry
    node = next((n for n in GRID_CANON if n["file"].replace(".md", "") == node_slug), None)
    if node is None:
        # Synthetic region node — build minimal entry from GRID_REGION_MOODS
        matched_region = next(
            (r for r in GRID_REGION_MOODS if node_slug in r.lower().replace(" ", "-").replace("the-", "")),
            None,
        )
        if matched_region:
            node = {
                "file":     node_slug + ".md",
                "region":   matched_region,
                "district": matched_region.replace("The ", ""),
                "keywords": matched_region.lower().split(),
                "nearby_paths": [],
                "warnings": [],
                "suggested_ascent": "",
            }
        else:
            return HTMLResponse("<html><body style='background:#000;color:#00e5ff;font-family:monospace;padding:40px'>"
                                f"<p>NODE NOT FOUND: {node_slug}</p>"
                                "<p><a href='/grid' style='color:#004a60'>← HIGHWAY</a></p></body></html>",
                                status_code=404)
    # Find most recent concept card for this node
    img_files = sorted(GRID_IMAGES_DIR.glob(f"{node_slug}_*.png"), reverse=True)
    img_src   = f"/grid/img/{img_files[0].name}" if img_files else ""
    return HTMLResponse(_node_page_html(node, img_src))


@app.get("/grid/img/{filename}")
async def gallery_image(filename: str):
    img_path = GRID_IMAGES_DIR / filename
    if not img_path.exists() or img_path.suffix != ".png":
        return JSONResponse({"error": "not found"}, status_code=404)
    return FileResponse(str(img_path), media_type="image/png")


_LIVE_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>JARVIS — Live Feed</title>
<style>
  @import url('https://fonts.googleapis.com/css2?family=Share+Tech+Mono&family=Orbitron:wght@700;900&display=swap');
  :root{--bg:#020408;--surface:#080f18;--card:#0c1520;--border:#0f2035;--amber:#f5a623;--green:#00ff88;--red:#ff3355;--blue:#0af;--dim:#1e3a52;--text:#4a7a99;--bright:#a0c8e0;--mono:'Share Tech Mono',monospace;--display:'Orbitron',sans-serif;}
  *{box-sizing:border-box;margin:0;padding:0;}
  body{background:var(--bg);color:var(--text);font-family:var(--mono);font-size:11px;height:100vh;display:grid;grid-template-rows:48px 1fr;overflow:hidden;}
  body::before{content:'';position:fixed;inset:0;background:repeating-linear-gradient(0deg,transparent,transparent 2px,rgba(0,0,0,.04) 2px,rgba(0,0,0,.04) 4px);pointer-events:none;z-index:1000;}
  .topbar{background:var(--surface);border-bottom:1px solid var(--border);display:flex;align-items:center;padding:0 20px;gap:20px;}
  .logo{font-family:var(--display);font-size:16px;font-weight:900;letter-spacing:5px;color:var(--amber);text-shadow:0 0 15px rgba(245,166,35,.3);}
  .logo span{color:var(--dim);}
  .live-dot{width:6px;height:6px;border-radius:50%;background:var(--green);box-shadow:0 0 8px var(--green);animation:blink 1.5s infinite;}
  @keyframes blink{0%,100%{opacity:1}50%{opacity:.2}}
  .topbar-right{margin-left:auto;display:flex;align-items:center;gap:16px;font-size:9px;color:var(--dim);letter-spacing:2px;}
  .main{display:grid;grid-template-columns:1fr 320px;gap:1px;background:var(--border);overflow:hidden;}
  .feed-panel{background:var(--bg);display:flex;flex-direction:column;overflow:hidden;}
  .feed-header{background:var(--surface);padding:8px 16px;font-size:8px;letter-spacing:4px;color:var(--dim);border-bottom:1px solid var(--border);display:flex;justify-content:space-between;}
  .feed-scroll{flex:1;overflow-y:auto;padding:12px;display:flex;flex-direction:column;gap:4px;}
  .feed-scroll::-webkit-scrollbar{width:3px;}.feed-scroll::-webkit-scrollbar-thumb{background:var(--border);}
  .entry{display:grid;grid-template-columns:70px 80px 1fr 60px;gap:8px;padding:6px 8px;border-left:2px solid var(--border);background:var(--card);animation:fadeIn .3s ease;align-items:center;}
  @keyframes fadeIn{from{opacity:0;transform:translateX(-8px)}to{opacity:1}}
  .entry.done{border-left-color:var(--green)}.entry.working{border-left-color:var(--amber);animation:pulse-border 1s infinite}.entry.failed{border-left-color:var(--red)}
  @keyframes pulse-border{0%,100%{border-left-color:var(--amber)}50%{border-left-color:rgba(245,166,35,.3)}}
  .entry-time{color:var(--dim);font-size:9px}.entry-action{color:var(--bright);font-size:10px}.entry-file{color:var(--text);font-size:9px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
  .entry-status{font-size:8px;letter-spacing:2px;text-align:right}
  .status-done{color:var(--green)}.status-working{color:var(--amber)}.status-failed{color:var(--red)}
  .sidebar{background:var(--surface);padding:16px;display:flex;flex-direction:column;gap:16px;overflow-y:auto;}
  .card{background:var(--card);border:1px solid var(--border);padding:12px;}
  .card-label{font-size:8px;letter-spacing:4px;color:var(--dim);border-bottom:1px solid var(--border);padding-bottom:6px;margin-bottom:10px;text-transform:uppercase;}
  .stat-row{display:flex;justify-content:space-between;padding:4px 0;border-bottom:1px solid var(--border);font-size:10px;}.stat-row:last-child{border-bottom:none;}
  .stat-k{color:var(--text)}.stat-v.ok{color:var(--green)}.stat-v.warn{color:var(--amber)}.stat-v.err{color:var(--red)}
  .activity-bar{display:flex;gap:2px;align-items:flex-end;height:40px;}
  .bar{flex:1;background:var(--amber);opacity:.6;min-height:2px;transition:height .3s ease;}
  .empty-state{color:var(--dim);font-size:9px;letter-spacing:2px;text-align:center;padding:40px 20px;line-height:2;}
  .cursor{display:inline-block;width:8px;height:12px;background:var(--amber);animation:cursor-blink 1s step-end infinite;vertical-align:middle;margin-left:4px;}
  @keyframes cursor-blink{0%,100%{opacity:1}50%{opacity:0}}
  .btn{width:100%;padding:8px;background:transparent;border:1px solid #7a4f0a;color:var(--amber);font-family:var(--mono);font-size:9px;letter-spacing:2px;cursor:pointer;text-align:left;}
  .btn:hover{background:var(--amber);color:var(--bg);}
  .instruction{font-size:9px;line-height:1.8;color:var(--text);}
  .instruction code{color:var(--amber);background:var(--bg);padding:1px 4px;}
  .nav-links{display:flex;gap:8px;flex-wrap:wrap;}
  .nav-link{font-size:9px;letter-spacing:2px;color:var(--dim);text-decoration:none;padding:6px 10px;border:1px solid var(--border);}
  .nav-link:hover{color:var(--amber);border-color:var(--amber);}
</style>
</head>
<body>
<div class="topbar">
  <div class="logo">JARVIS <span>LIVE</span></div>
  <div class="live-dot"></div>
  <span style="font-size:9px;color:var(--dim);letter-spacing:2px">CLAUDE CODE FEED</span>
  <div class="topbar-right">
    <span id="entry-count">0 ENTRIES</span>
    <span id="last-update">—</span>
    <span id="connection-status" style="color:var(--amber)">WAITING</span>
  </div>
</div>
<div class="main">
  <div class="feed-panel">
    <div class="feed-header">
      <span>LIVE FEED</span>
      <span id="feed-status">Connecting to /live_log.json...</span>
    </div>
    <div class="feed-scroll" id="feed">
      <div class="empty-state">Waiting for JARVIS activity<span class="cursor"></span><br><br>PROMETHEUS decisions appear here automatically.<br>POST to /live_log to push custom entries.</div>
    </div>
  </div>
  <div class="sidebar">
    <div class="card">
      <div class="card-label">Session Stats</div>
      <div class="stat-row"><span class="stat-k">Total Actions</span><span class="stat-v ok" id="stat-total">0</span></div>
      <div class="stat-row"><span class="stat-k">Completed</span><span class="stat-v ok" id="stat-done">0</span></div>
      <div class="stat-row"><span class="stat-k">In Progress</span><span class="stat-v warn" id="stat-working">0</span></div>
      <div class="stat-row"><span class="stat-k">Failed</span><span class="stat-v err" id="stat-failed">0</span></div>
      <div class="stat-row"><span class="stat-k">Success Rate</span><span class="stat-v ok" id="stat-rate">—</span></div>
    </div>
    <div class="card">
      <div class="card-label">Activity</div>
      <div class="activity-bar" id="activity-bar">
        <div class="bar" style="height:2px"></div><div class="bar" style="height:2px"></div>
        <div class="bar" style="height:2px"></div><div class="bar" style="height:2px"></div>
        <div class="bar" style="height:2px"></div><div class="bar" style="height:2px"></div>
        <div class="bar" style="height:2px"></div><div class="bar" style="height:2px"></div>
        <div class="bar" style="height:2px"></div><div class="bar" style="height:2px"></div>
      </div>
    </div>
    <div class="card">
      <div class="card-label">Navigate</div>
      <div class="nav-links">
        <a href="/grid" class="nav-link">&#9632; GRID</a>
        <a href="/health" class="nav-link">&#9632; HEALTH</a>
      </div>
    </div>
    <div class="card">
      <div class="card-label">Hook Setup</div>
      <div class="instruction">
        Add to <code>~/.claude/settings.json</code>:<br><br>
        <code>"PostToolUse"</code> hook → POST to<br>
        <code>localhost:7777/live_log</code><br><br>
        Body: <code>{"action":"...","file":"...","status":"done"}</code><br><br>
        PROMETHEUS decisions auto-appear via <code>jarvis_log</code>.
      </div>
    </div>
    <div class="card">
      <div class="card-label">Controls</div>
      <div style="display:flex;flex-direction:column;gap:6px;">
        <button class="btn" onclick="clearFeed()">&#9658; CLEAR FEED</button>
        <button class="btn" onclick="testEntry()">&#9658; TEST ENTRY</button>
      </div>
    </div>
  </div>
</div>
<script>
let entries=[], lastLen=0, activityHistory=new Array(10).fill(0);

async function pollLog(){
  try{
    const r=await fetch('/live_log.json?t='+Date.now());
    if(!r.ok) throw new Error();
    const data=await r.json();
    document.getElementById('connection-status').textContent='CONNECTED';
    document.getElementById('connection-status').style.color='var(--green)';
    document.getElementById('feed-status').textContent='Live — /live_log.json';
    if(data.length!==lastLen){entries=data.slice(-100);lastLen=data.length;renderFeed();updateStats();document.getElementById('last-update').textContent=new Date().toLocaleTimeString();}
  }catch{
    document.getElementById('connection-status').textContent='WAITING';
    document.getElementById('connection-status').style.color='var(--amber)';
  }
}

function renderFeed(){
  const feed=document.getElementById('feed');
  if(!entries.length) return;
  feed.innerHTML=[...entries].reverse().map(e=>`
    <div class="entry ${e.status||'done'}">
      <span class="entry-time">${e.time||'—'}</span>
      <span class="entry-action">${(e.action||'').slice(0,24)}</span>
      <span class="entry-file">${e.file||''}</span>
      <span class="entry-status status-${e.status||'done'}">${(e.status||'DONE').toUpperCase()}</span>
    </div>`).join('');
  document.getElementById('entry-count').textContent=`${entries.length} ENTRIES`;
}

function updateStats(){
  const done=entries.filter(e=>e.status==='done').length;
  const working=entries.filter(e=>e.status==='working').length;
  const failed=entries.filter(e=>e.status==='failed').length;
  const total=entries.length;
  document.getElementById('stat-total').textContent=total;
  document.getElementById('stat-done').textContent=done;
  document.getElementById('stat-working').textContent=working;
  document.getElementById('stat-failed').textContent=failed;
  document.getElementById('stat-rate').textContent=total>0?Math.round(done/total*100)+'%':'—';
  activityHistory.push(total);activityHistory=activityHistory.slice(-10);
  const max=Math.max(...activityHistory,1);
  document.querySelectorAll('#activity-bar .bar').forEach((b,i)=>{b.style.height=Math.max(2,activityHistory[i]/max*40)+'px';});
}

function clearFeed(){entries=[];lastLen=0;document.getElementById('feed').innerHTML='<div class="empty-state">Feed cleared<span class="cursor"></span></div>';updateStats();}

function testEntry(){
  entries.push({time:new Date().toLocaleTimeString(),action:'Test entry fired',file:'jarvis_mcp_server.py',status:'done'});
  lastLen=entries.length;renderFeed();updateStats();
}

setInterval(pollLog,1000);
pollLog();
</script>
</body>
</html>"""


@app.get("/live", response_class=HTMLResponse)
async def live_feed_page():
    return HTMLResponse(content=_LIVE_HTML)


@app.get("/live_log.json")
async def live_log_get():
    if LIVE_LOG_PATH.exists():
        try:
            data = json.loads(LIVE_LOG_PATH.read_text(encoding="utf-8"))
        except Exception:
            data = []
    else:
        data = []
    return JSONResponse(data)


@app.post("/live_log")
async def live_log_post(request: Request):
    try:
        entry = await request.json()
        live_log_append(
            entry.get("action", ""),
            entry.get("file", ""),
            entry.get("status", "done"),
        )
        return JSONResponse({"ok": True})
    except Exception as e:
        return JSONResponse({"ok": False, "error": str(e)}, status_code=400)


@app.get("/grid/frame/{filename}")
async def grid_frame(filename: str):
    """Serve a Pillow-annotated version of a grid image with scanline overlay + label."""
    img_path = GRID_IMAGES_DIR / filename
    if not img_path.exists() or img_path.suffix != ".png":
        return JSONResponse({"error": "not found"}, status_code=404)
    try:
        from PIL import Image, ImageDraw, ImageFont
        import io
        img = Image.open(img_path).convert("RGBA")
        w, h = img.size

        # scanline overlay
        overlay = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        draw = ImageDraw.Draw(overlay)
        for y in range(0, h, 4):
            draw.line([(0, y), (w, y)], fill=(0, 0, 0, 40))

        # amber label bar at bottom
        bar_h = 22
        draw.rectangle([(0, h - bar_h), (w, h)], fill=(10, 15, 24, 200))

        label = img_path.stem.replace("_", " ").replace("-", " ").upper()[:48]
        ts    = now()[:16]
        try:
            font = ImageFont.truetype("cour.ttf", 11)
        except Exception:
            font = ImageFont.load_default()
        draw.text((6, h - bar_h + 4), label, fill=(245, 166, 35, 220), font=font)
        draw.text((w - 90, h - bar_h + 4), ts, fill=(30, 58, 82, 200), font=font)

        composite = Image.alpha_composite(img, overlay).convert("RGB")
        buf = io.BytesIO()
        composite.save(buf, format="PNG", optimize=True)
        buf.seek(0)
        from fastapi.responses import Response
        return Response(content=buf.read(), media_type="image/png")
    except ImportError:
        return FileResponse(str(img_path), media_type="image/png")
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)


_DASHBOARD_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>JARVIS — Command Center</title>
<style>
  @import url('https://fonts.googleapis.com/css2?family=Share+Tech+Mono&family=Orbitron:wght@700;900&display=swap');
  :root{
    --bg:#020408;--surface:#080f18;--card:#0c1520;--border:#0f2035;
    --amber:#f5a623;--green:#00ff88;--red:#ff3355;--blue:#0af;
    --dim:#1e3a52;--text:#4a7a99;--bright:#a0c8e0;
    --mono:'Share Tech Mono',monospace;--display:'Orbitron',sans-serif;
  }
  *{box-sizing:border-box;margin:0;padding:0;}
  body{background:var(--bg);color:var(--text);font-family:var(--mono);font-size:11px;
       height:100vh;display:grid;grid-template-rows:48px 1fr;overflow:hidden;}
  body::before{content:'';position:fixed;inset:0;
    background:repeating-linear-gradient(0deg,transparent,transparent 2px,rgba(0,0,0,.04) 2px,rgba(0,0,0,.04) 4px);
    pointer-events:none;z-index:1000;}
  /* ── topbar ── */
  .topbar{background:var(--surface);border-bottom:1px solid var(--border);
          display:flex;align-items:center;padding:0 20px;gap:16px;}
  .logo{font-family:var(--display);font-size:15px;font-weight:900;letter-spacing:5px;
        color:var(--amber);text-shadow:0 0 15px rgba(245,166,35,.3);}
  .logo span{color:var(--dim);}
  .live-dot{width:6px;height:6px;border-radius:50%;background:var(--green);
            box-shadow:0 0 8px var(--green);animation:blink 1.5s infinite;}
  @keyframes blink{0%,100%{opacity:1}50%{opacity:.2}}
  .topbar-nav{margin-left:auto;display:flex;gap:12px;}
  .nav-btn{font-family:var(--mono);font-size:9px;letter-spacing:2px;color:var(--dim);
           background:transparent;border:1px solid var(--border);padding:5px 10px;
           cursor:pointer;text-decoration:none;}
  .nav-btn:hover{color:var(--amber);border-color:var(--amber);}
  /* ── 3-column main ── */
  .main{display:grid;grid-template-columns:280px 1fr 260px;gap:1px;background:var(--border);overflow:hidden;}
  /* ── LIVE FEED (left) ── */
  .feed-col{background:var(--bg);display:flex;flex-direction:column;overflow:hidden;}
  .col-header{background:var(--surface);padding:7px 12px;font-size:8px;letter-spacing:4px;
              color:var(--dim);border-bottom:1px solid var(--border);display:flex;justify-content:space-between;align-items:center;}
  .feed-scroll{flex:1;overflow-y:auto;padding:8px;display:flex;flex-direction:column;gap:3px;}
  .feed-scroll::-webkit-scrollbar{width:2px;}.feed-scroll::-webkit-scrollbar-thumb{background:var(--border);}
  .entry{display:grid;grid-template-columns:58px 1fr 48px;gap:6px;padding:5px 7px;
         border-left:2px solid var(--border);background:var(--card);animation:fadeIn .3s ease;align-items:center;}
  @keyframes fadeIn{from{opacity:0;transform:translateX(-6px)}to{opacity:1}}
  .entry.done{border-left-color:var(--green)}.entry.working{border-left-color:var(--amber)}.entry.failed{border-left-color:var(--red)}
  .e-time{color:var(--dim);font-size:8px;}
  .e-action{color:var(--bright);font-size:9px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;}
  .e-status{font-size:7px;letter-spacing:2px;text-align:right;}
  .s-done{color:var(--green)}.s-working{color:var(--amber)}.s-failed{color:var(--red)}
  .empty-state{color:var(--dim);font-size:9px;letter-spacing:2px;text-align:center;padding:30px 12px;line-height:2;}
  .cursor{display:inline-block;width:7px;height:11px;background:var(--amber);
          animation:cblink 1s step-end infinite;vertical-align:middle;margin-left:3px;}
  @keyframes cblink{0%,100%{opacity:1}50%{opacity:0}}
  /* ── IMAGE (center) ── */
  .img-col{background:var(--bg);display:flex;flex-direction:column;overflow:hidden;}
  .img-stage{flex:1;display:flex;align-items:center;justify-content:center;position:relative;overflow:hidden;}
  .img-stage img{max-width:100%;max-height:100%;object-fit:contain;display:block;
                 border:1px solid var(--border);image-rendering:pixelated;}
  .img-overlay{position:absolute;inset:0;pointer-events:none;
    background:repeating-linear-gradient(0deg,transparent,transparent 3px,rgba(0,200,255,.015) 3px,rgba(0,200,255,.015) 4px);}
  .img-controls{background:var(--surface);border-top:1px solid var(--border);
                padding:8px 16px;display:flex;align-items:center;gap:12px;}
  .img-name{flex:1;color:var(--bright);font-size:9px;letter-spacing:1px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;}
  .img-counter{color:var(--dim);font-size:8px;white-space:nowrap;}
  .ctrl-btn{background:transparent;border:1px solid var(--border);color:var(--dim);
            font-family:var(--mono);font-size:11px;padding:4px 10px;cursor:pointer;}
  .ctrl-btn:hover{border-color:var(--amber);color:var(--amber);}
  .auto-badge{font-size:7px;letter-spacing:2px;padding:3px 6px;border:1px solid var(--border);color:var(--dim);}
  .auto-badge.on{border-color:var(--green);color:var(--green);}
  .no-images{color:var(--dim);text-align:center;padding:40px;font-size:10px;line-height:2;}
  /* ── GRID NAV (right) ── */
  .grid-col{background:var(--surface);display:flex;flex-direction:column;overflow-y:auto;}
  .grid-col::-webkit-scrollbar{width:2px;}.grid-col::-webkit-scrollbar-thumb{background:var(--border);}
  .district-card{border-bottom:1px solid var(--border);padding:10px 12px;cursor:pointer;transition:background .15s;}
  .district-card:hover{background:var(--card);}
  .district-card a{text-decoration:none;display:block;}
  .d-region{font-size:7px;letter-spacing:3px;color:var(--dim);margin-bottom:3px;}
  .d-name{color:var(--bright);font-size:10px;margin-bottom:4px;}
  .d-keywords{color:var(--text);font-size:8px;line-height:1.6;overflow:hidden;
              display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;}
  .d-img-thumb{width:100%;height:60px;object-fit:cover;margin-bottom:6px;border:1px solid var(--border);display:block;}
  .grid-footer{padding:12px;border-top:1px solid var(--border);}
  .grid-all-btn{display:block;text-align:center;font-size:8px;letter-spacing:3px;color:var(--dim);
               padding:8px;border:1px solid var(--border);text-decoration:none;}
  .grid-all-btn:hover{color:var(--amber);border-color:var(--amber);}
  /* ── stat strip ── */
  .stat-strip{background:var(--card);border-top:1px solid var(--border);
              display:flex;gap:1px;padding:0;}
  .stat-cell{flex:1;padding:5px 8px;border-right:1px solid var(--border);font-size:8px;letter-spacing:1px;}
  .stat-cell:last-child{border-right:none;}
  .stat-cell .sk{color:var(--dim)}.stat-cell .sv{color:var(--green);}
  .stat-cell .sv.warn{color:var(--amber)}.stat-cell .sv.err{color:var(--red)}
</style>
</head>
<body>
<div class="topbar">
  <div class="logo">JARVIS <span>CMD</span></div>
  <div class="live-dot"></div>
  <span style="font-size:9px;color:var(--dim);letter-spacing:3px">COMMAND CENTER</span>
  <div class="topbar-nav">
    <a href="/grid" class="nav-btn">GRID</a>
    <a href="/live" class="nav-btn">LIVE</a>
    <a href="/health" class="nav-btn">HEALTH</a>
  </div>
</div>

<div class="main">

  <!-- ── LEFT: LIVE FEED ── -->
  <div class="feed-col">
    <div class="col-header">
      <span>LIVE FEED</span>
      <span id="feed-ts" style="color:var(--dim);font-size:7px">—</span>
    </div>
    <div class="feed-scroll" id="feed">
      <div class="empty-state" id="feed-empty">
        Waiting for activity<span class="cursor"></span>
      </div>
    </div>
    <div class="stat-strip">
      <div class="stat-cell"><div class="sk">TOTAL</div><div class="sv" id="s-total">0</div></div>
      <div class="stat-cell"><div class="sk">DONE</div><div class="sv" id="s-done">0</div></div>
      <div class="stat-cell"><div class="sk">WORK</div><div class="sv warn" id="s-work">0</div></div>
      <div class="stat-cell"><div class="sk">FAIL</div><div class="sv err" id="s-fail">0</div></div>
    </div>
  </div>

  <!-- ── CENTER: PILLOW IMAGE DISPLAY ── -->
  <div class="img-col">
    <div class="col-header">
      <span>GRID IMAGES</span>
      <span id="img-status" style="font-size:7px;color:var(--dim)">Polling /grid/manifest…</span>
    </div>
    <div class="img-stage" id="img-stage">
      <div class="no-images" id="no-images">
        No images yet.<br>Run <span style="color:var(--amber)">jarvis_image</span> to generate grid cards.
      </div>
      <img id="main-img" src="" alt="" style="display:none">
      <div class="img-overlay"></div>
    </div>
    <div class="img-controls">
      <button class="ctrl-btn" id="btn-prev">&#8592;</button>
      <button class="ctrl-btn" id="btn-next">&#8594;</button>
      <div class="img-name" id="img-name">—</div>
      <div class="img-counter" id="img-counter">0 / 0</div>
      <div class="auto-badge on" id="auto-badge">AUTO</div>
    </div>
  </div>

  <!-- ── RIGHT: GRID NAV ── -->
  <div class="grid-col">
    <div class="col-header" style="position:sticky;top:0;z-index:10;">
      <span>GRID DISTRICTS</span>
      <span style="font-size:7px" id="district-count">—</span>
    </div>
    <div id="district-list"></div>
    <div class="grid-footer">
      <a href="/grid" class="grid-all-btn">&#9632; FULL GRID HIGHWAY</a>
    </div>
  </div>

</div>

<script>
// ── LIVE FEED ──────────────────────────────────────────────────────────────
let lastFeedLen = 0;
function renderFeed(entries) {
  const feed  = document.getElementById('feed');
  const empty = document.getElementById('feed-empty');
  if (!entries.length) { empty.style.display=''; return; }
  empty.style.display = 'none';

  const existing = feed.querySelectorAll('.entry').length;
  entries.slice(existing).forEach(e => {
    const el = document.createElement('div');
    el.className = 'entry ' + (e.status || 'done');
    const action = (e.action || '').substring(0, 38);
    el.innerHTML = `
      <div class="e-time">${e.time || '--:--:--'}</div>
      <div class="e-action" title="${e.action || ''}">${action}</div>
      <div class="e-status s-${e.status || 'done'}">${(e.status||'done').toUpperCase()}</div>
    `;
    feed.appendChild(el);
  });
  feed.scrollTop = feed.scrollHeight;

  document.getElementById('s-total').textContent = entries.length;
  document.getElementById('s-done').textContent  = entries.filter(e=>e.status==='done').length;
  document.getElementById('s-work').textContent  = entries.filter(e=>e.status==='working').length;
  document.getElementById('s-fail').textContent  = entries.filter(e=>e.status==='failed').length;
  document.getElementById('feed-ts').textContent = new Date().toLocaleTimeString();
}
async function pollFeed() {
  try {
    const r = await fetch('/live_log.json');
    if (r.ok) renderFeed(await r.json());
  } catch(e) {}
}
setInterval(pollFeed, 2000);
pollFeed();

// ── IMAGE CAROUSEL ─────────────────────────────────────────────────────────
let images   = [];
let imgIdx   = 0;
let autoPlay = true;
let autoTimer = null;

function showImage(idx) {
  if (!images.length) return;
  imgIdx = ((idx % images.length) + images.length) % images.length;
  const img   = document.getElementById('main-img');
  const name  = document.getElementById('img-name');
  const ctr   = document.getElementById('img-counter');
  const noImg = document.getElementById('no-images');
  const entry = images[imgIdx];
  img.style.display = 'block';
  noImg.style.display = 'none';
  // Use /grid/frame for Pillow-annotated version
  img.src = '/grid/frame/' + entry.name + '?t=' + Date.now();
  name.textContent = entry.name.replace(/_/g,' ').replace(/-/g,' ').replace('.png','');
  ctr.textContent  = (imgIdx + 1) + ' / ' + images.length;
  resetAutoTimer();
}

function resetAutoTimer() {
  if (autoTimer) clearInterval(autoTimer);
  if (autoPlay) autoTimer = setInterval(() => showImage(imgIdx + 1), 4000);
}

document.getElementById('btn-prev').onclick = () => { showImage(imgIdx - 1); };
document.getElementById('btn-next').onclick = () => { showImage(imgIdx + 1); };
document.getElementById('auto-badge').onclick = function() {
  autoPlay = !autoPlay;
  this.textContent = autoPlay ? 'AUTO' : 'PAUSED';
  this.className   = 'auto-badge' + (autoPlay ? ' on' : '');
  resetAutoTimer();
};

async function pollImages() {
  try {
    const r = await fetch('/grid/manifest');
    if (!r.ok) return;
    const data = await r.json();
    document.getElementById('img-status').textContent = data.length + ' images';
    if (data.length !== images.length) {
      images = data.sort((a,b) => b.mtime - a.mtime);
      if (data.length) showImage(0);
    }
  } catch(e) {}
}
setInterval(pollImages, 5000);
pollImages();

// ── GRID DISTRICTS ─────────────────────────────────────────────────────────
async function loadDistricts() {
  try {
    const r = await fetch('/grid/districts');
    if (!r.ok) return;
    const districts = await r.json();
    document.getElementById('district-count').textContent = districts.length + ' nodes';
    const list = document.getElementById('district-list');
    list.innerHTML = '';
    districts.forEach(d => {
      const slug  = d.file.replace('.md','');
      const imgs  = d.images || [];
      const thumb = imgs.length ? `<img class="d-img-thumb" src="/grid/frame/${imgs[0]}" loading="lazy">` : '';
      const el    = document.createElement('div');
      el.className = 'district-card';
      el.innerHTML = `<a href="/grid/node/${slug}">
        ${thumb}
        <div class="d-region">${d.region || ''}</div>
        <div class="d-name">${d.district || slug}</div>
        <div class="d-keywords">${(d.keywords||[]).slice(0,6).join(', ')}</div>
      </a>`;
      list.appendChild(el);
    });
  } catch(e) {}
}
loadDistricts();
</script>
</body>
</html>"""


@app.get("/grid/districts")
async def grid_districts():
    """GRID_CANON with matched image filenames for the dashboard."""
    result = []
    for node in GRID_CANON:
        slug   = node["file"].replace(".md", "")
        imgs   = sorted(GRID_IMAGES_DIR.glob(f"{slug}_*.png"), reverse=True)
        result.append({**node, "images": [p.name for p in imgs]})
    return JSONResponse(result)


@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard_page():
    return HTMLResponse(content=_DASHBOARD_HTML)


@app.get("/gameboy/data")
async def gameboy_data():
    chaos    = load_chaos()
    god_syss = chaos.get("god_systems", {})
    gold_law = chaos.get("gold_law", {}).get("rules", [])
    pipeline = chaos.get("pipeline", {}).get("order", [])
    pipe_pos = {name: i for i, name in enumerate(pipeline)}

    systems = []
    for name, info in god_syss.items():
        systems.append({
            "name":        name,
            "description": info.get("description", ""),
            "domain":      info.get("domain", ""),
            "inputs":      info.get("inputs", []),
            "outputs":     info.get("outputs", []),
            "forbidden":   info.get("forbidden_edges", []),
            "pipeline_pos": pipe_pos.get(name, 99),
        })
    systems.sort(key=lambda s: s["pipeline_pos"])

    districts = [
        {
            "district": n.get("district", ""),
            "region":   n.get("region", ""),
            "keywords": n.get("keywords", [])[:5],
            "slug":     n["file"].replace(".md", ""),
            "warnings": n.get("warnings", []),
        }
        for n in GRID_CANON
    ]

    return JSONResponse({
        "god_systems": systems,
        "gold_law":    gold_law,
        "pipeline":    pipeline,
        "districts":   districts,
    })


_GAMEBOY_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>JARVIS HANDHELD</title>
<style>
@import url('https://fonts.googleapis.com/css2?family=Press+Start+2P&display=swap');
:root {
  --pixel: 'Press Start 2P', monospace;
  --amber: #f5a623; --green: #00ff88; --blue: #0af; --red: #ff3355;
  --dim: #1e3a52; --text: #4a7a99; --bright: #a0c8e0;
  --bg: #020408; --surface: #080f18;
}
* { box-sizing: border-box; margin: 0; padding: 0; }
html, body {
  background: radial-gradient(ellipse at center, #0a0f1a 0%, #020408 100%);
  display: flex; align-items: center; justify-content: center;
  min-height: 100vh; font-family: var(--pixel); user-select: none;
}

/* ── DEVICE SHELL ── */
.device {
  width: 340px;
  background: linear-gradient(160deg, #4a4a4a 0%, #2d2d2d 60%, #222 100%);
  border-radius: 14px 14px 52px 52px;
  padding: 18px 18px 32px;
  position: relative;
  box-shadow: 5px 5px 0 #111, 9px 9px 0 #0a0a0a,
    inset 0 1px 0 rgba(255,255,255,.13), inset 0 -2px 0 rgba(0,0,0,.5);
  background-image:
    repeating-linear-gradient(0deg, rgba(0,0,0,.05) 0, rgba(0,0,0,.05) 1px, transparent 1px, transparent 4px),
    repeating-linear-gradient(90deg, rgba(0,0,0,.05) 0, rgba(0,0,0,.05) 1px, transparent 1px, transparent 4px);
}

.led {
  position: absolute; top: 18px; right: 22px;
  width: 6px; height: 6px; border-radius: 50%;
  background: var(--green); box-shadow: 0 0 8px var(--green);
  animation: led-blink 2s infinite;
}
@keyframes led-blink { 0%,100%{opacity:1} 50%{opacity:.3} }

/* ── SCREEN HOUSING (Minecraft item-frame) ── */
.screen-housing {
  background: #120a02;
  border: 6px solid #6b4420;
  box-shadow: inset 0 0 0 2px #2e1a08, inset 0 0 0 4px #8a5a30,
    0 0 0 1px #1a0a00, 0 4px 14px rgba(0,0,0,.7);
  border-radius: 3px; padding: 8px; margin-bottom: 4px;
}
.screen-label {
  text-align: center; font-size: 5px; letter-spacing: 4px;
  color: #5a3d1c; margin-bottom: 6px;
}

/* ── LCD SCREEN ── */
.screen {
  width: 100%; height: 216px;
  background: var(--bg); border: 2px solid #0a0f1a;
  position: relative; overflow: hidden;
}
.screen::before {
  content: ''; position: absolute; inset: 0; z-index: 100; pointer-events: none;
  background: repeating-linear-gradient(0deg, transparent, transparent 2px, rgba(0,0,0,.09) 2px, rgba(0,0,0,.09) 4px);
}
.screen::after {
  content: ''; position: absolute; top: 0; left: 0; right: 50%; height: 45%;
  background: linear-gradient(135deg, rgba(255,255,255,.04), transparent);
  z-index: 101; pointer-events: none;
}
#screen-inner { position: absolute; inset: 0; overflow: hidden; font-family: var(--pixel); font-size: 7px; color: var(--text); }

/* ── SCREEN PANELS ── */
.panel { display: flex; flex-direction: column; height: 100%; }
.s-header {
  background: var(--surface); border-bottom: 1px solid #0f2035;
  padding: 5px 8px; font-size: 7px; color: var(--amber); letter-spacing: 2px;
  display: flex; justify-content: space-between; flex-shrink: 0;
}
.s-body { flex: 1; padding: 6px 8px; overflow: hidden; }
.s-body.scroll { overflow-y: auto; }
.s-body.scroll::-webkit-scrollbar { width: 2px; }
.s-body.scroll::-webkit-scrollbar-thumb { background: var(--dim); }
.s-footer {
  background: var(--surface); border-top: 1px solid #0f2035;
  padding: 4px 8px; font-size: 5px; color: var(--dim); letter-spacing: 1px; flex-shrink: 0;
}
.row {
  padding: 3px 4px; font-size: 7px; line-height: 1.7;
  overflow: hidden; text-overflow: ellipsis; white-space: nowrap;
  color: var(--bright); display: flex; align-items: center; gap: 4px;
}
.row.sel { color: var(--amber); background: rgba(245,166,35,.07); }
.row .sub { color: var(--dim); font-size: 5px; }
.dl { color: var(--dim); font-size: 5px; letter-spacing: 2px; margin: 6px 0 2px; }
.dv { color: var(--bright); font-size: 6px; line-height: 1.8; word-break: break-word; margin-bottom: 4px; }
.rule { padding: 2px 0; border-bottom: 1px solid #0f2035; font-size: 6px; line-height: 1.9; }
.rule.sel { color: var(--amber); }
.live-e { display: flex; gap: 5px; padding: 2px 0; border-bottom: 1px solid #080f18; font-size: 6px; }
.lt { color: var(--dim); flex-shrink: 0; }
.la { color: var(--bright); flex: 1; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.ls-done { color: var(--green); flex-shrink: 0; }
.ls-working { color: var(--amber); flex-shrink: 0; }
.ls-failed { color: var(--red); flex-shrink: 0; }

/* ── BOOT ── */
.boot-panel {
  display: flex; flex-direction: column; align-items: center; justify-content: center;
  height: 100%; gap: 10px; padding: 0 16px;
}
.boot-logo {
  font-size: 22px; color: var(--amber); letter-spacing: 10px;
  text-shadow: 0 0 20px rgba(245,166,35,.5); animation: gbglow 2s ease-in-out infinite;
}
@keyframes gbglow { 0%,100%{text-shadow:0 0 10px rgba(245,166,35,.3)} 50%{text-shadow:0 0 30px rgba(245,166,35,.8)} }
.boot-sub { font-size: 5px; color: var(--dim); letter-spacing: 3px; }
.boot-lines { width: 100%; min-height: 72px; font-size: 6px; line-height: 2; }
.boot-line { color: var(--green); animation: gbfade .3s ease; }
@keyframes gbfade { from{opacity:0} to{opacity:1} }
.boot-hint { font-size: 5px; color: var(--dim); animation: gblink 1s step-end infinite; }
@keyframes gblink { 0%,100%{opacity:1} 50%{opacity:0} }

/* ── BRAND + CONTROLS ── */
.brand { text-align: center; font-size: 6px; letter-spacing: 7px; color: #3a3a3a; padding: 6px 0 10px; text-shadow: 0 1px 0 #555; }

.ctrl-row { display: flex; align-items: center; justify-content: space-between; padding: 0 8px; margin-bottom: 14px; }

/* D-pad */
.dpad { position: relative; width: 78px; height: 78px; flex-shrink: 0; }
.dph, .dpv { position: absolute; background: #1e1e1e; border-radius: 2px; }
.dph { width: 78px; height: 26px; top: 26px; left: 0; box-shadow: 0 3px 0 #111, inset 0 1px 0 rgba(255,255,255,.08); }
.dpv { width: 26px; height: 78px; left: 26px; top: 0; box-shadow: 2px 0 0 #111; }
.dpc { position: absolute; width: 26px; height: 26px; background: #161616; top: 26px; left: 26px; z-index: 2; }
.dpb { position: absolute; background: transparent; border: none; cursor: pointer; z-index: 3;
       color: #3a3a3a; font-size: 9px; display: flex; align-items: center; justify-content: center; }
.dpb:active { background: rgba(255,255,255,.08); }
.dpb.up    { width: 26px; height: 26px; top: 0; left: 26px; }
.dpb.dn    { width: 26px; height: 26px; bottom: 0; left: 26px; }
.dpb.lf    { width: 26px; height: 26px; left: 0; top: 26px; }
.dpb.rt    { width: 26px; height: 26px; right: 0; top: 26px; }

/* Face buttons */
.face { position: relative; width: 88px; height: 78px; flex-shrink: 0; }
.fb { position: absolute; width: 34px; height: 34px; border-radius: 50%; border: none; cursor: pointer;
      font-family: var(--pixel); font-size: 9px; }
.fb:active { transform: translateY(2px); }
.fb.a { background: linear-gradient(145deg, #c83322, #881811); box-shadow: 0 4px 0 #550f00, 0 4px 10px rgba(0,0,0,.5); color: #ffccaa; right: 0; top: 22px; }
.fb.b { background: linear-gradient(145deg, #223caa, #111e66); box-shadow: 0 4px 0 #001040, 0 4px 10px rgba(0,0,0,.5); color: #aac8ff; left: 0; top: 22px; }
.fbl { position: absolute; font-size: 5px; color: #4a4a4a; letter-spacing: 1px; }
.fbl.a { right: 6px; top: 6px; }
.fbl.b { left: 8px; top: 6px; }

/* Select/Start */
.menu-row { display: flex; justify-content: center; gap: 22px; margin-bottom: 18px; }
.mb { background: #1e1e1e; border: 1px solid #2e2e2e; border-radius: 10px; padding: 5px 14px;
      color: #4a4a4a; font-family: var(--pixel); font-size: 5px; letter-spacing: 1px;
      cursor: pointer; box-shadow: 0 2px 0 #111; transform: rotate(-12deg); }
.mb:active { transform: rotate(-12deg) translateY(1px); box-shadow: none; }

/* Speaker */
.speaker { position: absolute; bottom: 22px; right: 20px;
           display: grid; grid-template-columns: repeat(5, 4px); grid-template-rows: repeat(3, 4px); gap: 3px; }
.sp { width: 4px; height: 4px; border-radius: 50%; background: #1a1a1a; box-shadow: inset 0 1px 0 rgba(0,0,0,.9); }
</style>
</head>
<body>
<div class="device">
  <div class="led"></div>

  <div class="screen-housing">
    <div class="screen-label">JARVIS GRID INTERFACE</div>
    <div class="screen">
      <div id="screen-inner"></div>
    </div>
  </div>

  <div class="brand">JARVIS</div>

  <div class="ctrl-row">
    <div class="dpad">
      <div class="dph"></div>
      <div class="dpv"></div>
      <div class="dpc"></div>
      <button class="dpb up" onclick="nav(-1)">&#9650;</button>
      <button class="dpb dn" onclick="nav(1)">&#9660;</button>
      <button class="dpb lf" onclick="back()">&#9664;</button>
      <button class="dpb rt" onclick="ok()">&#9654;</button>
    </div>
    <div class="face">
      <span class="fbl b">B</span>
      <span class="fbl a">A</span>
      <button class="fb b" onclick="back()">B</button>
      <button class="fb a" onclick="ok()">A</button>
    </div>
  </div>

  <div class="menu-row">
    <button class="mb" onclick="back()">SELECT</button>
    <button class="mb" onclick="start()">START</button>
  </div>

  <div class="speaker" id="spk"></div>
</div>

<script>
// ── speaker dots
(function(){ const s=document.getElementById('spk'); for(let i=0;i<15;i++){const d=document.createElement('div');d.className='sp';s.appendChild(d);} })();

// ── state
let S='boot', cur=0, detail=null, gdata=null, lives=[];
const PG=7;

const MENU=[
  {label:'GOD SYSTEMS', state:'god'},
  {label:'GOLD LAW',    state:'gold'},
  {label:'THE GRID',    state:'grid'},
  {label:'LIVE FEED',   state:'live'},
];

// ── render
function draw(){
  const el=document.getElementById('screen-inner');
  if(S==='menu')       el.innerHTML=rMenu();
  else if(S==='god')   el.innerHTML=rGodList();
  else if(S==='godD')  el.innerHTML=rGodDetail();
  else if(S==='gold')  el.innerHTML=rGold();
  else if(S==='grid')  el.innerHTML=rGrid();
  else if(S==='gridD') el.innerHTML=rGridDetail();
  else if(S==='live')  el.innerHTML=rLive();
}

function cursor(i,sel){ return `<span style="color:${sel?'var(--amber)':'var(--dim)'}">${sel?'&#9658;':' '}</span>`; }

function rMenu(){
  const subs=[
    gdata?gdata.god_systems.length+' NODES':'...',
    gdata?gdata.gold_law.length+' RULES':'...',
    gdata?gdata.districts.length+' DISTRICTS':'...',
    lives.length+' ENTRIES'
  ];
  return `<div class="panel">
    <div class="s-header"><span>JARVIS v2.5</span><span style="color:var(--green)">&#9632; ONLINE</span></div>
    <div class="s-body" style="padding-top:10px">
      ${MENU.map((m,i)=>`<div class="row ${cur===i?'sel':''}">${cursor(i,cur===i)} ${m.label} <span class="sub">${subs[i]}</span></div>`).join('')}
    </div>
    <div class="s-footer">A:SELECT &nbsp; &#8593;&#8595;:MOVE &nbsp; START:MENU</div>
  </div>`;
}

function rGodList(){
  if(!gdata) return rLoad();
  const sys=gdata.god_systems, pip=gdata.pipeline||[];
  const st=Math.floor(cur/PG)*PG, pg=sys.slice(st,st+PG);
  return `<div class="panel">
    <div class="s-header"><span>GOD SYSTEMS</span><span>${cur+1}/${sys.length}</span></div>
    <div class="s-body">
      ${pg.map((s,i)=>{const idx=st+i,inP=pip.includes(s.name);return `<div class="row ${cur===idx?'sel':''}">${cursor(idx,cur===idx)}<span style="color:${inP?'var(--green)':'var(--bright)'}">${s.name}</span><span class="sub">${(s.description||'').substring(0,18)}</span></div>`;}).join('')}
    </div>
    <div class="s-footer">A:VIEW &nbsp; B:BACK &nbsp; &#8593;&#8595;:SCROLL</div>
  </div>`;
}

function rGodDetail(){
  if(!detail) return rLoad();
  const d=detail;
  const desc=(d.description||'—').substring(0,180);
  const dom=(d.domain||'—').substring(0,80);
  const ins=(d.inputs||[]).join(', ').substring(0,60)||'—';
  const outs=(d.outputs||[]).join(', ').substring(0,60)||'—';
  const forb=(d.forbidden||[]).join(', ')||'none';
  return `<div class="panel">
    <div class="s-header"><span style="color:var(--amber)">${d.name}</span><span style="color:var(--dim)">SYS</span></div>
    <div class="s-body scroll">
      <div class="dl">DOMAIN</div><div class="dv">${dom}</div>
      <div class="dl">DESCRIPTION</div><div class="dv">${desc}</div>
      <div class="dl">INPUTS</div><div class="dv">${ins}</div>
      <div class="dl">OUTPUTS</div><div class="dv">${outs}</div>
      <div class="dl">FORBIDDEN EDGES</div><div class="dv" style="color:var(--red)">${forb}</div>
    </div>
    <div class="s-footer">B:BACK &nbsp; &#8593;&#8595;:SCROLL</div>
  </div>`;
}

function rGold(){
  if(!gdata) return rLoad();
  const rules=gdata.gold_law, st=Math.floor(cur/PG)*PG, pg=rules.slice(st,st+PG);
  return `<div class="panel">
    <div class="s-header"><span>GOLD LAW</span><span>${rules.length} RULES</span></div>
    <div class="s-body">
      ${pg.map((r,i)=>{const idx=st+i;return `<div class="rule ${cur===idx?'sel':''}"><span style="color:var(--amber);margin-right:3px">${cur===idx?'&#9658;':String(idx+1).padStart(2,'0')}</span>${r.substring(0,52)}</div>`;}).join('')}
    </div>
    <div class="s-footer">B:BACK &nbsp; &#8593;&#8595;:SCROLL</div>
  </div>`;
}

function rGrid(){
  if(!gdata) return rLoad();
  const ds=gdata.districts, st=Math.floor(cur/PG)*PG, pg=ds.slice(st,st+PG);
  return `<div class="panel">
    <div class="s-header"><span>THE GRID</span><span>${cur+1}/${ds.length}</span></div>
    <div class="s-body">
      ${pg.map((d,i)=>{const idx=st+i;return `<div class="row ${cur===idx?'sel':''}">${cursor(idx,cur===idx)}<span style="color:var(--blue)">${d.district}</span><span class="sub">[${(d.region||'').split(' ').pop()}]</span></div>`;}).join('')}
    </div>
    <div class="s-footer">A:VIEW &nbsp; B:BACK &nbsp; &#8593;&#8595;:SCROLL</div>
  </div>`;
}

function rGridDetail(){
  if(!detail) return rLoad();
  const d=detail, kw=(d.keywords||[]).join(', ')||'—';
  const warns=(d.warnings||[]).slice(0,2);
  return `<div class="panel">
    <div class="s-header"><span style="color:var(--blue)">${d.district}</span><span style="color:var(--dim)">NODE</span></div>
    <div class="s-body scroll">
      <div class="dl">REGION</div><div class="dv">${d.region}</div>
      <div class="dl">KEYWORDS</div><div class="dv">${kw}</div>
      ${warns.length?`<div class="dl">WARNINGS</div>${warns.map(w=>`<div class="dv" style="color:var(--amber)">${w.substring(0,80)}</div>`).join('')}`:''}
      <div style="margin-top:10px"><a href="/grid/node/${d.slug}" style="color:var(--blue);font-size:6px;text-decoration:none">&#9654; OPEN IN GRID</a></div>
    </div>
    <div class="s-footer">B:BACK &nbsp; A:OPEN</div>
  </div>`;
}

function rLive(){
  const ents=lives.slice(-PG);
  return `<div class="panel">
    <div class="s-header"><span>LIVE FEED</span><span style="color:var(--green)">&#9632; LIVE</span></div>
    <div class="s-body">
      ${ents.length?ents.map(e=>`<div class="live-e"><span class="lt">${(e.time||'').substring(0,5)}</span><span class="la">${(e.action||'').substring(0,28)}</span><span class="ls-${e.status||'done'}">${(e.status||'OK').toUpperCase().substring(0,4)}</span></div>`).join(''):'<div style="color:var(--dim);font-size:6px;padding:20px;text-align:center">NO ACTIVITY YET</div>'}
    </div>
    <div class="s-footer">B:BACK &nbsp; AUTO-REFRESH 3S</div>
  </div>`;
}

function rLoad(){ return `<div class="panel"><div class="s-body" style="display:flex;align-items:center;justify-content:center;height:100%"><span style="color:var(--dim);font-size:6px">LOADING...</span></div></div>`; }

// ── navigation
function nav(d){
  let mx=0;
  if(S==='menu') mx=MENU.length;
  if(S==='god'&&gdata)  mx=gdata.god_systems.length;
  if(S==='gold'&&gdata) mx=gdata.gold_law.length;
  if(S==='grid'&&gdata) mx=gdata.districts.length;
  if(mx>0){ cur=((cur+d)%mx+mx)%mx; draw(); beep(d>0?440:400,40); }
}

function ok(){
  beep(880,60);
  if(S==='boot'){ S='menu'; cur=0; draw(); return; }
  if(S==='menu'){ S=MENU[cur].state; cur=0; draw(); return; }
  if(S==='god'&&gdata){ detail=gdata.god_systems[cur]; S='godD'; draw(); return; }
  if(S==='grid'&&gdata){ detail=gdata.districts[cur]; S='gridD'; draw(); return; }
  if(S==='gridD'&&detail){ window.open('/grid/node/'+detail.slug,'_blank'); return; }
}

function back(){
  beep(220,40);
  if(S==='godD')  { S='god';  draw(); return; }
  if(S==='gridD') { S='grid'; draw(); return; }
  if(['god','gold','grid','live'].includes(S)){ S='menu'; cur=0; draw(); return; }
}

function start(){
  beep(660,80);
  S='menu'; cur=0; draw();
}

// ── 8-bit beep
let actx=null;
function beep(f,ms){
  try{
    if(!actx) actx=new(window.AudioContext||window.webkitAudioContext)();
    const o=actx.createOscillator(), g=actx.createGain();
    o.connect(g); g.connect(actx.destination);
    o.type='square'; o.frequency.value=f;
    g.gain.setValueAtTime(0.07,actx.currentTime);
    g.gain.exponentialRampToValueAtTime(0.001,actx.currentTime+ms/1000);
    o.start(); o.stop(actx.currentTime+ms/1000);
  }catch(e){}
}

// ── keyboard
document.addEventListener('keydown',e=>{
  const k=e.key;
  if(['ArrowUp','ArrowDown','ArrowLeft','ArrowRight',' '].includes(k)||k==='Enter') e.preventDefault();
  if(k==='ArrowUp')   nav(-1);
  if(k==='ArrowDown') nav(1);
  if(k==='ArrowRight'||k==='z'||k==='Z'||k==='Enter') ok();
  if(k==='ArrowLeft' ||k==='x'||k==='X'||k==='Escape') back();
  if(k===' ') start();
});

// ── boot sequence
const BOOT_LINES=[
  'INITIALIZING...',
  'LOADING GOD SYSTEMS...',
  'CHECKING GOLD LAW...',
  'MOUNTING THE GRID...',
  'ERIS ENTROPY CHECK...',
  'READY.',
];

function runBoot(){
  const el=document.getElementById('screen-inner');
  el.innerHTML=`<div class="boot-panel">
    <div class="boot-logo">JARVIS</div>
    <div class="boot-sub">GOD SYSTEM INTERFACE v2.5</div>
    <div class="boot-lines" id="blines"></div>
    <div class="boot-hint">PRESS START</div>
  </div>`;
  let i=0;
  function tick(){
    if(i>=BOOT_LINES.length){ setTimeout(()=>{S='menu';cur=0;draw();},700); return; }
    const ln=document.createElement('div');
    ln.className='boot-line';
    ln.textContent=BOOT_LINES[i++];
    document.getElementById('blines').appendChild(ln);
    setTimeout(tick,220);
  }
  setTimeout(tick,350);
}

// ── data
async function loadData(){
  try{ const r=await fetch('/gameboy/data'); if(r.ok){ gdata=await r.json(); if(S!=='boot') draw(); } }catch(e){}
}
async function loadLive(){
  try{ const r=await fetch('/live_log.json'); if(r.ok){ lives=await r.json(); if(S==='live') draw(); } }catch(e){}
}

loadData();
loadLive();
setInterval(loadLive,3000);
runBoot();
</script>
</body>
</html>"""


@app.get("/gameboy", response_class=HTMLResponse)
async def gameboy_page():
    return HTMLResponse(content=_GAMEBOY_HTML)


if __name__ == "__main__":
    print("═" * 50)
    print("JARVIS MCP SERVER v1.0")
    print("═" * 50)

    chaos = load_chaos()
    if chaos:
        entropy = compute_entropy_vector(chaos)
        print(f"CHAOS loaded:  v{chaos.get('chaos_version','?')} | {len(chaos.get('god_systems',{}))} systems")
        print(f"ERIS entropy:  {entropy['score']:.3f} [{entropy['status']}]")
        print(f"Guardian:      {chaos.get('mission_statement',{}).get('guardian','?')}")
    else:
        print(f"⚠  CHAOS seed not found — expected: {CHAOS_PATH}")

    # Seed Grid nodes into Neo4j (fire-and-forget — skips silently if Neo4j is offline)
    try:
        grid_result = neo4j_seed_grid()
        print(f"Grid seeded:   {grid_result['nodes']} nodes, {grid_result['edges']} edges")
    except Exception as _grid_err:
        print(f"Grid seed skipped (Neo4j offline): {_grid_err}")

    print()
    print("Running on http://localhost:7777")
    print("═" * 50)

    uvicorn.run(app, host="0.0.0.0", port=7777, log_level="warning")
