#!/usr/bin/env python3
"""topology_lens.py — the system's shape, projected from the graph that already exists.

GPT wanted an "Omni-Map / Canonical System Graph as a first-class object." It already is one:
graph.json (every governed object = a node, parent/related/steward = edges). The missing piece was
never the map — it's the QUERIES over it. This lens answers "show me the shape": the hubs
(highest-connected), the leaves, the isolated, and how the edges distribute. Self-mapping over the
existing graph, not a parallel Omni-Map.

Reads JarvisMain/yggdrasil/lal/graph.json. Writes lal/TOPOLOGY-LENS.md. Stdlib only.
Runs at the seed tail. A registered grimoire lens ('Topology').
"""
from __future__ import annotations
import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[3]
LAL = ROOT / "JarvisMain" / "yggdrasil" / "lal"
OUT = LAL / "TOPOLOGY-LENS.md"


def build() -> str:
    g = json.loads((LAL / "graph.json").read_text())
    nodes = {n["id"]: n for n in g.get("nodes", [])}
    edges = g.get("edges", [])
    deg = Counter()
    indeg = Counter()
    outdeg = Counter()
    for e in edges:
        s, t = e.get("source"), e.get("target")
        if s in nodes: outdeg[s] += 1; deg[s] += 1
        if t in nodes: indeg[t] += 1; deg[t] += 1
    isolated = sorted(j for j in nodes if deg[j] == 0)
    hubs = sorted(nodes, key=lambda j: deg[j], reverse=True)[:12]
    etypes = Counter(e.get("type", "?") for e in edges)
    dom_nodes = Counter(n.get("domain", "?") for n in nodes.values())
    now = datetime.now(timezone.utc)
    stamp = f"{now.strftime('%Y-%m-%dT%H:%M:%SZ')} ({now.astimezone(ZoneInfo('America/New_York')).strftime('%Y-%m-%d %H:%M %Z')})"
    L = [
        "# Topology Lens — the shape of the system",
        "",
        f"_generated: {stamp} · projected from `graph.json` (the canonical graph that already exists). "
        "GPT's 'Omni-Map' is this graph; this lens is the query over it — hubs, leaves, isolation, edges._",
        "",
        f"**{len(nodes)} nodes · {len(edges)} edges · {len(isolated)} isolated · "
        f"avg degree {round(2*len(edges)/max(1,len(nodes)),2)}.**",
        "",
        "## Hubs — the most-connected nodes (the system's load-bearing spine)",
        "| node | degree | in | out | domain |",
        "|---|---|---|---|---|",
    ]
    L += [f"| `{j}` {nodes[j].get('name','')[:28]} | {deg[j]} | {indeg[j]} | {outdeg[j]} | {nodes[j].get('domain','')} |"
          for j in hubs]
    L += [
        "",
        "## Isolated — nodes with NO edges (in or out): unreachable, invisible to the loop",
        ", ".join(f"`{j}`" for j in isolated) or "✓ none — every node is connected.",
        "",
        "## Edge types (the relationships that bind the graph)",
        "| type | count |", "|---|---|",
    ]
    L += [f"| {t} | {c} |" for t, c in etypes.most_common()]
    L += [
        "",
        "## Nodes by domain",
        "| domain | nodes |", "|---|---|",
    ]
    L += [f"| {d} | {c} |" for d, c in sorted(dom_nodes.items())]
    L += ["",
          "_The map was never missing — it's `graph.json`. What this adds is the answer to "
          "'show me the shape.' Next queries (Pressure/Drift/Resilience) are more lenses over the "
          "same graph, not new systems._", ""]
    return "\n".join(L) + "\n"


def main() -> int:
    import re
    new = build()
    if OUT.exists():
        rx = re.compile(r"^_generated:.*$", re.M)
        if rx.sub("", OUT.read_text()) == rx.sub("", new):
            new = OUT.read_text()
    OUT.write_text(new)
    print(f"topology-lens: {OUT.relative_to(ROOT)} regenerated.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
