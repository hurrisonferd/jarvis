"""Sync the JD/JNL substrate into the Supabase mirror (JMS — files are truth).

Two modes:
  SQL (default):  python JarvisMain/yggdrasil/tools/sync_supabase.py > /tmp/jd_load.sql
                  then run via Supabase MCP execute_sql (or psql with the service role).
  --push:         POST upserts straight to PostgREST. Needs SUPABASE_URL +
                  SUPABASE_SERVICE_KEY env; skips cleanly if unset. Run by CI on
                  every push to main (yggdrasil-validate.yml `mirror` job).
"""
from __future__ import annotations
import json
import os
import re
import sys
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
JD = ROOT / "JarvisMain" / "yggdrasil" / "jd" / "entries"
REG = ROOT / "JarvisMain" / "yggdrasil" / "lal" / "address-registry.json"
FM = re.compile(r"^---\n(.*?)\n---\n(.*)", re.DOTALL)


def parse(text: str) -> dict:
    m = FM.match(text)
    fm, body = {}, m.group(2)
    for line in m.group(1).splitlines():
        if ":" not in line:
            continue
        k, v = line.split(":", 1)
        v = v.strip()
        if v.startswith("[") and v.endswith("]"):
            v = [x.strip() for x in v[1:-1].split(",") if x.strip()]
        fm[k.strip()] = v
    dfn = re.search(r"\*\*Definition:\*\*\s*(.*)", body)
    pur = re.search(r"\*\*Purpose:\*\*\s*(.*)", body)
    fm["definition"] = dfn.group(1).strip() if dfn else ""
    fm["purpose"] = pur.group(1).strip() if pur else ""
    return fm


def reg_rows() -> list[dict]:
    return [{
        "jnl": r["jnl"], "name": r["name"], "type": r["type"], "class": r.get("class", ""),
        "tier": r.get("tier", ""), "owner": r.get("owner", ""), "parent": r.get("parent", ""), "location": r["location"],
        "tags": r["tags"], "anchors": r["anchors"], "state": r["state"],
        "status": r.get("status", "ACTIVE"), "created": r["created"], "updated": r["updated"],
    } for r in json.loads(REG.read_text())["records"]]


def jd_rows() -> list[dict]:
    rows = []
    for f in sorted(JD.glob("*.md")):
        e = parse(f.read_text())
        rows.append({
            "jnl": e["jnl"], "name": e["name"], "type": e["type"], "class": e.get("class", ""),
            "tier": e.get("tier", ""), "owner": e.get("owner", ""), "parent": e.get("parent", "") if isinstance(e.get("parent"), str) else "", "authority": e["authority"],
            "definition": e["definition"], "purpose": e["purpose"], "source": e.get("source", ""),
            "related": e.get("related", []), "cross_refs": e.get("references", []),
            "tags": e.get("tags", []), "ref": e.get("ref", []),
            "aliases": e.get("aliases", []) if isinstance(e.get("aliases"), list) else [],
            "status": e.get("status", "ACTIVE"), "created": e["created"], "updated": e["updated"],
        })
    return rows


# --- SQL mode ---

def arr(xs) -> str:
    if not xs:
        return "'{}'"
    return "'{" + ",".join('"' + x.replace('"', '\\"') + '"' for x in xs) + "}'"


def q(s) -> str:
    return "'" + (s or "").replace("'", "''") + "'"


