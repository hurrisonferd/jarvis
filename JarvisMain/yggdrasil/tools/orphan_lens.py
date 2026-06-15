#!/usr/bin/env python3
"""orphan_lens.py — the Grimoire's conscience chapter.

HEALTH.md *lists* orphans. This lens *judges* them: for every object with no parent it
proposes a disposition — legitimate root / attach to an existing parent / archive / needs a
Raven decision — so the 43-orphan debt becomes a worklist, not a number. It writes PROPOSALS
only (GL2: JARVIS proposes, Raven commits). Nothing here mutates the tree.

A page is a projection over truth: reads the address registry, writes lal/ORPHAN-LENS.md.
Invoked at the seed tail (before grimoire, so the book can mark this lens live). Stdlib only.
"""
from __future__ import annotations
import json
from datetime import datetime, timezone
from pathlib import Path
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[3]
LAL = ROOT / "JarvisMain" / "yggdrasil" / "lal"
OUT = LAL / "ORPHAN-LENS.md"


def classify(o: dict, by: dict) -> tuple[str, str]:
    """Return (verdict, detail). Verdicts: ROOT / ATTACH / ARCHIVE / DECIDE."""
    jnl = o["jnl"]
    parts = jnl.split("-")
    dom, sys = parts[0], (parts[1] if len(parts) > 1 else "")
    status = o.get("status", "")
    if status in ("ARCHIVED", "INACTIVE", "DEPRECATED"):
        return ("ARCHIVE", f"status is {status} — autosort to the archive lane")
    if jnl.endswith("IDX-0001"):
        return ("ROOT", "index object — legitimate top-level (no parent by design)")
    if dom == "GS" or jnl.endswith("CORE-0001"):
        return ("ROOT", "core/system root — legitimate top-level")
    # an obvious same-system CORE to hang under (e.g. ARCH-JMS-SPEC → ARCH-JMS-CORE)
    core = f"{dom}-{sys}-CORE-0001"
    if core in by and core != jnl:
        return ("ATTACH", core)
    if dom == "PROJ":
        bio = f"PROJ-{sys}-BIO-0001"
        if jnl == bio:
            return ("DECIDE", "project root — no Projects index exists; propose minting PROJ-IDX-0001 to parent all project BIOs")
        if bio in by:
            return ("ATTACH", bio)
        return ("DECIDE", f"project artifact with no {bio} — confirm the project node")
    if dom == "AUD":
        return ("ARCHIVE", "point-in-time review — parent to an audit index or archive once read")
    # a domain root to hang under, if one exists
    for cand in (f"{dom}-CAN-CORE-0001", f"{dom}-CON-CORE-0001", f"{dom}-PROC-CORE-0001"):
        if cand in by and cand != jnl:
            return ("ATTACH", f"{cand} (domain root — confirm fit)")
    return ("DECIDE", "no obvious parent — needs a placement decision")


def build() -> str:
    recs = json.loads((LAL / "address-registry.json").read_text())["records"]
    by = {r["jnl"]: r for r in recs}
    orphans = [r for r in recs if not r.get("parent")]
    verdicts: dict[str, list[tuple[dict, str]]] = {"ATTACH": [], "DECIDE": [], "ARCHIVE": [], "ROOT": []}
    for o in sorted(orphans, key=lambda x: x["jnl"]):
        v, d = classify(o, by)
        verdicts[v].append((o, d))
    now = datetime.now(timezone.utc)
    stamp = f"{now.strftime('%Y-%m-%dT%H:%M:%SZ')} ({now.astimezone(ZoneInfo('America/New_York')).strftime('%Y-%m-%d %H:%M %Z')})"
    L = [
        "# Orphan Lens — the debt, made into a worklist",
        "",
        f"_generated: {stamp} · projected from the address registry — do not hand-edit; run "
        "`orphan_lens.py` (auto at seed tail). **Proposals only (GL2): Raven commits.**_",
        "",
        f"{len(orphans)} orphan(s) with no parent. Verdicts: "
        f"**{len(verdicts['ATTACH'])} attach** (obvious parent exists) · "
        f"**{len(verdicts['DECIDE'])} decide** (needs your call) · "
        f"**{len(verdicts['ARCHIVE'])} archive** · "
        f"**{len(verdicts['ROOT'])} root** (legitimate top-level, leave as-is).",
        "",
        "## ATTACH — an existing parent is right there (low-risk prune)",
        "Set `parent:` to the suggestion, reseed; the JNL never changes (JMS law).",
        "",
        "| orphan | name | suggested parent |",
        "|---|---|---|",
    ]
    L += [f"| `{o['jnl']}` | {o.get('name','')[:42]} | `{d}` |" for o, d in verdicts["ATTACH"]] or ["| — | none | — |"]
    L += ["", "## DECIDE — needs a Raven verdict (a missing root, mostly)", "",
          "| orphan | name | question |", "|---|---|---|"]
    L += [f"| `{o['jnl']}` | {o.get('name','')[:42]} | {d} |" for o, d in verdicts["DECIDE"]] or ["| — | none | — |"]
    L += ["", "## ARCHIVE — done or point-in-time (move to the archive lane)", "",
          "| orphan | name | why |", "|---|---|---|"]
    L += [f"| `{o['jnl']}` | {o.get('name','')[:42]} | {d} |" for o, d in verdicts["ARCHIVE"]] or ["| — | none | — |"]
    L += ["", "## ROOT — legitimate top-level (no action)", "",
          ", ".join(f"`{o['jnl']}`" for o, _ in verdicts["ROOT"]) or "—", "",
          "---",
          "_The single biggest unlock: most PROJ orphans want one new root. Mint `PROJ-IDX-0001` "
          "(Projects Registry), parent the project BIOs to it, and the orphan count drops hard "
          "in one governed move._", ""]
    return "\n".join(L) + "\n"


def main() -> int:
    import re
    new = build()
    if OUT.exists():
        rx = re.compile(r"^_generated:.*$", re.M)
        if rx.sub("", OUT.read_text()) == rx.sub("", new):
            new = OUT.read_text()
    OUT.write_text(new)
    print(f"orphan-lens: {OUT.relative_to(ROOT)} regenerated.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
