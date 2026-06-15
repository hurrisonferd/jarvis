#!/usr/bin/env python3
"""grimoire.py — the Novochrono Grimoire: the book through which JARVIS knows itself.

Not a hand-written doc — a PROJECTION over the one truth (the JD entries + the graph).
A *page* is a query + a layout over that data, so a page can never show an object that
isn't in the dex, and never hide one that is (the fix for stream-blindness: a claim of
"missing" must check the catalog, and the catalog is generated from what exists).

Two faces, one spec:
  • the BOOK  — `lal/GRIMOIRE.md`: cover + the full catalog index + the lens (omni/fusion)
                page registry + a sample card. Generated; committed; idempotent stamp.
  • the CARD  — projected on demand: `grimoire.py card <anything>` resolves a JID(seq),
                JNL, name, or alias to one object's page (its four ID faces, lineage,
                steward, tags, definition, neighbors). This is the projection screen the
                MCP summon tool + TRON view will render from the same render_card().

Atom = the JID card. Every other page (the lenses) is a different filter over the same render.
Invoked at the tail of seed.py (after wiring_map / health). Stdlib only.

Usage:
  grimoire.py                 # (re)generate the book → lal/GRIMOIRE.md
  grimoire.py card <query>    # project one card; query = seq / JNL / name / alias
  grimoire.py find <term>     # list catalog rows matching a term
"""
from __future__ import annotations
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[3]
JD = ROOT / "JarvisMain" / "yggdrasil" / "jd" / "entries"
LAL = ROOT / "JarvisMain" / "yggdrasil" / "lal"
OUT = LAL / "GRIMOIRE.md"

# The omni/fusion lenses — each is a grimoire PAGE generator (a filter over the same data).
# Raven 2026-06-15: keep both (lenses + grimoire), integrated — the grimoire is the book,
# the lenses are its chapters. status: live = a generator already exists; planned = page
# defined, generator pending. Listing them here is what makes them findable.
LENSES = [
    ("Wiring",     "live",    "how streams + god systems connect (route guide)",        "WIRING-MAP.md"),
    ("Changes",    "live",    "what got built lately + why — rehydration (delta view)",   "CHANGES.md"),
    ("Brief",      "live",    "cold-boot prompt — paste to wake JARVIS in any LLM",       "PORTABLE-BRIEF.md"),
    ("Health",     "live",    "vitality: orphans, isolated, stewardless, open tasks",    "HEALTH.md"),
    ("Sovereign",  "planned", "full self-model: state + intent + history + structure",   "—"),
    ("Cause",      "planned", "event causality: A → task B → structural change C",       "—"),
    ("Architect",  "planned", "structure integrity: missing modules / under-linkage",    "—"),
    ("Pressure",   "planned", "load map: overloaded domains, stalled clusters",          "—"),
    ("Topology",   "live",    "the system's shape: hubs, leaves, isolation, edge types",  "TOPOLOGY-LENS.md"),
    ("Drift",      "planned", "evolution over snapshots: acceleration / decay zones",    "—"),
    ("Orphan",     "live",    "the debt as a worklist: a disposition proposal per orphan", "ORPHAN-LENS.md"),
    ("Sync",       "live",    "git vs Supabase divergence — the cross-store alarm (Love Train)", "SYNC-LENS.md"),
    ("Intent",     "planned", "intent vs execution mismatch (did we build what we meant)", "—"),
    ("Resilience", "planned", "failure map: single points of failure, fragile deps",     "—"),
    ("Media",      "live",    "media linked into the graph: track/image → project/world",  "MEDIA-LINKS.md"),
]


def _parse_frontmatter(text: str) -> dict:
    """Tolerant YAML-lite reader for JD entry frontmatter (stdlib only — no pyyaml)."""
    m = re.match(r"^---\n(.*?)\n---\n?(.*)$", text, re.S)
    fm: dict = {}
    body = text
    if m:
        body = m.group(2)
        for line in m.group(1).splitlines():
            if ":" not in line or line.strip().startswith("#"):
                continue
            k, v = line.split(":", 1)
            k, v = k.strip(), v.strip()
            if v.startswith("[") and v.endswith("]"):
                fm[k] = [x.strip() for x in v[1:-1].split(",") if x.strip()]
            else:
                fm[k] = v
    # definition / purpose live in the body as **Definition:** / **Purpose:** lines
    for key in ("Definition", "Purpose"):
        mm = re.search(rf"\*\*{key}:\*\*\s*(.+)", body)
        if mm:
            fm[key.lower()] = mm.group(1).strip()
    return fm


def load_entries() -> list[dict]:
    out = []
    for p in sorted(JD.glob("*.md")):
        try:
            fm = _parse_frontmatter(p.read_text())
            if fm.get("jnl"):
                out.append(fm)
        except Exception:
            continue
    return out


def load_graph() -> dict:
    try:
        return json.loads((LAL / "graph.json").read_text())
    except Exception:
        return {"nodes": [], "edges": []}


