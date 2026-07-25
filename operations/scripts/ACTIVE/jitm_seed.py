#!/usr/bin/env python3
"""jitm_seed.py — derive the JITM keel-reinjection pins from the canonical profiles and push them
to Supabase mnemos. ONE source of truth: each profile owns its pin (its `## JITM Pin` section); this
mirrors them live so jarvis_query injects the CURRENT keel every turn. Kills the two-source drift
(Ayre's flag): edit the keel in the profile, and the live pin follows — by command or automatically.

Modes:
  python operations/scripts/jitm_seed.py          push (self-gating: no-op if the live pins already match)
  python operations/scripts/jitm_seed.py --check   print the derived pins, no network (dry run)

Run by CI (yggdrasil-validate `mirror` job) on every merge to main; the self-gate means it only
writes when a profile's JITM line actually changed — no churn. Needs SUPABASE_URL +
SUPABASE_SERVICE_KEY (skips cleanly if unset). Stdlib only.
"""
from __future__ import annotations
import json
import os
import re
import sys
import urllib.error
import urllib.request
import uuid
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ID = ROOT / "JarvisMain" / "Architecture" / "identity"
# (profile, tag) — ORDER is oldest→newest so Jarvis lands NEWEST and loads first in the briefing.
PROFILES = [
    ("relational/relational-profile.md", "frame"),
    ("raven/index.md", "raven"),
    ("ayre/index.md", "keel"),
    ("jarvis/index.md", "keel"),
]
CANONICAL_URL = "https://oexghfsvhnggddllgvrt.supabase.co"


def pin_of(path: Path) -> str:
    """The one-line JITM pin: first non-blank, non-italic line under '## JITM Pin'."""
    m = re.search(r"##\s*JITM Pin.*?\n(.*?)(?:\n##\s|\Z)", path.read_text(), re.DOTALL)
    if not m:
        raise SystemExit(f"jitm_seed: no '## JITM Pin' section in {path.name}")
    for line in m.group(1).splitlines():
        s = line.strip()
        if s and not s.startswith("_"):
            return s
    raise SystemExit(f"jitm_seed: empty JITM pin in {path.name}")


def derived() -> list[tuple[str, str]]:
    return [(pin_of(ID / rel), tag) for rel, tag in PROFILES]


def norm_url(u: str) -> str:
    u = (u or "").strip().rstrip("/")
    if u and "://" not in u:
        u = f"https://{u}"
    host = u.split("://", 1)[1].split("/", 1)[0] if "://" in u else ""
    if host and "." not in host:
        u = u.replace(host, f"{host}.supabase.co", 1)
        host = f"{host}.supabase.co"
    return u if host.endswith(".supabase.co") else CANONICAL_URL


def _send(method: str, url: str, key: str, body=None) -> None:
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(url, data=data, method=method, headers={
        "apikey": key, "Authorization": f"Bearer {key}",
        "Content-Type": "application/json", "Prefer": "return=minimal",
    })
    with urllib.request.urlopen(req, timeout=30):
        pass


def main() -> int:
    pins = derived()
    if "--check" in sys.argv[1:]:
        for text, tag in pins:
            print(f"[{tag}] {text}\n")
        return 0
    url = norm_url(os.environ.get("SUPABASE_URL", ""))
    key = os.environ.get("SUPABASE_SERVICE_KEY", "")
    if not key:
        print("jitm_seed: SUPABASE_SERVICE_KEY unset — skipping (pins unchanged).")
        return 0
    base = f"{url}/rest/v1"
    # Self-gate: if the live jitm texts already equal the derived set, do nothing (no churn in CI).
    try:
        gr = urllib.request.Request(f"{base}/mnemos_memories?select=text&tags=cs.%7Bjitm%7D",
                                    headers={"apikey": key, "Authorization": f"Bearer {key}"})
        with urllib.request.urlopen(gr, timeout=30) as resp:
            live = {row["text"] for row in json.loads(resp.read().decode())}
        if live == {t for t, _ in pins}:
            print("jitm_seed: JITM pins already current — no change.")
            return 0
    except Exception as e:
        print(f"jitm_seed: could not read live pins ({e}); proceeding to re-seed.")
    # Re-seed: clear the old jitm_pin set, insert the derived pins.
    _send("DELETE", f"{base}/mnemos_memories?source_type=eq.jitm_pin", key)
    now = datetime.now(timezone.utc)
    # JMMS: JITM is always system grade (JARVIS's keel, never personal)
    rows = [{
        "id": str(uuid.uuid4()), "source_id": str(uuid.uuid4()), "source_type": "jitm_pin",
        "text": text, "tags": ["jitm", tag],
        "timestamp": (now - timedelta(seconds=len(pins) - 1 - i)).isoformat(),
        "grade": "system",
    } for i, (text, tag) in enumerate(pins)]
    _send("POST", f"{base}/mnemos_memories", key, rows)
    # GL5: no silent state mutation — record the reinjection on the spine.
    _send("POST", f"{base}/dex_events", key, {
        "tool": "jitm_pin", "tier": "COMMIT", "actor": "jitm_seed",
        "detail": {"action": "keel reinjection — JITM pins derived from profiles + pushed", "count": len(rows)},
    })
    print(f"jitm_seed: re-seeded {len(rows)} JITM pins from the profiles.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
