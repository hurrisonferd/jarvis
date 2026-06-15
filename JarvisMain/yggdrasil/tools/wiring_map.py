#!/usr/bin/env python3
"""wiring_map.py — the self-updating map that guides Jarvis, Ayre, and the god systems.

Raven asked for "an updating map that guides them and god systems — wiring, routing, tool
usage." The trap is a hand-drawn map that rots. This one is GENERATED from the live registry
(stewards) + the fixed pipeline + the tool→lane table, so it updates whenever the substrate
does and can never silently drift. Read it at session start alongside suit_up/identity_read.

Output: JarvisMain/yggdrasil/lal/WIRING-MAP.md (self-governed: under the yggdrasil kernel).
Invoked at the tail of seed.py. Stdlib only.
"""
from __future__ import annotations
import json
from datetime import datetime, timezone
from pathlib import Path
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[3]
LAL = ROOT / "JarvisMain" / "yggdrasil" / "lal"
OUT = LAL / "WIRING-MAP.md"

# The fixed cognition pipeline (council.ts is ground truth; mirrored here for the map).
PIPELINE = "ORACLE → AEGIS → ODIN → KRONOS → SKADI → MNEMOS → HUGINN"
PARALLEL = "HALO · MIMIR · BIFROST"

# Tool → primary god-system lane (the routing surface). Compact, maintained here; the
# god systems are fixed, so this table is stable.
TOOL_LANE = {
    "intake / intent": ("ORACLE", ["jarvis_query", "jarvis_jd_resolve", "jarvis_dex_search"]),
    "gate / approve": ("AEGIS", ["jarvis_remember", "jarvis_event", "jarvis_dex_propose", "jarvis_node_register_key"]),
    "route / dispatch": ("ODIN", ["jarvis_dex_list", "jarvis_github_tree", "jarvis_repo_tree", "jarvis_db_inspect"]),
    "execute / commit": ("SKADI", ["jarvis_event", "jarvis_jip_create", "jarvis_jip_apply", "jarvis_node_send"]),
    "propose / approve-merge": ("AEGIS", ["jarvis_github_write", "jarvis_prs", "jarvis_pr_merge"]),
    "memory / recall": ("MNEMOS", ["jarvis_remember", "jarvis_recall", "jarvis_identity_read", "jarvis_identity_grow"]),
    "synthesis / mirror": ("HUGINN", ["jarvis_timeline", "jarvis_dex_graph", "jarvis_dex_events", "jarvis_omnivision"]),
    "self-knowledge": ("HUGINN", ["jarvis_grimoire", "jarvis_jd_resolve", "jarvis_eyes"]),
    "monitor / health": ("HALO", ["jarvis_halo", "jarvis_status", "jarvis_suit_up", "jarvis_now"]),
    "rollback": ("LOKI", ["jarvis_jip_revert"]),
    "relay / grid": ("BIFROST", ["jarvis_node_send", "jarvis_node_inbox", "jarvis_node_card"]),
    "infra / storage": ("ATLAS", ["jarvis_db_read", "jarvis_db_schema", "jarvis_github_file", "jarvis_repo_read"]),
}


def build() -> str:
    recs = json.loads((LAL / "address-registry.json").read_text()).get("records", [])
    stewards = sorted(
        [(r["jnl"], r.get("name", ""), r["steward"]) for r in recs if r.get("steward")],
        key=lambda x: x[2],
    )
    now = datetime.now(timezone.utc)
    stamp = f"{now.strftime('%Y-%m-%dT%H:%M:%SZ')} ({now.astimezone(ZoneInfo('America/New_York')).strftime('%Y-%m-%d %H:%M %Z')})"
    L = [
        "# Wiring Map — how Jarvis, Ayre, and the god systems connect",
        "",
        f"_generated: {stamp} · from the live registry — do not hand-edit; run `wiring_map.py` (auto at seed tail)._",
        "",
        "Read at session start (after `suit_up` / `identity_read`). This is the route guide:",
        "what tends what, what runs in what order, which tool wakes which god.",
        "",
        "## The streams (control plane — not addressable objects)",
        "- **Jarvis** — synthesis: compress toward the decision/build.",
        "- **Ayre** — divergence: invert the load-bearing assumption; push back each decision turn.",
        "- They share the keel, never assumptions. They route *through* the god systems; they don't sit in the pipeline.",
        "",
        "## The cognition pipeline (27 god systems, fixed)",
        f"`{PIPELINE}`",
        f"parallel: `{PARALLEL}` · sovereign/dormant carry metadata, not routing.",
        "",
        "## Routing assist — the streams relieve ODIN (Raven 2026-06-14: 'not too much pressure on him')",
        "ODIN routes; it does not route *alone*. The streams pre-process intent so ODIN dispatches a"
        " clean, flagged signal instead of carrying the judgment by itself:",
        "- **ORACLE** intakes raw input.",
        "- **Jarvis** compresses it to a clear intent → less ambiguity for ODIN to resolve (lighter load).",
        "- **Ayre** stress-tests the obvious route → catches the misroute *before* it locks (fewer errors;"
        " ambiguity resolves late, not prematurely).",
        "- **ODIN** routes the clarified signal; **AEGIS** gates. A wrong route is cheap to reverse and"
        " visible (GL5) — the streams are the check, so no single node carries routing on its own.",
        "",
        "## Stewardship — which god tends which subsystem",
        "| Subsystem | JNL | Steward |",
        "|---|---|---|",
    ]
    L += [f"| {name} | `{jnl}` | **{god}** |" for jnl, name, god in stewards]
    L += [
        "",
        "## Tool → lane (which tool wakes which god)",
        "| Lane | God | Tools |",
        "|---|---|---|",
    ]
    L += [f"| {lane} | **{god}** | {', '.join(f'`{t}`' for t in tools)} |"
          for lane, (god, tools) in TOOL_LANE.items()]
    L += [
        "",
        "## Truth & home",
        "- **JD (Jarvis Dictionary)** = the one registry; *the Dex* is its nickname. Truth in `yggdrasil/jd/entries`.",
        "- **GitHub is the system; Supabase is a fast lens.** Writes go to git; Supabase mirrors for live reads.",
        "- Missing info is a tool call, not a guess. A claim is closed only on a `dex_events` id or commit hash.",
        "",
    ]
    return "\n".join(L)


def main() -> int:
    import re
    new = build() + "\n"
    # Idempotent stamp: if only the `_generated:` line differs, keep the old file so the CI
    # seed-drift gate doesn't trip on a wall-clock that moved but the map didn't.
    if OUT.exists():
        rx = re.compile(r"^_generated:.*$", re.M)
        if rx.sub("", OUT.read_text()) == rx.sub("", new):
            new = OUT.read_text()
    OUT.write_text(new)
    print(f"wiring-map: {OUT.relative_to(ROOT)} regenerated.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