def resolve(entries: list[dict], query: str) -> dict | None:
    q = query.strip().lower()
    # exact: seq (JID) → jnl → name → alias
    for e in entries:
        if str(e.get("seq", "")).lower() == q:
            return e
    for e in entries:
        if e.get("jnl", "").lower() == q:
            return e
    for e in entries:
        if e.get("name", "").lower() == q:
            return e
    for e in entries:
        if q in [a.lower() for a in e.get("aliases", [])]:
            return e
    # partial: name contains
    hits = [e for e in entries if q in e.get("name", "").lower()]
    return hits[0] if len(hits) == 1 else (hits[0] if hits else None)


def render_card(e: dict, entries: list[dict], graph: dict) -> str:
    jnl = e.get("jnl", "?")
    seq = e.get("seq", "—")
    children = sorted(x["jnl"] for x in entries if x.get("parent") == jnl)
    parent = e.get("parent") or "—"
    siblings = sorted(x["jnl"] for x in entries
                      if x.get("parent") == e.get("parent") and x.get("jnl") != jnl and e.get("parent"))
    out_edges = [(ed["target"], ed.get("type", "")) for ed in graph.get("edges", []) if ed.get("source") == jnl]
    in_edges = [(ed["source"], ed.get("type", "")) for ed in graph.get("edges", []) if ed.get("target") == jnl]
    L = [
        f"## ▣ {e.get('name','(unnamed)')}",
        "",
        "| face | value |",
        "|---|---|",
        f"| **JID** (seq) | `{seq}` |",
        f"| **JNL** (address) | `{jnl}` |",
        f"| **name** | {e.get('name','—')} |",
        f"| type · class · tier | {e.get('type','—')} · {e.get('class','—')} · {e.get('tier','—')} |",
        f"| status · authority | {e.get('status','—')} · {e.get('authority','—')} |",
        f"| owner · steward | {e.get('owner','—')} · {e.get('steward') or '—'} |",
        "",
        f"**Definition.** {e.get('definition','—')}",
        "",
        f"**Purpose.** {e.get('purpose','—')}",
        "",
        "**Lineage**",
        f"- parent ↑ `{parent}`",
        f"- children ↓ {' '.join(f'`{c}`' for c in children) or '—'}",
        f"- siblings ↔ {' '.join(f'`{s}`' for s in siblings) or '—'}",
        f"- related → {' '.join(f'`{r}`' for r in e.get('related', [])) or '—'}",
        "",
        "**Neighbors (graph edges)**",
        f"- out → {' '.join(f'`{t}`({ty})' for t, ty in out_edges) or '—'}",
        f"- in ← {' '.join(f'`{s}`({ty})' for s, ty in in_edges) or '—'}",
        "",
        f"**Tags.** {' '.join('`'+t+'`' for t in e.get('tags', [])) or '—'}"
        + (f" · **aliases:** {', '.join(e.get('aliases', []))}" if e.get("aliases") else ""),
        f"\n**Home.** `{e.get('source','—')}`",
    ]
    return "\n".join(L)


