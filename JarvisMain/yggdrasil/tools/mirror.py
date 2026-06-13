#!/usr/bin/env python3
"""mirror.py — the Global Mirror generator (JMS / earned omnivision, ARCH-JMS-SPEC-0001).

Consolidates the LAL registries into ONE freshness-stamped, single-read snapshot of the
whole repo-side system: lal/global-mirror.json. A stream reads this one file and holds
the entire world at once — omnivision — but it is NEVER authoritative: it carries its own
freshness (generated_at + source_commit) so a stale read is impossible to mistake for a
current one (JMS law: references, never truth). Freshness first, the mirror second.

Run standalone, or it is invoked at the tail of seed.py so it stays fresh with every
reseed (= every commit, per the workflow). Repo layer only; the live-dex sync is a
separate, connector-gated mirror.
"""
from __future__ import annotations
import json
import subprocess
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[3]
LAL = ROOT / "JarvisMain" / "yggdrasil" / "lal"


def _git_head() -> str:
    try:
        return subprocess.run(["git", "rev-parse", "--short", "HEAD"],
                              capture_output=True, text=True, cwd=ROOT, check=True).stdout.strip()
    except Exception:
        return "unknown"


def build() -> dict:
    reg = json.loads((LAL / "address-registry.json").read_text())
    records = reg.get("records", [])
    now = datetime.now(timezone.utc)
    eastern = now.astimezone(ZoneInfo("America/New_York"))

    by_status = Counter(r.get("status", "?") for r in records)
    by_domain = Counter(r.get("jnl", "-").split("-")[0] for r in records)
    by_tier = Counter(r.get("tier", "?") for r in records)

    # Trim each object to the load-bearing fields for a true single-read map.
    objects = sorted(
        ({
            "jnl": r.get("jnl"), "name": r.get("name"), "type": r.get("type"),
            "class": r.get("class"), "tier": r.get("tier"), "status": r.get("status"),
            "parent": r.get("parent", ""), "location": r.get("location", ""),
            "tags": r.get("tags", []),
        } for r in records),
        key=lambda o: o["jnl"] or "",
    )

    return {
        # FRESHNESS FIRST — the stamp that makes omnivision honest (read this before trusting the rest).
        "freshness": {
            "generated_at_utc": now.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "generated_at_eastern": eastern.strftime("%Y-%m-%d %H:%M %Z"),
            "source_commit": _git_head(),
            "authoritative": False,
            "law": "JMS: this mirror points at truth (files + dex + spine); it is never truth. Stale stamp -> fall back to source.",
        },
        "summary": {
            "object_count": len(records),
            "by_status": dict(sorted(by_status.items())),
            "by_domain": dict(sorted(by_domain.items())),
            "by_tier": dict(sorted(by_tier.items())),
        },
        "objects": objects,
    }


def main() -> int:
    mirror = build()
    out = LAL / "global-mirror.json"
    out.write_text(json.dumps(mirror, indent=2, ensure_ascii=False) + "\n")
    f = mirror["freshness"]; s = mirror["summary"]
    print(f"global-mirror: {s['object_count']} objects @ {f['source_commit']} "
          f"({f['generated_at_eastern']}) -> {out.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
