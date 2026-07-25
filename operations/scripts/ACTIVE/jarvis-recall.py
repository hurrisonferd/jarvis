#!/usr/bin/env python3
"""
In-session memory recall — called via /recall <query> slash command.
Read order: memory/mnemos/ repo files first (no credentials), then Supabase semantic search.
Also queries prometheus_log and consensus_proposals for governance queries.
"""
import json
import os
import pathlib
import sys
import urllib.request

SUPABASE_URL  = os.environ.get("SUPABASE_URL",  "https://oexghfsvhnggddllgvrt.supabase.co")
if not SUPABASE_URL.startswith(("http://", "https://")):
    SUPABASE_URL = f"https://{SUPABASE_URL}"  # secret may omit the scheme

SUPABASE_ANON = os.environ.get("SUPABASE_ANON_KEY", "sb_publishable_N1-MFLpXtOXkKh3UQNfclw_ZG0TVqOA")
SEARCH_FN     = f"{SUPABASE_URL}/functions/v1/mnemos-search"
RECALL_FN     = f"{SUPABASE_URL}/functions/v1/mnemos-recall"
REST_BASE     = f"{SUPABASE_URL}/rest/v1"
HEADERS       = {"apikey": SUPABASE_ANON, "Authorization": f"Bearer {SUPABASE_ANON}"}

REPO_ROOT     = pathlib.Path(__file__).parent.parent
MNEMOS_DIR    = REPO_ROOT / "mnemos"


def read_local_memories(query: str, limit: int = 8) -> tuple[list, str]:
    """Read from memory/mnemos/memories/recent.json — no credentials needed."""
    recent_path = MNEMOS_DIR / "memories" / "recent.json"
    try:
        data = json.loads(recent_path.read_text())
        memories = data.get("memories", [])
    except Exception:
        return [], "local_missing"
    if not memories:
        return [], "local_empty"
    q = query.lower()
    scored = []
    for m in memories:
        text  = (m.get("text") or "").lower()
        tags  = " ".join(m.get("tags") or []).lower()
        words = [w for w in q.split() if len(w) > 2]
        hits  = sum(1 for w in words if w in text or w in tags)
        if hits:
            scored.append((hits, m))
    scored.sort(key=lambda x: x[0], reverse=True)
    results = [m for _, m in scored[:limit]]
    if not results:
        results = memories[:limit]
    return results, "local"


def semantic_search(query: str, limit: int = 8, source_type: str = None) -> tuple[list, str]:
    """Search via mnemos-search (semantic if API key present, keyword fallback)."""
    payload = {"query": query, "limit": limit}
    if source_type:
        payload["source_type"] = source_type
    data = json.dumps(payload).encode()
    req = urllib.request.Request(
        SEARCH_FN, data=data,
        headers={"Content-Type": "application/json", "Authorization": f"Bearer {SUPABASE_ANON}"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            body = json.loads(resp.read())
            return body.get("results", []), body.get("method", "unknown")
    except Exception:
        return [], "error"


def recall_legacy(payload: dict) -> list:
    """Legacy mnemos-recall fallback (keyword-only)."""
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
    req = urllib.request.Request(f"{REST_BASE}/consensus_proposals?{params}", headers=HEADERS)
    try:
        with urllib.request.urlopen(req, timeout=8) as resp:
            return json.loads(resp.read())
    except Exception:
        return []


def query_prometheus(limit: int = 5, min_weight: float = 0.0) -> list:
    params = f"select=decision,rationale,gl_law,tags,eris_weight,timestamp&raven_approved=eq.true&eris_weight=gte.{min_weight}&order=eris_weight.desc,timestamp.desc&limit={limit}"
    req = urllib.request.Request(f"{REST_BASE}/prometheus_log?{params}", headers=HEADERS)
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

    # Tier 1: repo files (no credentials needed — readable by any model)
    results, method = read_local_memories(query, limit=8)

    # Tier 2: Supabase semantic search (pgvector cosine similarity, keyword fallback)
    if not results or method in ("local_missing", "local_empty"):
        results, method = semantic_search(query, limit=8)

    # Tier 3: legacy recall
    if not results:
        results = recall_legacy({"query": query, "limit": 8})
        method = "legacy"

    gov_keywords = ["gold law", "gl", "decision", "constraint", "governance",
                    "architecture", "gl2", "gl5", "gl6", "gl7", "gl9"]
    is_gov = any(k in query.lower() for k in gov_keywords)

    # For governance queries: supplement with decision-typed memories
    if is_gov:
        extra, _ = semantic_search(query, limit=5, source_type="decision")
        seen = {r.get("text") for r in results}
        for d in extra:
            if d.get("text") not in seen:
                results.append(d)

    method_label = {
        "local": "LOCAL (repo)", "local_missing": "LOCAL→MISSING", "local_empty": "LOCAL→EMPTY",
        "semantic": "SEMANTIC", "fulltext": "FULLTEXT", "recent": "RECENT",
        "keyword": "KEYWORD", "legacy": "LEGACY", "error": "ERROR",
    }.get(method, method.upper())
    print(f"  method: {method_label}")
    print()

    if not results:
        print("No memories found for that query.")
        print("MNEMOS may be unreachable or no matching records exist.")
    else:
        for m in results:
            ts  = (m.get("timestamp") or "")[:10]
            src = (m.get("source_type") or "memory")[:14]
            txt = (m.get("text") or "").replace("\n", " ")
            tags = m.get("tags") or []
            sim  = m.get("similarity")
            sim_str = f" {sim:.2f}" if sim is not None else ""
            tag_str = f" [{', '.join(tags[:3])}]" if tags else ""
            print(f"[{src} {ts}{sim_str}]{tag_str}")
            print(f"  {txt[:200]}")
            print()

    if is_gov:
        open_proposals = query_proposals(limit=3)
        if open_proposals:
            print("─" * 50)
            print("OPEN PROPOSALS (GNPL):")
            for p in open_proposals:
                ptype = p.get("proposal_type") or "?"
                ts    = (p.get("created_at") or "")[:10]
                pid   = p.get("patch_id") or ""
                pid_s = f" [{pid}]" if pid else ""
                desc  = ((p.get("payload") or {}).get("description") or "")[:120]
                print(f"  [{ptype} {ts}]{pid_s} {desc}")
            print()

        decisions_pg = query_prometheus(limit=5, min_weight=0.8)
        if decisions_pg:
            print("─" * 50)
            print("PROMETHEUS RECORD — active governance decisions:")
            for d in decisions_pg:
                gl  = d.get("gl_law") or "—"
                ts  = (d.get("timestamp") or "")[:10]
                w   = d.get("eris_weight") or 0
                dec = (d.get("decision") or "").replace("\n", " ")
                tags = d.get("tags") or []
                tag_str = f" [{', '.join(tags[:3])}]" if tags else ""
                print(f"  [{gl} w={w:.2f} {ts}]{tag_str}")
                print(f"    {dec[:180]}")
                print()

    print("─" * 50)
    print(f"{len(results)} memories recalled from MNEMOS.")


if __name__ == "__main__":
    main()
