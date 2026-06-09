"""dex — query the dex like a dex (JQL-lite, the CLI realization of IMPL-JQL-CORE-0001).

Usage:
  dex.py find [--domain D] [--class C] [--tier T] [--status S] [--tag T] [--text SUBSTR]
  dex.py show <JNL>                 # print the JD entry
  dex.py related <JNL> [--depth N]  # walk the semantic web (both directions)
  dex.py stats                      # the YGG manifest + edge density

Reads only derived mirrors (registry + entries + graph) — never mutates (JMS).
Run from repo root:  python JarvisMain/yggdrasil/tools/dex.py find --tag governance
"""
from __future__ import annotations
import argparse
import json
from collections import defaultdict, deque
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
LAL = ROOT / "JarvisMain" / "yggdrasil" / "lal"
JD_DIR = ROOT / "JarvisMain" / "yggdrasil" / "jd" / "entries"


def records() -> list[dict]:
    return json.loads((LAL / "address-registry.json").read_text())["records"]


def row(r: dict) -> str:
    return f"{r['jnl']:24} {r['status']:10} {r['class']:8} {r['tier']:5} {r['name'][:34]:34} {r['location']}"


def cmd_find(a) -> int:
    out = []
    for r in records():
        if a.domain and r["jnl"].split("-")[0] != a.domain.upper():
            continue
        if a.cls and r["class"] != a.cls.upper():
            continue
        if a.tier and r["tier"] != a.tier.upper():
            continue
        if a.status and r["status"] != a.status.upper():
            continue
        if a.tag and a.tag.lower() not in [t.lower() for t in r["tags"]]:
            continue
        if a.text and a.text.lower() not in (r["name"] + " " + r["location"]).lower():
            continue
        out.append(r)
    for r in out:
        print(row(r))
    print(f"-- {len(out)} object(s)")
    return 0


def cmd_show(a) -> int:
    f = JD_DIR / f"{a.jnl}.md"
    if not f.exists():
        print(f"no JD entry for '{a.jnl}'")
        return 1
    print(f.read_text())
    return 0


def cmd_related(a) -> int:
    g = json.loads((LAL / "graph.json").read_text())
    adj: dict[str, set[str]] = defaultdict(set)
    for e in g["edges"]:
        adj[e["source"]].add(e["target"])
        adj[e["target"]].add(e["source"])
    if a.jnl not in {n["id"] for n in g["nodes"]}:
        print(f"'{a.jnl}' not in the graph")
        return 1
    names = {n["id"]: n["name"] for n in g["nodes"]}
    seen, q = {a.jnl: 0}, deque([a.jnl])
    while q:
        cur = q.popleft()
        if seen[cur] >= a.depth:
            continue
        for nxt in sorted(adj[cur]):
            if nxt not in seen:
                seen[nxt] = seen[cur] + 1
                q.append(nxt)
    for jnl, d in sorted(seen.items(), key=lambda kv: (kv[1], kv[0])):
        if d:
            print(f"  {'· ' * d}{jnl:24} {names.get(jnl, '?')}")
    print(f"-- {len(seen) - 1} object(s) within depth {a.depth} of {a.jnl}")
    return 0


def cmd_family(a) -> int:
    """Transitive children via parent edges: 'JFS-compliant' = this whole listing."""
    recs = records()
    kids: dict[str, list[str]] = defaultdict(list)
    byjnl = {r["jnl"]: r for r in recs}
    for r in recs:
        if r.get("parent"):
            kids[r["parent"]].append(r["jnl"])
    if a.jnl not in byjnl:
        print(f"'{a.jnl}' not in the registry")
        return 1
    count = 0

    def walk(jnl: str, depth: int) -> None:
        nonlocal count
        for c in sorted(kids.get(jnl, [])):
            print(f"  {'· ' * depth}{c:24} {byjnl[c]['name']}")
            count += 1
            walk(c, depth + 1)

    print(f"{a.jnl} — {byjnl[a.jnl]['name']}")
    walk(a.jnl, 1)
    print(f"-- family of {count} under {a.jnl}")
    return 0


def cmd_stats(a) -> int:
    print((LAL / "version.json").read_text(), end="")
    g = json.loads((LAL / "graph.json").read_text())
    linked = {e["source"] for e in g["edges"]} | {e["target"] for e in g["edges"]}
    print(f"graph: {g['counts']['nodes']} nodes, {g['counts']['edges']} edges, "
          f"{len(linked)} linked, {g['counts']['nodes'] - len(linked)} isolated")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    sub = ap.add_subparsers(dest="cmd", required=True)
    f = sub.add_parser("find")
    f.add_argument("--domain"), f.add_argument("--class", dest="cls")
    f.add_argument("--tier"), f.add_argument("--status")
    f.add_argument("--tag"), f.add_argument("--text")
    s = sub.add_parser("show")
    s.add_argument("jnl")
    r = sub.add_parser("related")
    r.add_argument("jnl"), r.add_argument("--depth", type=int, default=1)
    fam = sub.add_parser("family")
    fam.add_argument("jnl")
    sub.add_parser("stats")
    a = ap.parse_args()
    return {"find": cmd_find, "show": cmd_show, "related": cmd_related,
            "family": cmd_family, "stats": cmd_stats}[a.cmd](a)


if __name__ == "__main__":
    raise SystemExit(main())
