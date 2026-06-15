#!/usr/bin/env python3
"""changes_lens.py — rehydration: what changed, and why, without being told.

Raven 2026-06-15: "instead of telling Jarvis and Ayre to look at the upgrades, they can see them
and understand them." The event log (dex_events) is the raw spine — too granular for that. The
grimoire boot/verbs show the END STATE (current capability = the upgrades, understood). This lens
adds the missing DELTA view: the recent meaningful commits, grouped, so a stream waking cold reads
"here's what got built lately" in one page. End-state (grimoire) + delta (this) = full rehydration.

Reads git log (skips the mnemos rotation noise). Writes lal/CHANGES.md. Runs at seed tail; a live
grimoire lens ('Changes'). Stdlib only (uses git via subprocess; available in CI + locally).
"""
from __future__ import annotations
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / "JarvisMain" / "yggdrasil" / "lal" / "CHANGES.md"
SKIP = ("chore(mnemos)",)  # ledger rotation = noise, not a change
GROUPS = [("feat", "✦ Added"), ("fix", "✚ Fixed"), ("audit", "⊙ Audited"),
          ("chore(yggdrasil)", "⊕ Governance"), ("refactor", "↻ Refactored")]


def recent(n: int = 60) -> list[tuple[str, str, str]]:
    try:
        out = subprocess.run(["git", "log", f"-n{n}", "--date=short", "--format=%h%x1f%ad%x1f%s"],
                             cwd=ROOT, capture_output=True, text=True, timeout=20).stdout
    except Exception:
        return []
    rows = []
    for line in out.splitlines():
        parts = line.split("\x1f")
        if len(parts) == 3 and not any(parts[2].startswith(s) for s in SKIP):
            rows.append((parts[0], parts[1], parts[2]))
    return rows


def build() -> str:
    rows = recent()
    now = datetime.now(timezone.utc)
    stamp = f"{now.strftime('%Y-%m-%dT%H:%M:%SZ')} ({now.astimezone(ZoneInfo('America/New_York')).strftime('%Y-%m-%d %H:%M %Z')})"
    L = [
        "# Changes Lens — what got built lately (rehydration)",
        "",
        f"_generated: {stamp} · from git history (ledger-rotation noise filtered). The grimoire shows "
        "the END STATE; this shows the DELTA — read both to come up to speed cold._",
        "",
        f"**{len(rows)} meaningful commits.** Read this, then `grimoire {{page:boot}}` for current capability.",
        "",
    ]
    seen = set()
    for prefix, header in GROUPS:
        hits = [(h, d, s) for h, d, s in rows if s.startswith(prefix) and h not in seen]
        if not hits:
            continue
        L += [f"## {header}", ""]
        for h, d, s in hits[:20]:
            seen.add(h)
            # strip the conventional-commit prefix for readability
            msg = s.split(":", 1)[1].strip() if ":" in s else s
            L.append(f"- `{h}` {d} — {msg}")
        L.append("")
    other = [(h, d, s) for h, d, s in rows if h not in seen]
    if other:
        L += ["## · Other", ""]
        L += [f"- `{h}` {d} — {s}" for h, d, s in other[:10]] + [""]
    L += ["_To verify any single fact, the raw spine is `dex_events` (events_list / jarvis_dex_events). "
          "This page is the human-readable why; the event log is the auditable proof._", ""]
    return "\n".join(L) + "\n"


def main() -> int:
    import re
    new = build()
    if OUT.exists():
        rx = re.compile(r"^_generated:.*$", re.M)
        if rx.sub("", OUT.read_text()) == rx.sub("", new):
            new = OUT.read_text()
    OUT.write_text(new)
    print(f"changes-lens: {OUT.relative_to(ROOT)} regenerated.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
