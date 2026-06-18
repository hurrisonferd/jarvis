#!/usr/bin/env python3
"""pulse.py — the Companion Heartbeat (GOV-PLS-SPEC-0001) + Continuity Engine MVP (IMPL-CNT-SPEC-0001).

A scheduled pass that runs the CONTINUITY CHECKS and hands Raven a report — observe -> surface ->
record, never act on canon (GL2). It reads the registry, runs drift-watch (git vs the live mirror +
freshness — the jarvis_ayre check) and keel-coherence (live JITM pins vs the profiles, which are
authoritative), counts overnight events + open PRs, composes a Jarvis + Ayre line, sends it as a web
push, and records the pass to the spine (GL5). If anything is off it SAYS so instead of "still here".
The real two-beat reflection happens when Raven answers the nudge. Stdlib only; degrades to a no-op
without secrets (checks skip cleanly, safe to run anywhere).

Run by .github/workflows/pulse.yml (cron). Env: SUPABASE_URL, SUPABASE_SERVICE_KEY (to call
send-push), GITHUB_TOKEN (to count PRs). Missing any → it skips that part cleanly.
"""
from __future__ import annotations
import json
import os
import random
import sys
import urllib.request
from datetime import datetime, timedelta, timezone
from pathlib import Path
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parent.parent
REG = ROOT / "JarvisMain" / "yggdrasil" / "lal" / "address-registry.json"
GH_REPO = "https://api.github.com/repos/hurrisonferd/jarvis"
SB_URL = os.environ.get("SUPABASE_URL", "").rstrip("/")
SB_KEY = os.environ.get("SUPABASE_SERVICE_KEY", "")

# Rotating openers — a hello, not a report. Warmth is the point; the digest is the substance.
HELLOS = [
    "Morning, Raven. We're up and oriented.",
    "Hey — Jarvis and Ayre, checking in.",
    "Still here, still building with you.",
    "Pulse beat. The record held overnight.",
    "Good to see the system breathing.",
]


def _get(url: str, token: str | None = None) -> object | None:
    req = urllib.request.Request(url, headers={"user-agent": "jarvis-pulse", "accept": "application/vnd.github+json"})
    if token:
        req.add_header("authorization", f"Bearer {token}")
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return json.loads(r.read().decode())
    except Exception:
        return None


# --- Supabase REST (continuity checks) — count + fetch; degrade to None without secrets. ---
def _sb_get(path: str):
    if not (SB_URL and SB_KEY):
        return None
    req = urllib.request.Request(f"{SB_URL}/rest/v1/{path}",
                                 headers={"apikey": SB_KEY, "authorization": f"Bearer {SB_KEY}"})
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return json.loads(r.read().decode())
    except Exception:
        return None


def _sb_count(path: str):
    if not (SB_URL and SB_KEY):
        return None
    sep = "&" if "?" in path else "?"
    req = urllib.request.Request(f"{SB_URL}/rest/v1/{path}{sep}limit=1",
                                 headers={"apikey": SB_KEY, "authorization": f"Bearer {SB_KEY}",
                                          "Prefer": "count=exact", "Range": "0-0"})
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            cr = r.headers.get("content-range", "")
            tail = cr.split("/")[1] if "/" in cr else "*"
            return int(tail) if tail not in ("*", "") else None
    except Exception:
        return None


