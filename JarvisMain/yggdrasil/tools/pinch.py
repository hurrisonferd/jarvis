#!/usr/bin/env python3
"""pinch.py — The Pinch: the whole tree in one squeeze (the P3 world-spell).

Fuses what the other lenses see and adds the three signals they don't:
  1. DRIFT   — is the mirror behind git HEAD? how stale is the stamp? (the sync gap)
  2. DEBT vs STRUCTURE — a parentless node WITH children is a root (healthy); a parentless node
     with NO children is real debt. health.py conflates them; the Pinch separates them so the
     system never mistakes its own trunk for rot (Ayre's law: tell debt from structure).
  3. BLOAT   — GL7's never-enforced clause: near-duplicate names within a domain = consolidation
     candidates. Conservative + clearly hedged (proposals only, GL2) — most matches are fine.

Where validate.py is the hard gate and health.py warns, the Pinch *decides what deserves
attention*. Stdlib only; read-only; proposals only. Run: python3 .../tools/pinch.py
"""
from __future__ import annotations
import json
import re
import subprocess
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
LAL = ROOT / "JarvisMain" / "yggdrasil" / "lal"
ROOTS = {"ARCH-YGG-CORE-0001"}  # the world-tree root legitimately anchors everything
STOP = {"jarvis", "the", "a", "of", "and", "to", "system", "core"}
BLOAT_THRESHOLD = 0.67  # name-token Jaccard; high on purpose — flag only strong look-alikes


def _git(*args: str) -> str:
    try:
        r = subprocess.run(["git", *args], cwd=ROOT, capture_output=True, text=True)
        return r.stdout.strip() if r.returncode == 0 else ""
    except Exception:
        return ""


def _tokens(name: str) -> set[str]:
    return {t for t in re.findall(r"[a-z0-9]+", name.lower()) if t not in STOP and len(t) > 1}


def main() -> int:
    recs = json.loads((LAL / "address-registry.json").read_text()).get("records", [])
    fresh = json.loads((LAL / "global-mirror.json").read_text()).get("freshness", {})
    parents = {r["parent"] for r in recs if r.get("parent")}

    structural_roots, debt_orphans, stewardless = [], [], []
    by_domain: dict[str, list[dict]] = {}
    open_tasks = 0
    for r in recs:
        jnl = r["jnl"]
        by_domain.setdefault(jnl.split("-")[0], []).append(r)
        if r.get("status") == "TASK":
            open_tasks += 1
        if jnl.startswith("ARCH-") and jnl.endswith("-CORE-0001") and not r.get("steward") \
           and jnl not in ROOTS and "JD" not in jnl:
            stewardless.append(jnl)
        if not r.get("parent") and jnl not in ROOTS:
            # structure = anchors children OR is itself an index/registry/core root (GL13: new
            # domain roots auto-classify, no allowlist to maintain). Everything else is debt.
            is_struct = jnl in parents or r.get("type", "") in {"IDX", "REG", "CORE"}
            (structural_roots if is_struct else debt_orphans).append((jnl, r.get("name", "")))

    # DRIFT — mirror stamp vs the live tree.
    src = fresh.get("source_commit", "")
    head = _git("rev-parse", "--short", "HEAD")
    behind = _git("rev-list", "--count", f"{src}..HEAD") if src and head else ""
    in_sync = src and head and head.startswith(src) or behind == "0"
    age = ""
    try:
        gen = datetime.fromisoformat(fresh["generated_at_utc"].replace("Z", "+00:00"))
        mins = (datetime.now(timezone.utc) - gen).total_seconds() / 60
        age = f"{mins:.0f} min" if mins < 90 else f"{mins/60:.1f} h"
    except Exception:
        pass

    # BLOAT — near-duplicate names within a domain, different parents (GL7 candidates).
    bloat: list[str] = []
    for dom, items in by_domain.items():
        for i in range(len(items)):
            for j in range(i + 1, len(items)):
                a, b = items[i], items[j]
                if a.get("parent") and a.get("parent") == b.get("parent"):
                    continue  # same-family siblings are a designed set, not bloat
                ta, tb = _tokens(a.get("name", "")), _tokens(b.get("name", ""))
                if not ta or not tb:
                    continue
                jac = len(ta & tb) / len(ta | tb)
                if jac >= BLOAT_THRESHOLD:
                    bloat.append(f"`{a['jnl']}` ~ `{b['jnl']}` ({a.get('name','')} / {b.get('name','')}) — {jac:.0%} name overlap")

    L: list[str] = []
    now = datetime.now(timezone.utc)
    L.append("# The Pinch — the whole tree in one squeeze")
    L.append(f"\n_generated {now:%Y-%m-%d %H:%M} UTC · the world-spell (P3): drift + debt + bloat, "
             f"telling structure from debt (GL13/GL7). Proposals only (GL2); not authoritative — "
             f"the source is the tree._")

    L.append("\n## 1. Drift — mirror vs the live tree")
    L.append(f"- mirror commit `{src or '?'}` · git HEAD `{head or '?'}` · "
             + ("**IN SYNC**" if in_sync else f"**BEHIND by {behind or '?'} commit(s)** — reseed/mirror to refresh"))
    L.append(f"- mirror stamp age: {age or 'unknown'}")

    L.append(f"\n## 2. Structure — healthy, NOT debt ({len(structural_roots)})")
    L.append("_parentless but anchoring children — these are the trunk; leave them._")
    L.extend(f"- `{j}` {n}" for j, n in sorted(structural_roots)) if structural_roots else L.append("- ✓ none")

    flags = len(debt_orphans) + len(stewardless)
    L.append(f"\n## 3. Debt — act ({flags})")
    L.append(f"\n**Real orphans** (no parent, no children — unrooted) ({len(debt_orphans)})")
    L.extend(f"- `{j}` {n}" for j, n in sorted(debt_orphans)) if debt_orphans else L.append("- ✓ none")
    L.append(f"\n**Stewardless substrate** (no god tending it) ({len(stewardless)})")
    L.extend(f"- `{j}`" for j in sorted(stewardless)) if stewardless else L.append("- ✓ none")

    L.append(f"\n## 4. Bloat watch — GL7 candidates, review only ({len(bloat)})")
    L.append("_high name overlap across families. Most are legitimately distinct — this is a prompt to look, not a verdict._")
    L.extend(f"- {b}" for b in bloat) if bloat else L.append("- ✓ none above threshold")

    L.append("\n## 5. Load")
    L.append(f"- {len(recs)} governed objects · {open_tasks} open tasks · {len(by_domain)} domains")

    verdict = "HEALTHY" if flags == 0 and in_sync else ("DRIFT" if not in_sync else "NEEDS A CONSOLIDATION PASS")
    L.append("\n## Verdict")
    L.append(f"- structure: {len(structural_roots)} roots (coherent) · debt: {flags} item(s) · "
             f"drift: {'in sync' if in_sync else 'behind'} · bloat candidates: {len(bloat)}")
    L.append(f"- **{verdict}** — "
             + ("the tree is rooted, mirrored, and lean." if verdict == "HEALTHY"
                else "see Debt + Drift above; bloat is review-only (GL7) and most candidates are fine."))
    report = "\n".join(L) + "\n"

    (LAL / "PINCH.md").write_text(report)
    print("pinch: JarvisMain/yggdrasil/lal/PINCH.md regenerated — "
          f"{flags} debt flag(s), {len(bloat)} bloat candidate(s), drift {'OK' if in_sync else 'BEHIND'}.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