def emit_sql() -> None:
    reg_vals = [
        f"({q(r['jnl'])},{q(r['name'])},{q(r['type'])},{q(r['class'])},{q(r['tier'])},"
        f"{q(r['owner'])},{q(r['parent'])},{q(r['location'])},{arr(r['tags'])},{arr(r['anchors'])},"
        f"{q(r['state'])},{q(r['status'])},{q(r['created'])},{q(r['updated'])})"
        for r in reg_rows()
    ]
    jd_vals = [
        f"({q(e['jnl'])},{q(e['name'])},{q(e['type'])},{q(e['class'])},{q(e['tier'])},"
        f"{q(e['owner'])},{q(e['parent'])},{q(e['authority'])},{q(e['definition'])},{q(e['purpose'])},"
        f"{q(e['source'])},{arr(e['related'])},{arr(e['cross_refs'])},"
        f"{arr(e['tags'])},{arr(e['ref'])},{arr(e['aliases'])},"
        f"{q(e['status'])},{q(e['created'])},{q(e['updated'])})"
        for e in jd_rows()
    ]

    print("insert into public.jnl_registry (jnl,name,type,class,tier,owner,parent,location,tags,anchors,state,status,created,updated) values")
    print(",\n".join(reg_vals))
    print("on conflict (jnl) do update set name=excluded.name,type=excluded.type,class=excluded.class,"
          "tier=excluded.tier,owner=excluded.owner,parent=excluded.parent,location=excluded.location,tags=excluded.tags,"
          "anchors=excluded.anchors,state=excluded.state,status=excluded.status,"
          "created=excluded.created,updated=excluded.updated,synced_at=now();\n")

    print("insert into public.jd_entries (jnl,name,type,class,tier,owner,parent,authority,definition,purpose,source,related,cross_refs,tags,ref,aliases,status,created,updated) values")
    print(",\n".join(jd_vals))
    print("on conflict (jnl) do update set name=excluded.name,type=excluded.type,class=excluded.class,"
          "tier=excluded.tier,owner=excluded.owner,parent=excluded.parent,authority=excluded.authority,definition=excluded.definition,"
          "purpose=excluded.purpose,source=excluded.source,related=excluded.related,cross_refs=excluded.cross_refs,"
          "tags=excluded.tags,ref=excluded.ref,aliases=excluded.aliases,status=excluded.status,"
          "created=excluded.created,updated=excluded.updated,synced_at=now();")


# --- push mode (PostgREST upsert) ---

# The canonical project host (CLAUDE.md Services). The SUPABASE_URL secret has proven
# unreliable in shape; anything that doesn't yield a *.supabase.co host falls back here.
CANONICAL_URL = "https://oexghfsvhnggddllgvrt.supabase.co"


def norm_url(u: str) -> str:
    """Tolerate secret variants: bare host (no scheme) and bare project ref (no domain).
    Anything that still doesn't look like a Supabase host falls back to CANONICAL_URL."""
    u = u.strip().rstrip("/")
    if not u:
        return u
    if "://" not in u:
        u = f"https://{u}"
    host = u.split("://", 1)[1].split("/", 1)[0]
    if "." not in host:
        host_fixed = f"{host}.supabase.co"
        u = u.replace(host, host_fixed, 1)
        host = host_fixed
    if not u.startswith("https://") or not host.endswith(".supabase.co"):
        print(f"sync_supabase: SUPABASE_URL secret has unusable shape — using canonical project URL")
        return CANONICAL_URL
    return u


def push() -> int:
    import time
    url = norm_url(os.environ.get("SUPABASE_URL", ""))
    key = os.environ.get("SUPABASE_SERVICE_KEY", "")
    if not url or not key:
        print("sync_supabase: SUPABASE_URL / SUPABASE_SERVICE_KEY unset — skipping (mirror stays stale).")
        return 0
    headers = {
        "apikey": key, "Authorization": f"Bearer {key}",
        "Content-Type": "application/json",
        "Prefer": "resolution=merge-duplicates,return=minimal",
    }
    candidates = [url] + ([CANONICAL_URL] if url != CANONICAL_URL else [])
    for table, rows in (("jnl_registry", reg_rows()), ("jd_entries", jd_rows())):
        last_err: Exception | None = None
        done = False
        for base in candidates:  # secret-derived URL first, canonical as the safety net
            for attempt in range(2):
                req = urllib.request.Request(
                    f"{base}/rest/v1/{table}?on_conflict=jnl",
                    data=json.dumps(rows).encode(), headers=headers, method="POST")
                try:
                    with urllib.request.urlopen(req, timeout=60) as r:
                        print(f"sync_supabase: {table} <- {len(rows)} rows (HTTP {r.status}) via {base.split('//')[1].split('.')[0][:4]}…")
                    done = True
                    break
                except urllib.error.URLError as e:
                    last_err = e
                    print(f"sync_supabase: {table} attempt failed ({e}); ", end="")
                    print("retrying" if attempt == 0 else "next URL")
                    time.sleep(2)
            if done:
                break
        if not done:
            raise SystemExit(f"sync_supabase: {table} failed on all URLs: {last_err}")
    return 0


if __name__ == "__main__":
    raise SystemExit(push() if "--push" in sys.argv[1:] else emit_sql())