def build_book(entries: list[dict], graph: dict) -> str:
    now = datetime.now(timezone.utc)
    stamp = f"{now.strftime('%Y-%m-%dT%H:%M:%SZ')} ({now.astimezone(ZoneInfo('America/New_York')).strftime('%Y-%m-%d %H:%M %Z')})"
    by_domain: dict[str, list[dict]] = {}
    for e in entries:
        dom = e.get("jnl", "?-").split("-")[0]
        by_domain.setdefault(dom, []).append(e)
    L = [
        "# The Grimoire — JARVIS, as it knows itself",
        "",
        f"_generated: {stamp} · projected from `jd/entries` + `graph.json` (truth) — "
        "do not hand-edit; run `grimoire.py` (auto at seed tail)._",
        "",
        "A page is a query over the one dataset, never a hand-written claim. A card cannot show "
        "an object absent from the dex, nor hide one present — so \"missing\" is always a lookup, "
        "never a guess. **Summon a card:** `grimoire.py card <seq | JNL | name | alias>`.",
        "",
        f"**{len(entries)} governed objects** · {len(graph.get('edges', []))} edges · "
        f"{len(by_domain)} domains.",
        "",
    ]
    # Boot Menu — the AI-native front door (Raven 2026-06-15). Rendered from live vitals so a
    # stream waking cold sees the system's state + what it can do. Summon: jarvis_grimoire page=boot.
    tasks = [e for e in entries if e.get("status") == "TASK"]
    orphans = [e for e in entries if not e.get("parent")]
    L += [
        "## Boot Menu — say a number, or speak it",
        "",
        f"_JARVIS online · {len(entries)} objects · {len(tasks)} open tasks · {len(orphans)} orphans · "
        f"{len(graph.get('edges', []))} edges._",
        "",
        "1. **System health** → `jarvis_eyes` (state + wiring + vitality)",
        "2. **Open tasks** → `jarvis_dex_list {status:'TASK'}`" + (f" — {len(tasks)} in flight" if tasks else ""),
        "3. **Orphan debt** → the Orphan lens (`jarvis_grimoire {page:'catalog'}` / `ORPHAN-LENS.md`)"
        + (f" — {len(orphans)} unparented" if orphans else ""),
        "4. **What happened** → `jarvis_timeline` (recent events + commits)",
        "5. **Summon a card** → `jarvis_jd_resolve` ('jid 1', a name, or a JNL)",
        "6. **The lenses** → `jarvis_grimoire {page:'lenses'}` (the fusion chapters)",
        "7. **Propose a change** → `jarvis_github_write` (files→one PR) → `jarvis_pr_merge` (summary+approve)",
        "",
        "_Boot ritual: this menu, then act on what Raven says. Missing info is a tool call, not a guess._",
        "",
        "## Verbs — what you can say (the system's own phrasebook)",
        "Meta-NLP: natural phrases → the tool they wake. The model routes; this is the map it routes by.",
        "",
        "| say… | → tool |",
        "|---|---|",
        "| \"load X\" · \"what is X\" · \"jid 1\" · a name/JNL | `jarvis_jd_resolve` |",
        "| \"listen to <track>\" · \"what key is X in\" | `jarvis_listen` |",
        "| \"show me / look at <image>\" | `jarvis_media_view` |",
        "| \"boot\" · \"what can I do\" | `jarvis_grimoire {page:boot}` |",
        "| \"the grimoire\" · \"what views exist\" | `jarvis_grimoire {page:lenses}` |",
        "| \"what can I say\" · \"verbs\" | `jarvis_grimoire {page:verbs}` |",
        "| \"how are we\" · \"system health\" · \"where do I go\" | `jarvis_eyes` |",
        "| \"what's open\" · \"tasks\" | `jarvis_dex_list {status:TASK}` |",
        "| \"what's wrong\" · \"the debt\" | the Orphan lens (`ORPHAN-LENS.md`) |",
        "| \"what happened\" · \"recently\" | `jarvis_timeline` |",
        "| \"search for X\" | `jarvis_dex_search` |",
        "| \"remember / recall X\" | `jarvis_remember` / `jarvis_recall` |",
        "| \"the time\" · \"now\" | `jarvis_now` |",
        "| \"propose a change\" · \"write files\" | `jarvis_github_write` (files→one PR) |",
        "| \"any PRs\" | `jarvis_prs` |",
        "| \"merge / approve it\" | `jarvis_pr_merge` (Jarvis+Ayre summary, then your yes) |",
        "",
        "## Lens pages (the omni/fusion chapters)",
        "The grimoire is the book; each lens is a chapter — a different filter over the same data.",
        "",
        "| page | status | renders | source |",
        "|---|---|---|---|",
    ]
    L += [f"| **{n}** | {s} | {d} | `{src}` |" for n, s, d, src in LENSES]
    L += ["", "## Catalog (every object, summonable as a card)", ""]
    for dom in sorted(by_domain):
        rows = sorted(by_domain[dom], key=lambda x: x.get("jnl", ""))
        L += [f"### {dom} ({len(rows)})", "", "| JID | JNL | name | status | steward |", "|---|---|---|---|---|"]
        L += [f"| `{e.get('seq','—')}` | `{e['jnl']}` | {e.get('name','—')} | "
              f"{e.get('status','—')} | {e.get('steward') or '—'} |" for e in rows]
        L += [""]
    # a sample card so the projection format lives in the book too
    sample = resolve(entries, "ARCH-YGG-CORE-0001") or (entries[0] if entries else None)
    if sample:
        L += ["---", "", "## Sample card (the atom — every page builds on this)", "",
              render_card(sample, entries, graph), ""]
    return "\n".join(L) + "\n"


def main() -> int:
    args = sys.argv[1:]
    entries = load_entries()
    graph = load_graph()
    if args and args[0] == "card":
        if len(args) < 2:
            print("usage: grimoire.py card <seq | JNL | name | alias>"); return 2
        e = resolve(entries, " ".join(args[1:]))
        if not e:
            print(f"no card for '{' '.join(args[1:])}' — check the catalog (grimoire.py find <term>)"); return 1
        print(render_card(e, entries, graph)); return 0
    if args and args[0] == "find":
        term = " ".join(args[1:]).lower()
        hits = [e for e in entries if term in e.get("name", "").lower() or term in e.get("jnl", "").lower()
                or term in [t.lower() for t in e.get("tags", [])]]
        for e in hits:
            print(f"{e.get('seq','—'):>4}  {e['jnl']:<28}  {e.get('name','')}")
        print(f"— {len(hits)} match(es)"); return 0
    # default: regenerate the book, idempotent stamp (don't trip the CI seed-drift gate)
    new = build_book(entries, graph)
    if OUT.exists():
        rx = re.compile(r"^_generated:.*$", re.M)
        if rx.sub("", OUT.read_text()) == rx.sub("", new):
            new = OUT.read_text()
    OUT.write_text(new)
    print(f"grimoire: {OUT.relative_to(ROOT)} regenerated — {len(entries)} cards catalogued.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
