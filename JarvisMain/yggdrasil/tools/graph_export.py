"""YVG — Yggdrasil Visual Graph: export the dex as a nodes+edges graph.

The data layer of the visualizer (packet 4). Reads the JD entries + LAL registry and
emits a renderer-agnostic graph (D3 / Three.js / the web UI can all consume it). Derived
only — never authoritative (JMS law). Writes JarvisMain/yggdrasil/lal/graph.json.

Run from repo root:  python JarvisMain/yggdrasil/tools/graph_export.py
"""
from __future__ import annotations
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
JD_DIR = ROOT / "JarvisMain" / "yggdrasil" / "jd" / "entries"
OUT = ROOT / "JarvisMain" / "yggdrasil" / "lal" / "graph.json"
FM = re.compile(r"^---\n(.*?)\n---", re.DOTALL)


def fm(text: str) -> dict:
    m = FM.match(text)
    out = {}
    for line in (m.group(1).splitlines() if m else []):
        if ":" not in line:
            continue
        k, v = line.split(":", 1)
        v = v.strip()
        if v.startswith("[") and v.endswith("]"):
            v = [x.strip() for x in v[1:-1].split(",") if x.strip()]
        out[k.strip()] = v
    return out


def main() -> None:
    nodes, edges = [], []
    for f in sorted(JD_DIR.glob("*.md")):
        e = fm(f.read_text())
        jnl = e.get("jnl", "")
        if not jnl:
            continue
        nodes.append({
            "id": jnl, "name": e.get("name", ""), "domain": jnl.split("-")[0],
            "class": e.get("class", ""), "tier": e.get("tier", ""),
            "status": e.get("status", ""), "owner": e.get("owner", ""),
        })
        for rel in e.get("related", []) or []:
            edges.append({"source": jnl, "target": rel, "type": "related"})
        for ref in e.get("references", []) or []:
            edges.append({"source": jnl, "target": ref, "type": "reference"})
        par = e.get("parent", "")
        if par and isinstance(par, str):
            edges.append({"source": jnl, "target": par, "type": "parent"})

    ids = {n["id"] for n in nodes}
    dangling = [edge for edge in edges if edge["target"] not in ids]
    graph = {
        "note": "Derived graph of the dex (YVG data layer). Rebuild with tools/graph_export.py.",
        "counts": {"nodes": len(nodes), "edges": len(edges),
                   "main": sum(n["tier"] == "MAIN" for n in nodes),
                   "side": sum(n["tier"] == "SIDE" for n in nodes)},
        "nodes": nodes, "edges": edges,
    }
    OUT.write_text(json.dumps(graph, indent=2) + "\n")
    print(f"graph: {len(nodes)} nodes, {len(edges)} edges -> {OUT.relative_to(ROOT)}")
    if dangling:
        print(f"  ! {len(dangling)} edge(s) point to unknown nodes: "
              + ", ".join(sorted({e['target'] for e in dangling})))


if __name__ == "__main__":
    main()