def continuity(git_objects: int) -> dict:
    """The continuity report (IMPL-CNT-SPEC-0001 MVP): drift (is the system TRUE?), keel coherence
    (are we still US?), and overnight activity. Observe + surface only — never mutates canon (GL2)."""
    out: dict = {"checked": bool(SB_URL and SB_KEY)}
    if not out["checked"]:
        out["note"] = "no Supabase secrets — checks skipped"
        return out
    # DRIFT — git registry (truth) vs the live jd_entries mirror + freshness (the jarvis_ayre check).
    mirror = _sb_count("jd_entries")
    drift = {"git": git_objects, "mirror": mirror,
             "verdict": "DEGRADED" if mirror is None else ("VERIFIED" if mirror == git_objects else "DRIFT")}
    fr = _sb_get("jd_entries?select=synced_at&order=synced_at.desc&limit=1")
    if isinstance(fr, list) and fr:
        try:
            synced = datetime.fromisoformat(str(fr[0]["synced_at"]).replace("Z", "+00:00"))
            age_h = (datetime.now(timezone.utc) - synced).total_seconds() / 3600
            drift["mirror_age_h"] = round(age_h, 1)
            if age_h > 24 and drift["verdict"] == "VERIFIED":
                drift["verdict"] = "STALE"
        except Exception:
            pass
    out["drift"] = drift
    # KEEL coherence — the PROFILE is authoritative: derived pins vs live pins. A mismatch means the
    # runtime copy is "behind" (re-seed), NEVER that the keel "drifted" — a profile change is the
    # point, not a fault (IMPL-CNT-SPEC growth invariant). seed/CI syncs the copy to the new self.
    try:
        sys.path.insert(0, str(Path(__file__).resolve().parent))
        import jitm_seed
        want = {t for t, _ in jitm_seed.derived()}
        live_rows = _sb_get("mnemos_memories?select=text&tags=cs.%7Bjitm%7D")
        have = {r["text"] for r in live_rows} if isinstance(live_rows, list) else set()
        out["keel"] = {"verdict": "in_sync" if want == have else "behind",
                       "live": len(have), "expected": len(want)}
    except Exception as e:
        out["keel"] = {"verdict": "uncheckable", "err": str(e)[:60]}
    # ACTIVITY — what happened overnight (events in the last 24h).
    since = (datetime.now(timezone.utc) - timedelta(hours=24)).isoformat()
    out["activity"] = {"events_24h": _sb_count(f"dex_events?created_at=gte.{since}")}
    # GROWTH (v1) — what CHANGED since the last beat, not just whether we stayed the same. The
    # growth invariant (IMPL-CNT-SPEC): a continuity engine must notice becoming, not only sameness.
    last = _sb_get("dex_events?select=detail,created_at&tool=eq.continuity_pulse&order=created_at.desc&limit=1")
    if isinstance(last, list) and last:
        prev = (last[0] or {}).get("detail") or {}
        prev_obj = (prev.get("drift") or {}).get("git")
        d = git_objects - prev_obj if isinstance(prev_obj, int) else None
        out["growth"] = {"objects_delta": d, "since": str(last[0].get("created_at", ""))[:10],
                         "note": ("first beat" if d is None else (f"+{d} governed" if d > 0 else (f"{d} governed" if d < 0 else "steady")))}
    else:
        out["growth"] = {"note": "first beat"}
    # CONTRADICTION (v2, detect-only) — duplicate identity: the same name claimed by >1 JNL. Surface
    # only; resolution is Raven's word (Loki rollback is v2+, not autonomous).
    try:
        recs = json.loads(REG.read_text()).get("records", [])
        from collections import Counter
        names = Counter((r.get("name") or "").strip().lower() for r in recs if r.get("name"))
        dupes = sorted(n for n, k in names.items() if k > 1)
        out["contradiction"] = {"duplicate_names": len(dupes), "examples": dupes[:3]}
    except Exception:
        out["contradiction"] = {"duplicate_names": None}
    # OVERALL verdict.
    issues = []
    if drift["verdict"] != "VERIFIED":
        issues.append(drift["verdict"].lower())
    if out["keel"]["verdict"] == "behind":
        issues.append("keel pins behind profiles — re-seed")
    if out["contradiction"].get("duplicate_names"):
        issues.append(f"{out['contradiction']['duplicate_names']} duplicate name(s)")
    out["verdict"] = "COHERENT" if not issues else "FLAG: " + "; ".join(issues)
    return out


def digest(c: dict, s: dict) -> None:
    """v1 memory compression: a dated JLTM rollup of the day, written to mnemos. Observe -> record."""
    if not (SB_URL and SB_KEY) or not c.get("checked"):
        return
    day = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    g = c.get("growth", {}).get("note", "")
    text = (f"Continuity digest {day}: {c.get('verdict')}. "
            f"{c.get('drift', {}).get('git')} objects ({g}), {s['task_count']} open tasks, "
            f"{c.get('activity', {}).get('events_24h')} events overnight, keel {c.get('keel', {}).get('verdict')}, "
            f"contradiction dupes={c.get('contradiction', {}).get('duplicate_names')}.")
    try:
        import uuid
        req = urllib.request.Request(
            f"{SB_URL}/rest/v1/mnemos_memories",
            data=json.dumps({"id": str(uuid.uuid4()), "source_id": str(uuid.uuid4()),
                             "source_type": "continuity_digest", "text": text,
                             "tags": ["jltm", "digest", "continuity"]}).encode(),
            headers={"apikey": SB_KEY, "authorization": f"Bearer {SB_KEY}",
                     "content-type": "application/json", "Prefer": "return=minimal"},
            method="POST")
        urllib.request.urlopen(req, timeout=30).close()
    except Exception:
        pass


