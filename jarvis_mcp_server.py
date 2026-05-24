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
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

BASE_DIR   = Path(__file__).parent
CHAOS_PATH = BASE_DIR / "chaos" / "chaos_seed.json"


def load_env_file(path: Path = BASE_DIR / ".env") -> None:
    if not path.exists():
        return
    for raw_line in path.read_text().splitlines():
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

def supabase_update_stats(system_id: str, touches: int = 1) -> dict:
    if not supabase_enabled():
        return {"ok": False, "status": None, "error": "Supabase credentials not configured"}
    try:
        req = urllib.request.Request(
            f"{SUPABASE_URL}/rest/v1/god_system_stats?system_id=eq.{system_id}",
            data=json.dumps({
                "session_touches": touches,
                "last_updated": now()
            }).encode(),
            headers={
                "Content-Type": "application/json",
                "apikey": SUPABASE_KEY,
                "Authorization": f"Bearer {SUPABASE_KEY}",
                "Prefer": "return=minimal"
            },
            method="PATCH"
        )
        with urllib.request.urlopen(req, timeout=5) as r:
            return {"ok": r.status in (200, 204), "status": r.status, "error": None}
    except urllib.error.HTTPError as e:
        return {"ok": False, "status": e.code, "error": e.read().decode(errors="replace")}
    except Exception as e:
        return {"ok": False, "status": None, "error": str(e)}

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
                "platform": {"type": "string", "enum": ["claude", "gpt", "gemini"]}
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
                "platform": {"type": "string", "enum": ["claude", "gpt", "gemini"]},
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
                "decision": {"type": "string"},
                "rationale": {"type": "string"},
                "system_affected": {"type": "string"}
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
]

PLATFORM_ARCHETYPES = {
    "claude": {"archetype": "Shiroe", "role": "vetting, audit, consistency enforcement"},
    "gpt":    {"archetype": "Kang",   "role": "production, execution, organized JARVIS spec"},
    "gemini": {"archetype": "Aizen",  "role": "ideation, interpretation, instance demonstration"},
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
    # Update system touches for platforms
    mnemos_stats = supabase_update_stats("MNEMOS")
    eris_stats = supabase_update_stats("ERIS")
    # Local fallback
    log = load_log(LOG_PATH)
    log.append(entry)
    save_log(LOG_PATH, log)
    mnemos_vector = store_mnemos_session(entry)

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

    entry = {
        "id":              str(uuid.uuid4())[:8],
        "timestamp":       now(),
        "decision":        decision,
        "rationale":       rationale,
        "system_affected": system,
        "raven_approved":  False
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
    stats_sync = supabase_update_stats(entry["system_affected"])
    # Local fallback
    log = load_log(PROM_PATH)
    log.append(entry)
    save_log(PROM_PATH, log)
    mnemos_vector = store_mnemos_prometheus(entry)

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
    return "\n".join(lines)


TOOL_HANDLERS = {
    "jarvis_status":     handle_jarvis_status,
    "jarvis_entropy":    handle_jarvis_entropy,
    "jarvis_god_system": handle_jarvis_god_system,
    "jarvis_end":        handle_jarvis_end,
    "jarvis_log":        handle_jarvis_log,
    "jarvis_overlap":    handle_jarvis_overlap,
    "jarvis_sessions":   handle_jarvis_sessions,
    "jarvis_recall":     handle_jarvis_recall,
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

    print()
    print("Running on http://localhost:7777")
    print("═" * 50)

    uvicorn.run(app, host="0.0.0.0", port=7777, log_level="warning")
