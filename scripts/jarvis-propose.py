#!/usr/bin/env python3
"""
GNPL proposal — called via /propose <type> <description>.
Creates a formal consensus proposal in consensus_proposals table.
JARVIS proposes. Raven approves. The record is the governance.

Proposal types: architecture, feature, patch, decision, gold_law
Trust scores:   jarvis=1.0, codex=0.85, gpt=0.80, gemini=0.70
Quorum:         1 (Raven approval sufficient for all types)
"""
import json
import os
import sys
import urllib.request
from datetime import datetime, timezone

SUPABASE_URL = os.environ.get("SUPABASE_URL", "https://oexghfsvhnggddllgvrt.supabase.co")
SUPABASE_ANON = os.environ.get("SUPABASE_ANON_KEY", "sb_publishable_N1-MFLpXtOXkKh3UQNfclw_ZG0TVqOA")
REST_BASE = f"{SUPABASE_URL}/rest/v1"
HEADERS = {
    "Content-Type": "application/json",
    "apikey": SUPABASE_ANON,
    "Authorization": f"Bearer {SUPABASE_ANON}",
}

VALID_TYPES = {"architecture", "feature", "patch", "decision", "gold_law"}
TRUST_SCORES = {"jarvis": 1.0, "codex": 0.85, "gpt": 0.80, "gemini": 0.70}


def create_proposal(proposal_type: str, description: str, patch_id: str = None) -> dict | None:
    payload = {
        "proposal_type": proposal_type,
        "proposer": "jarvis",
        "payload": {
            "description": description,
            "proposer_trust": TRUST_SCORES["jarvis"],
            "proposed_at": datetime.now(timezone.utc).isoformat(),
        },
        "status": "pending",
        "votes": {"jarvis": TRUST_SCORES["jarvis"]},
        "required_quorum": 1,
        "stage": "proposed",
    }
    if patch_id:
        payload["patch_id"] = patch_id

    # P34 phase 2: writes go through the grid-write service-role proxy, not direct
    # PostgREST — consensus_proposals is anon read-only at the DB now (GL5).
    body = json.dumps({
        "table": "consensus_proposals", "op": "insert", "data": payload, "returning": "id",
    }).encode()
    req = urllib.request.Request(
        f"{SUPABASE_URL}/functions/v1/grid-write",
        data=body,
        headers=HEADERS,
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=8) as resp:
            res = json.loads(resp.read())
            if not res.get("ok"):
                print(f"grid-write rejected proposal: {res.get('error')}", file=sys.stderr)
                return None
            d = res.get("data")
            if isinstance(d, dict):
                return d
            if isinstance(d, list) and d:
                return d[0]
            return {"id": "created"}
    except Exception as e:
        print(f"Error creating proposal: {e}", file=sys.stderr)
        return None


def list_open() -> list:
    params = "select=id,proposal_type,proposer,payload,status,created_at,patch_id&status=eq.pending&order=created_at.desc&limit=10"
    req = urllib.request.Request(
        f"{REST_BASE}/consensus_proposals?{params}",
        headers={"apikey": SUPABASE_ANON, "Authorization": f"Bearer {SUPABASE_ANON}"},
    )
    try:
        with urllib.request.urlopen(req, timeout=8) as resp:
            return json.loads(resp.read())
    except Exception:
        return []


def main():
    args = sys.argv[1:]

    if not args or args[0] == "list":
        proposals = list_open()
        if not proposals:
            print("No open proposals.")
            sys.exit(0)
        print(f"OPEN PROPOSALS ({len(proposals)})")
        print("─" * 50)
        for p in proposals:
            ts = (p.get("created_at") or "")[:10]
            pid = (p.get("patch_id") or "")
            pid_str = f" [{pid}]" if pid else ""
            desc = ((p.get("payload") or {}).get("description") or "")[:100]
            print(f"  [{p['proposal_type']} {ts}]{pid_str}")
            print(f"  {desc}")
            print()
        sys.exit(0)

    if len(args) < 2:
        print("Usage: jarvis-propose.py <type> <description> [patch_id]")
        print(f"Types: {', '.join(sorted(VALID_TYPES))}")
        print("Example: jarvis-propose.py architecture 'Migrate BUS to Supabase Realtime'")
        sys.exit(1)

    proposal_type = args[0].lower()
    if proposal_type not in VALID_TYPES:
        print(f"Invalid type '{proposal_type}'. Valid: {', '.join(sorted(VALID_TYPES))}")
        sys.exit(1)

    description = args[1]
    patch_id = args[2] if len(args) > 2 else None

    print(f"GNPL PROPOSAL — {proposal_type.upper()}")
    print("─" * 50)

    result = create_proposal(proposal_type, description, patch_id)
    if result:
        proposal_id = str(result.get("id", "unknown"))[:8]
        print(f"  created:  {proposal_id}...")
        print(f"  type:     {proposal_type}")
        print(f"  proposer: jarvis (trust=1.0)")
        print(f"  status:   pending — awaiting Raven approval")
        if patch_id:
            print(f"  patch:    {patch_id}")
        print(f"  payload:  {description[:120]}")
        print()
        print("Proposal on record. Raven reviews and approves.")
    else:
        print("Failed to create proposal. Supabase may be unreachable.")
        sys.exit(1)


if __name__ == "__main__":
    main()
