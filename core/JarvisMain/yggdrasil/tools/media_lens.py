#!/usr/bin/env python3
"""media_lens.py — the one un-graphed domain, brought into the graph.

Media files weren't nodes — they were storage. This lens reads the declared media->object links
(JarvisSide/Media/media-links.json), VALIDATES every link against the registry (no dangling edges,
the honesty rule), folds in the librosa audio features, and renders a navigable media graph:
"Neon Breakwater -> MUSICOS", "Aincrad image -> The Grid". Net-new coverage, not a new system —
it links media into the canonical graph that already exists.

Reads: JarvisSide/Media/media-links.json, AUDIO-FEATURES.json, lal/address-registry.json.
Writes: lal/MEDIA-LINKS.md. Runs at seed tail; a live grimoire lens ('Media'). Stdlib only.
"""
from __future__ import annotations
import json
from datetime import datetime, timezone
from pathlib import Path
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[3]
LAL = ROOT / "JarvisMain" / "yggdrasil" / "lal"
MEDIA = ROOT / "JarvisSide" / "Media"
LINKS = MEDIA / "media-links.json"
FEATURES = MEDIA / "AUDIO-FEATURES.json"
OUT = LAL / "MEDIA-LINKS.md"


def build() -> str:
    reg = {r["jnl"]: r for r in json.loads((LAL / "address-registry.json").read_text()).get("records", [])}
    items = json.loads(LINKS.read_text()).get("items", []) if LINKS.exists() else []
    feats = json.loads(FEATURES.read_text()).get("tracks", {}) if FEATURES.exists() else {}
    now = datetime.now(timezone.utc)
    stamp = f"{now.strftime('%Y-%m-%dT%H:%M:%SZ')} ({now.astimezone(ZoneInfo('America/New_York')).strftime('%Y-%m-%d %H:%M %Z')})"
    dangling = []  # (file, jnl) links that point at nothing — flagged loudly

    def linkfmt(item):
        out = []
        for j in item.get("links", []):
            if j in reg:
                out.append(f"`{j}` ({reg[j].get('name','')[:24]})")
            else:
                out.append(f"`{j}` ⚠UNKNOWN")
                dangling.append((item["file"], j))
        return " · ".join(out) or "—"

    imgs = [i for i in items if i.get("kind") == "image"]
    auds = [i for i in items if i.get("kind") == "audio"]
    L = [
        "# Media Lens — media linked into the graph",
        "",
        f"_generated: {stamp} · from `media-links.json` (declared, git-first) + `AUDIO-FEATURES.json`. "
        "Every link is validated against the registry — dangling links are flagged, never silent._",
        "",
        f"**{len(items)} media items · {len(imgs)} images · {len(auds)} audio · linked into the graph.**",
        "",
        "## Images → objects",
        "| image | links | tags |", "|---|---|---|",
    ]
    L += [f"| `{i['file'].split('/')[-1]}` | {linkfmt(i)} | {' '.join(i.get('tags', []))} |" for i in imgs]
    L += ["", "## Audio → objects (with librosa features when heard)",
          "| track | links | BPM · key · mood |", "|---|---|---|"]
    for i in auds:
        name = i["file"].split("/")[-1]
        f = feats.get(name, {})
        bones = (f"{f.get('bpm','?')} · {f.get('key','?')} · {f.get('mood','not yet heard')}"
                 if f and "error" not in f else "not yet heard")
        L += [f"| `{name}` | {linkfmt(i)} | {bones} |"]
    if dangling:
        L += ["", "## ⚠ Dangling links (point at JNLs not in the registry — fix in media-links.json)"]
        L += [f"- `{file}` → `{jnl}`" for file, jnl in dangling]
    L += ["",
          "_Media is now navigable: a track or image resolves to the project/world it belongs to. "
          "Refine the links in `JarvisSide/Media/media-links.json`; the lens re-validates on reseed._", ""]
    return "\n".join(L) + "\n"


def main() -> int:
    import re
    new = build()
    if OUT.exists():
        rx = re.compile(r"^_generated:.*$", re.M)
        if rx.sub("", OUT.read_text()) == rx.sub("", new):
            new = OUT.read_text()
    OUT.write_text(new)
    print(f"media-lens: {OUT.relative_to(ROOT)} regenerated.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
