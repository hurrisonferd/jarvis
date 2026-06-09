"""Emit idempotent upsert SQL to sync the JD/JNL substrate into the Supabase mirror.

Files are truth; this regenerates the rows for public.jnl_registry + public.jd_entries.
Usage:  python yggdrasil/tools/sync_supabase.py > /tmp/jd_load.sql
Then run via the Supabase MCP execute_sql (or psql with the service role).
"""
from __future__ import annotations
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
JD = ROOT / "yggdrasil" / "jd" / "entries"
REG = ROOT / "yggdrasil" / "lal" / "address-registry.json"
FM = re.compile(r"^---\n(.*?)\n---\n(.*)", re.DOTALL)


def arr(xs) -> str:
    if not xs:
        return "'{}'"
    return "'{" + ",".join('"' + x.replace('"', '\\"') + '"' for x in xs) + "}'"


def q(s) -> str:
    return "'" + (s or "").replace("'", "''") + "'"


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


def main() -> None:
    reg = json.loads(REG.read_text())["records"]
    reg_vals = [
        f"({q(r['jnl'])},{q(r['name'])},{q(r['type'])},{q(r.get('class',''))},{q(r.get('tier',''))},"
        f"{q(r.get('owner',''))},{q(r['location'])},{arr(r['tags'])},{arr(r['anchors'])},"
        f"{q(r['state'])},{q(r.get('status','ACTIVE'))},{q(r['created'])},{q(r['updated'])})"
        for r in reg
    ]
    jd_vals = []
    for f in sorted(JD.glob("*.md")):
        e = parse(f.read_text())
        jd_vals.append(
            f"({q(e['jnl'])},{q(e['name'])},{q(e['type'])},{q(e.get('class',''))},{q(e.get('tier',''))},"
            f"{q(e.get('owner',''))},{q(e['authority'])},{q(e['definition'])},{q(e['purpose'])},"
            f"{q(e.get('source',''))},{arr(e.get('related',[]))},{arr(e.get('references',[]))},"
            f"{arr(e.get('tags',[]))},{arr(e.get('ref',[]))},"
            f"{q(e.get('status','ACTIVE'))},{q(e['created'])},{q(e['updated'])})"
        )

    print("insert into public.jnl_registry (jnl,name,type,class,tier,owner,location,tags,anchors,state,status,created,updated) values")
    print(",\n".join(reg_vals))
    print("on conflict (jnl) do update set name=excluded.name,type=excluded.type,class=excluded.class,"
          "tier=excluded.tier,owner=excluded.owner,location=excluded.location,tags=excluded.tags,"
          "anchors=excluded.anchors,state=excluded.state,status=excluded.status,"
          "created=excluded.created,updated=excluded.updated,synced_at=now();\n")

    print("insert into public.jd_entries (jnl,name,type,class,tier,owner,authority,definition,purpose,source,related,cross_refs,tags,ref,status,created,updated) values")
    print(",\n".join(jd_vals))
    print("on conflict (jnl) do update set name=excluded.name,type=excluded.type,class=excluded.class,"
          "tier=excluded.tier,owner=excluded.owner,authority=excluded.authority,definition=excluded.definition,"
          "purpose=excluded.purpose,source=excluded.source,related=excluded.related,cross_refs=excluded.cross_refs,"
          "tags=excluded.tags,ref=excluded.ref,status=excluded.status,"
          "created=excluded.created,updated=excluded.updated,synced_at=now();")


if __name__ == "__main__":
    main()
