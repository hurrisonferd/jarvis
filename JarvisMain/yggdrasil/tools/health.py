#!/usr/bin/env python3
"""health.py — JD vitality audit: are governed objects actually USED, not just stored?

validate.py proves the dex is structurally sound (grammar, GL12, mirror). This proves it is
ALIVE: it flags orphans, isolated dead-ends, ruleless JIPs, stewardless subsystems, and
registry/truth drift. Where validate fails the build, health only WARNS — vitality is a
signal for Jarvis + Ayre to act on (peer audit), not a hard gate. Stdlib only; read-only.

Run: python3 JarvisMain/yggdrasil/tools/health.py
"""
from __future__ import annotations
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
LAL = ROOT / "JarvisMain" / "yggdrasil" / "lal"
ROOTS = {"ARCH-YGG-CORE-0001"}  # the world-tree root legitimately has no parent


def load():
    recs = json.loads((LAL / "address-registry.json").read_text()).get("records", [])
    g = json.loads((LAL / "graph.json").read_text())
    edges = g.get("edges", [])
    return recs, edges


def main() -> int:
    recs, edges = load()
    by = {r["jnl"]: r for r in recs}
    # incoming/outgoing reference sets (parent + related/cross-ref edges)
    has_parent = {r["jnl"]: bool(r.get("parent")) for r in recs}
    has_child = {e["target"] for e in edges if e.get("type") == "parent"} | \
                {r["parent"] for r in recs if r.get("parent")}
    referenced = {e["target"] for e in edges} | {e["source"] for e in edges} | has_child

    orphans, isolated, ruleless_jip, stewardless, open_tasks = [], [], [], [], []
    for r in recs:
        jnl, typ, status = r["jnl"], r.get("type", ""), r.get("status", "")
        if jnl in ROOTS:
            continue
        if not has_parent[jnl]:
            orphans.append(jnl)
        if not has_parent[jnl] and jnl not in referenced:
            isolated.append(jnl)
        if typ == "JIP" and not (r.get("parent") or jnl in referenced):
            ruleless_jip.append(jnl)        # a rule/overlay attached to nothing = dead
        if jnl.startswith("ARCH-") and jnl.endswith("-CORE-0001") and not r.get("steward") \
           and jnl not in ROOTS and "JD" not in jnl:
            stewardless.append(jnl)         # substrate without a tending god
        if status == "TASK":
            open_tasks.append((jnl, r.get("name", "")))

    flags = len(orphans) + len(isolated) + len(ruleless_jip) + len(stewardless)
    lines, log = [], print

    def section(title, items, fmt=lambda x: x):
        lines.append(f"\n## {title} ({len(items)})")
        lines.extend(f"- {fmt(it)}" for it in items) if items else lines.append("- ✓ none")

    lines.append(f"# JD Health — vitality of the governed record")
    lines.append(f"\n_{len(recs)} governed objects, {len(edges)} edges · health WARNS, never blocks "
                 f"(validate.py is the hard gate). Read alongside omnivision + the wiring map._")
    section("Orphans (no parent — should join the family tree)", orphans)
    section("Isolated (no parent, nothing references them — dead-ends)", isolated)
    section("Ruleless JIPs (a rule attached to nothing)", ruleless_jip)
    section("Stewardless substrate (no god tending it)", stewardless)
    section("Open tasks (in-flight work, aging watch)", open_tasks, lambda t: f"`{t[0]}` {t[1]}")
    lines.append(f"\n**VITALITY:** {flags} structural flag(s) + {len(open_tasks)} open task(s).")
    report = "\n".join(lines) + "\n"

    (LAL / "HEALTH.md").write_text(report)   # connector-readable: Jarvis/Ayre are Raven's eyes
    log(report)
    log(f"health: report -> JarvisMain/yggdrasil/lal/HEALTH.md")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
