#!/usr/bin/env python3
"""
Grid node registration + heartbeat.
Upserts this node into grid_nodes table and reports status.
Called on session start (optional) and daily via GitHub Actions.

Node 001 — Raven's node. First node on The Grid.
"""
import json
import os
import sys
import urllib.request
from datetime import datetime, timezone

SUPABASE_URL = os.environ.get("SUPABASE_URL", "https://oexghfsvhnggddllgvrt.supabase.co")
SUPABASE_ANON = os.environ.get("SUPABASE_ANON_KEY", "sb_publishable_N1-MFLpXtOXkKh3UQNfclw_ZG0TVqOA")
REST_BASE = f"{SUPABASE_URL}/rest/v1"

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NODE_PATH = os.path.join(REPO_ROOT, "nodes", "raven.json")


def load_node() -> dict:
    try:
        with open(NODE_PATH, "r") as f:
            return json.load(f)
    except Exception:
        return {}


def heartbeat(node: dict) -> bool:
    payload = json.dumps({
        "node_id":       node["node_id"],
        "owner":         node["owner"],
        "owner_email":   node.get("owner_email"),
        "trust_score":   node.get("trust_score", 1.0),
        "capabilities":  node.get("capabilities", []),
        "gnpl_version":  node.get("gnpl_version", "1.0"),
        "grid_version":  node.get("grid_version", "0.1"),
        "node_type":     node.get("node_type", "personal"),
        "status":        "active",
        "last_seen":     datetime.now(timezone.utc).isoformat(),
        "metadata":      {
            "stack": node.get("stack", []),
            "description": node.get("description", ""),
            "established": node.get("established", ""),
        },
    }).encode()

    req = urllib.request.Request(
        f"{REST_BASE}/grid_nodes",
        data=payload,
        headers={
            "Content-Type": "application/json",
            "apikey": SUPABASE_ANON,
            "Authorization": f"Bearer {SUPABASE_ANON}",
            "Prefer": "resolution=merge-duplicates,return=minimal",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=8) as resp:
            return resp.status in (200, 201, 204)
    except Exception as e:
        print(f"  [node] heartbeat failed: {e}", file=sys.stderr)
        return False


def get_node_count() -> int:
    req = urllib.request.Request(
        f"{REST_BASE}/grid_nodes?select=node_id&status=eq.active",
        headers={
            "apikey": SUPABASE_ANON,
            "Authorization": f"Bearer {SUPABASE_ANON}",
            "Prefer": "count=exact",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=8) as resp:
            count_hdr = resp.getheader("Content-Range", "")
            if "/" in count_hdr:
                return int(count_hdr.split("/")[-1])
            data = json.loads(resp.read())
            return len(data) if isinstance(data, list) else 0
    except Exception:
        return 0


def main():
    node = load_node()
    if not node:
        print("ERROR: could not load nodes/raven.json", file=sys.stderr)
        sys.exit(1)

    print(f"GRID NODE — {node['node_id']}")
    print(f"  owner:      {node['owner']}")
    print(f"  type:       {node.get('node_type', '?')}")
    print(f"  trust:      {node.get('trust_score', 1.0)}")
    print(f"  caps:       {', '.join(node.get('capabilities', []))}")

    ok = heartbeat(node)
    print(f"  heartbeat:  {'ok' if ok else 'FAILED'}")

    count = get_node_count()
    if count:
        print(f"  grid size:  {count} active node(s)")

    if not ok:
        sys.exit(1)


if __name__ == "__main__":
    main()
