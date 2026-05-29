#!/usr/bin/env python3
"""
In-session memory recall — called via /recall <query> slash command.
Queries MNEMOS and prometheus_log, prints relevant memories for JARVIS to reference mid-session.
"""
import json
import os
import sys
import urllib.request
from datetime import datetime, timezone

SUPABASE_URL = os.environ.get("SUPABASE_URL", "https://oexghfsvhnggddllgvrt.supabase.co")
SUPABASE_ANON = os.environ.get("SUPABASE_ANON_KEY", "sb_publishable_N1-MFLpXtOXkKh3UQNfclw_ZG0TVqOA")
RECALL_FN = f"{SUPABASE_URL}/functions/v1/mnemos-recall"
REST_BASE = f"{SUPABASE_URL}/rest/v1"
HEADERS = {"apikey": SUPABASE_ANON, "Authorization": f"Bearer {SUPABASE_ANON}"}


def recall(payload: dict) -> list:
    data = json.dumps(payload).encode()
    req = urllib.request.Request(
        RECALL_FN, data=data,
        headers={"Content-Type": "application/json", "Authorization": f"Bearer {SUPABASE_ANON}"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=8) as resp:
            return json.loads(resp.read()).get("memories", [])
    except Exception:
        return []


def query_proposals(limit: int = 5, status: str = "pending") -> list:
    params = f"select=proposal_type,proposer,payload,status,patch_id,created_at&status=eq.{status}&order=created_at.desc&limit={limit}"
    url = f"{REST_BASE}/consensus_proposals?{params}"
    req = urllib.request.Request(url, headers=HEADERS)
    try:
        with urllib.request.urlopen(req, timeout=8) as resp:
            return json.loads(resp.read())
    except Exception:
        return []


def query_prometheus(limit: int = 5, min_weight: float = 0.0) -> list:
    params = f"select=decision,rationale,gl_law,tags,eris_weight,timestamp&raven_approved=eq.true&eris_weight=gte.{min_weight}&order=eris_weight.desc,timestamp.desc&limit={limit}"
    url = f"{REST_BASE}/prometheus_log?{params}"
    req = urllib.request.Request(url, headers=HEADERS)
    try:
        with urllib.request.urlopen(req, timeout=8) as resp:
            return json.loads(resp.read())
    except Exception:
        return []


def main():
    query = " ".join(sys.argv[1:]).strip()
    if not query:
        print("Usage: jarvis-recall.py <query>")
        print("Example: jarvis-recall.py Pachinko Bounce monetization")
        sys.exit(1)

    print(f"MNEMOS RECALL — \"{query}\"")
    print("─" * 50)

    # Full-text + tag search
    results = recall({"query": query, "limit": 8})

    # For governance queries: pull MNEMOS decisions + prometheus_log
    gov_keywords = ["gold law", "gl", "decision", "constraint", "governance", "architecture", "gl2", "gl5", "gl6", "gl7", "gl9"]
    is_gov = any(k in query.lower() for k in gov_keywords)

    if is_gov:
        decisions = recall({"source_type": "decision", "limit": 5})
        seen = {r.get("text") for r in results}
        for d in decisions:
            if d.get("text") not in seen:
                results.append(d)

    if not results:
        print("No memories found for that query.")
        print("MNEMOS may be unreachable or no matching records exist.")
    else:
        for m in results:
            ts = (m.get("timestamp") or "")[:10]
            src = (m.get("source_type") or "memory")[:14]
            text = (m.get("text") or "").replace("\n", " ")
            tags = m.get("tags") or []
            tag_str = f" [{', '.join(tags[:3])}]" if tags else ""
            print(f"[{src} {ts}]{tag_str}")
            print(f"  {text[:200]}")
            print()

    # Open GNPL proposals (governance queries)
    if is_gov:
        open_proposals = query_proposals(limit=3)
        if open_proposals:
            print("─" * 50)
            print("OPEN PROPOSALS (GNPL):")
            for p in open_proposals:
                ptype = p.get("proposal_type") or "?"
                ts = (p.get("created_at") or "")[:10]
                pid = p.get("patch_id") or ""
                pid_str = f" [{pid}]" if pid else ""
                desc = ((p.get("payload") or {}).get("description") or "")[:120]
                print(f"  [{ptype} {ts}]{pid_str} {desc}")
            print()

    # Prometheus structured decisions (governance queries always pull this)
    if is_gov:
        decisions_pg = query_prometheus(limit=5, min_weight=0.8)
        if decisions_pg:
            print("─" * 50)
            print("PROMETHEUS RECORD — active governance decisions:")
            for d in decisions_pg:
                gl = d.get("gl_law") or "—"
                ts = (d.get("timestamp") or "")[:10]
                w = d.get("eris_weight") or 0
                decision = (d.get("decision") or "").replace("\n", " ")
                tags = d.get("tags") or []
                tag_str = f" [{', '.join(tags[:3])}]" if tags else ""
                print(f"  [{gl} w={w:.2f} {ts}]{tag_str}")
                print(f"    {decision[:180]}")
                print()

    total = len(results)
    print("─" * 50)
    print(f"{total} memories recalled from MNEMOS.")


if __name__ == "__main__":
    main()
