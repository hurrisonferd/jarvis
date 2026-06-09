#!/usr/bin/env python3
"""
P30 — World kernel registration + heartbeat.
Reads worlds/<name>.json and upserts into world_kernels + world_agents.
Run directly or called daily via monitor-daily.yml alongside node heartbeat.

Usage: python3 jarvis-world-init.py [world_name]
Default world_name: raven  →  reads worlds/raven.json
"""
import json
import os
import sys
import urllib.request
from datetime import datetime, timezone

SUPABASE_URL  = os.environ.get("SUPABASE_URL",  "https://oexghfsvhnggddllgvrt.supabase.co")
SUPABASE_ANON = os.environ.get("SUPABASE_ANON_KEY", "sb_publishable_N1-MFLpXtOXkKh3UQNfclw_ZG0TVqOA")
# P34: the world_* tables are anon read-only; writes go through the service role.
# Heartbeat (CI) carries SUPABASE_SERVICE_KEY; falls back to anon for local reads.
SUPABASE_SERVICE_KEY = os.environ.get("SUPABASE_SERVICE_KEY") or os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
WRITE_KEY     = SUPABASE_SERVICE_KEY or SUPABASE_ANON
REST_BASE     = f"{SUPABASE_URL}/rest/v1"
REPO_ROOT     = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WORLDS_DIR    = os.path.join(REPO_ROOT, "worlds")
DEFAULT_WORLD = "raven"


def load_world(name: str) -> dict:
    path = os.path.join(WORLDS_DIR, f"{name}.json")
    try:
        with open(path, "r") as f:
            return json.load(f)
    except Exception as e:
        print(f"ERROR: could not load worlds/{name}.json: {e}", file=sys.stderr)
        return {}


def rest_upsert(table: str, payload: dict) -> bool:
    data = json.dumps(payload).encode()
    req = urllib.request.Request(
        f"{REST_BASE}/{table}",
        data=data,
        headers={
            "Content-Type":  "application/json",
            "apikey":        WRITE_KEY,
            "Authorization": f"Bearer {WRITE_KEY}",
            "Prefer":        "resolution=merge-duplicates,return=minimal",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=8) as resp:
            return resp.status in (200, 201, 204)
    except Exception as e:
        print(f"  [{table}] upsert failed: {e}", file=sys.stderr)
        return False


def emit_event(world_id: str, event_type: str, payload: dict) -> None:
    rest_upsert("world_events", {
        "world_id":   world_id,
        "event_type": event_type,
        "stage":      "MNEMOS",
        "agent_id":   "jarvis",
        "payload":    payload,
        "gl_law":     "GL9",
        "ts":         datetime.now(timezone.utc).isoformat(),
        "patch_id":   "P30",
    })


def register_world(world: dict) -> bool:
    return rest_upsert("world_kernels", {
        "world_id":       world["world_id"],
        "node_id":        world["node_id"],
        "owner":          world["owner"],
        "display_name":   world["display_name"],
        "description":    world.get("description", ""),
        "schema_version": world.get("schema_version", 1),
        "rules":          world.get("rules", {}),
        "bounds":         world["bounds"],
        "initial_state":  world.get("initial_state", {}),
        "access_policy":  world.get("access_policy", {}),
        "tick_rate_ms":   world.get("tick_rate_ms", 900),
        "status":         "active",
        "gl7_approved":   world.get("gl7_approved", False),
        "raven_sign_off": world.get("raven_sign_off", False),
        "patch_id":       "P30",
    })


def register_agents(world: dict) -> int:
    world_id = world["world_id"]
    ok = 0
    for agent_id, cfg in world.get("agents", {}).items():
        if rest_upsert("world_agents", {
            "world_id":     world_id,
            "agent_id":     agent_id,
            "role":         cfg.get("role", "observer"),
            "trust_score":  cfg.get("trust", 0.5),
            "capabilities": cfg.get("capabilities", []),
            "admitted_by":  world["owner"],
            "status":       "active",
            "patch_id":     "P30",
        }):
            ok += 1
    return ok


def get_world_count() -> int:
    req = urllib.request.Request(
        f"{REST_BASE}/world_kernels?select=world_id&status=eq.active",
        headers={
            "apikey":        SUPABASE_ANON,
            "Authorization": f"Bearer {SUPABASE_ANON}",
            "Prefer":        "count=exact",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=8) as resp:
            hdr = resp.getheader("Content-Range", "")
            if "/" in hdr:
                return int(hdr.split("/")[-1])
            return len(json.loads(resp.read()) or [])
    except Exception:
        return 0


def main():
    world_name = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_WORLD
    world = load_world(world_name)
    if not world:
        sys.exit(1)

    bounds = world.get("bounds", {})

    print(f"WORLD KERNEL — {world['world_id']}")
    print(f"  node:         {world['node_id']}")
    print(f"  owner:        {world['owner']}")
    print(f"  display:      {world['display_name']}")
    print(f"  tick_rate:    {world.get('tick_rate_ms', 900)}ms")
    print(f"  bounds:       {bounds.get('max_objects',0)} obj | depth {bounds.get('max_depth',0)} | {bounds.get('storage_budget_kb',0)}kb | {bounds.get('max_child_worlds',0)} child worlds")
    print(f"  gl7:          {'approved' if world.get('gl7_approved') else 'PENDING'}")
    print(f"  raven signoff:{'yes' if world.get('raven_sign_off') else 'PENDING'}")

    ok_world = register_world(world)
    print(f"  register:     {'ok' if ok_world else 'FAILED'}")

    ok_agents = register_agents(world)
    print(f"  agents:       {ok_agents} registered")

    if ok_world:
        emit_event(world["world_id"], "world_heartbeat", {
            "schema_version": world.get("schema_version", 1),
            "status": "active",
        })

    count = get_world_count()
    if count:
        print(f"  grid worlds:  {count} active")

    if not ok_world:
        sys.exit(1)


if __name__ == "__main__":
    main()