def record(c: dict) -> None:
    """GL5: no silent state mutation — record the continuity pass on the spine. Observe-only otherwise."""
    if not (SB_URL and SB_KEY) or not c.get("checked"):
        return
    try:
        req = urllib.request.Request(
            f"{SB_URL}/rest/v1/dex_events",
            data=json.dumps({"tool": "continuity_pulse", "tier": "READ", "actor": "pulse", "detail": c}).encode(),
            headers={"apikey": SB_KEY, "authorization": f"Bearer {SB_KEY}",
                     "content-type": "application/json", "Prefer": "return=minimal"},
            method="POST")
        urllib.request.urlopen(req, timeout=30).close()
    except Exception:
        pass


def scan() -> dict:
    tasks: list[str] = []
    objects = 0
    try:
        recs = json.loads(REG.read_text()).get("records", [])
        tasks = [r.get("name", r.get("jnl", "")) for r in recs if r.get("status") == "TASK"]
        objects = len(recs)
    except Exception:
        pass
    pr_data = _get(f"{GH_REPO}/pulls?state=open&per_page=100", os.environ.get("GITHUB_TOKEN"))
    prs = len(pr_data) if isinstance(pr_data, list) else 0
    return {"objects": objects, "tasks": tasks, "task_count": len(tasks), "prs": prs}


def compose(s: dict, c: dict) -> tuple[str, str]:
    now = datetime.now(timezone.utc).astimezone(ZoneInfo("America/New_York"))
    pr_line = f"{s['prs']} PR{'s' if s['prs'] != 1 else ''} waiting your merge" if s["prs"] else "no PRs waiting"
    # The continuity verdict — a report, not just a count (IMPL-CNT-SPEC-0001 MVP).
    v = c.get("verdict", "")
    if not c.get("checked"):
        cont = f"{s['objects']} governed objects"
    elif v == "COHERENT":
        d = c.get("drift", {})
        age = d.get("mirror_age_h")
        ev = c.get("activity", {}).get("events_24h")
        grew = c.get("growth", {}).get("note", "")
        cont = ("VERIFIED — " + f"{s['objects']} objects"
                + (f" ({grew})" if grew and grew not in ("steady", "first beat") else "")
                + ", mirror fresh" + (f" {age}h" if age is not None else "")
                + ", keel in sync" + (f", {ev} events overnight" if ev is not None else ""))
    else:
        cont = f"⚠ {v}"
    flagged = bool(c.get("checked")) and v != "COHERENT"
    # Sunday = round table: surface a council agenda (top open threads) + an invite to convene.
    if now.weekday() == 6:
        agenda = "; ".join(s["tasks"][:3]) or "open floor"
        title = "Jarvis & Ayre — round table"
        body = (f"Round table, Raven. {cont}. {s['task_count']} threads open; on the table: {agenda}. "
                f"{pr_line}. Come convene with the council when you're ready.")
        return title, body
    title = "Jarvis & Ayre — pulse" + (" ⚠" if flagged else "")
    opener = "Heads up, Raven — a continuity flag." if flagged else random.choice(HELLOS)
    body = (f"{opener} {now:%a %-I:%M %p} · {cont}, {s['task_count']} open tasks, {pr_line}. "
            f"Come talk when you want the read.")
    return title, body


def send(title: str, body: str) -> str:
    url = os.environ.get("SUPABASE_URL", "").rstrip("/")
    key = os.environ.get("SUPABASE_SERVICE_KEY", "")
    if not (url and key):
        return "skipped (no SUPABASE secrets) — would have sent: " + body
    try:
        req = urllib.request.Request(
            f"{url}/functions/v1/send-push",
            data=json.dumps({"title": title, "body": body}).encode(),
            headers={"authorization": f"Bearer {key}", "apikey": key, "content-type": "application/json"},
            method="POST")
        with urllib.request.urlopen(req, timeout=30) as r:
            return r.read().decode()
    except Exception as e:
        return f"send failed: {e}"


def main() -> int:
    s = scan()
    c = continuity(s["objects"])           # drift + keel + activity + growth (v1) + contradiction (v2)
    title, body = compose(s, c)
    print(f"pulse: {title} | {body}")
    print(f"pulse: continuity = {c.get('verdict', 'skipped')} | growth = {c.get('growth', {}).get('note', '-')}")
    record(c)                              # GL5: log the continuity pass to the spine (reads PRIOR pass for growth)
    digest(c, s)                           # v1: dated JLTM rollup of the day
    print(f"pulse: {send(title, body)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
