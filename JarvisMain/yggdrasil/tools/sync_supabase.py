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
            "seq": int(e["seq"]) if str(e.get("seq", "")).isdigit() else None,
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
        f"{arr(e['tags'])},{arr(e['ref'])},{arr(e['aliases'])},{e['seq'] if e['seq'] is not None else 'null'},"
        f"{q(e['status'])},{q(e['created'])},{q(e['updated'])})"
        for e in jd_rows()
    ]

    print("insert into public.jnl_registry (jnl,name,type,class,tier,owner,parent,location,tags,anchors,state,status,created,updated) values")
    print(",\n".join(reg_vals))
    print("on conflict (jnl) do update set name=excluded.name,type=excluded.type,class=excluded.class,"
          "tier=excluded.tier,owner=excluded.owner,parent=excluded.parent,location=excluded.location,tags=excluded.tags,"
          "anchors=excluded.anchors,state=excluded.state,status=excluded.status,"
          "created=excluded.created,updated=excluded.updated,synced_at=now();\n")

    print("insert into public.jd_entries (jnl,name,type,class,tier,owner,parent,authority,definition,purpose,source,related,cross_refs,tags,ref,aliases,seq,status,created,updated) values")
    print(",\n".join(jd_vals))
    print("on conflict (jnl) do update set name=excluded.name,type=excluded.type,class=excluded.class,"
          "tier=excluded.tier,owner=excluded.owner,parent=excluded.parent,authority=excluded.authority,definition=excluded.definition,"
          "purpose=excluded.purpose,source=excluded.source,related=excluded.related,cross_refs=excluded.cross_refs,"
          "tags=excluded.tags,ref=excluded.ref,aliases=excluded.aliases,seq=excluded.seq,status=excluded.status,"
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


def _upsert(base: str, table: str, payload: list[dict] | dict, headers: dict) -> tuple[bool, str]:
    """One PostgREST upsert. Returns (ok, detail). detail is the server error on failure."""
    req = urllib.request.Request(
        f"{base}/rest/v1/{table}?on_conflict=jnl",
        data=json.dumps(payload).encode(), headers=headers, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            return True, f"HTTP {r.status}"
    except urllib.error.HTTPError as e:
        body = ""
        try:
            body = e.read().decode()[:300]
        except Exception:
            pass
        return False, f"HTTP {e.code} {body}"
    except urllib.error.URLError as e:
        return False, str(e)


def push() -> int:
    """Mirror git → Supabase, batch-first with a per-row fallback so ONE bad row can no
    longer freeze a whole table silently (the 2026-06-11 jd_entries freeze). Any row that
    still cannot land is reported by jnl and forces a non-zero exit so CI goes red."""
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
    failures: list[str] = []  # "table/jnl: detail" — anything that never landed
    for table, rows in (("jnl_registry", reg_rows()), ("jd_entries", jd_rows())):
        base = None
        # Pick a reachable base URL with the full-batch upsert (the happy path).
        for cand in candidates:
            ok, detail = _upsert(cand, table, rows, headers)
            if ok:
                base = cand
                print(f"sync_supabase: {table} <- {len(rows)} rows ({detail}) via {cand.split('//')[1].split('.')[0][:4]}…")
                break
            print(f"sync_supabase: {table} batch on {cand.split('//')[1].split('.')[0][:4]}… failed ({detail})")
            time.sleep(1)
        if base:
            continue
        # Batch failed on every URL — almost always ONE poison row. Degrade to per-row on the
        # secret-derived URL so the other ~200 rows still land, and name the row(s) that don't.
        base = candidates[0]
        print(f"sync_supabase: {table} — falling back to per-row upsert to isolate the bad row(s)…")
        landed = 0
        for row in rows:
            ok, detail = _upsert(base, table, row, headers)
            if ok:
                landed += 1
            else:
                failures.append(f"{table}/{row.get('jnl', '?')}: {detail}")
        print(f"sync_supabase: {table} per-row — {landed}/{len(rows)} landed, {len(rows) - landed} failed")
    if failures:
        print("sync_supabase: ROWS THAT NEVER LANDED (mirror is incomplete):")
        for f in failures:
            print(f"  - {f}")
        raise SystemExit(f"sync_supabase: {len(failures)} row(s) failed to mirror — see above.")
    return 0


if __name__ == "__main__":
    raise SystemExit(push() if "--push" in sys.argv[1:] else emit_sql())
