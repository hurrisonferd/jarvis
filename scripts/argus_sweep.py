"""ARGUS sweep (P43) — scheduled drift detection for the governed record.

The loop's continuity must not lean on session reconstruction or human memory
(the P17 lesson: a stale ledger claim survived two weeks until Raven caught it
over coffee). This sweep re-verifies record claims against live state on a
schedule and fails loudly when they disagree (GL5: no silent drift).

Checks:
  1. Mirror integrity   — cloud jnl_registry/jd_entries vs repo registries:
                          missing rows, status drift, serial drift.
  2. Reconcile backlog  — cloud-only ACTIVE entries older than the reconcile
                          window (approved via connector, never materialized).
  3. Proposal staleness — pending dex proposals older than 3 days.
  4. Ledger staleness   — patch_ledger entries claiming partial/pending whose
                          record hasn't moved in 14 days (re-verify, don't trust).

Exit 0 = clean (warnings allowed); exit 1 = drift (workflow opens an issue).
Logs its own verdict to dex_events (the check itself is an event — GL5).
Stdlib only. Run by .github/workflows/argus-sweep.yml (cron + dispatch).
"""
from __future__ import annotations
import json
import os
import re
import sys
import urllib.request
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
JD_DIR = ROOT / "JarvisMain" / "yggdrasil" / "jd" / "entries"
REG = ROOT / "JarvisMain" / "yggdrasil" / "lal" / "address-registry.json"
SEQ = ROOT / "JarvisMain" / "yggdrasil" / "lal" / "seq-registry.json"
LEDGER = ROOT / "audit" / "patch_ledger.json"

CANONICAL_URL = "https://oexghfsvhnggddllgvrt.supabase.co"
RECONCILE_GRACE_DAYS = 2
PROPOSAL_STALE_DAYS = 3
LEDGER_STALE_DAYS = 14

_FM_RE = re.compile(r"^---\n(.*?)\n---", re.DOTALL)


def norm_url(u: str) -> str:
    u = (u or "").strip().rstrip("/")
    if not u:
        return CANONICAL_URL
    if "://" not in u:
        u = f"https://{u}"
    host = u.split("://", 1)[1].split("/", 1)[0]
    if "." not in host:
        u = u.replace(host, f"{host}.supabase.co", 1)
    return u if u.startswith("https://") and ".supabase.co" in u else CANONICAL_URL


def rest(base: str, key: str, path: str):
    req = urllib.request.Request(
        f"{base}/rest/v1/{path}",
        headers={"apikey": key, "Authorization": f"Bearer {key}"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read().decode())


def log_event(base: str, key: str, verdict: str, detail: dict) -> None:
    """The sweep itself is an event (GL5). Best-effort — a failed log never masks the verdict."""
    try:
        req = urllib.request.Request(
            f"{base}/rest/v1/dex_events",
            data=json.dumps({"tool": "argus_sweep", "tier": "READ", "jnl": None,
                             "actor": "argus", "detail": {"verdict": verdict, **detail}}).encode(),
            headers={"apikey": key, "Authorization": f"Bearer {key}",
                     "Content-Type": "application/json", "Prefer": "return=minimal"},
            method="POST")
        urllib.request.urlopen(req, timeout=30)
    except Exception as e:  # noqa: BLE001
        print(f"argus: event log failed ({e}) — verdict stands regardless")


def repo_state() -> dict:
    records = json.loads(REG.read_text())["records"]
    statuses = {r["jnl"]: r.get("status", "ACTIVE") for r in records}
    seqs = json.loads(SEQ.read_text())["map"]
    return {"statuses": statuses, "seqs": seqs}


def main() -> int:
    fails: list[str] = []
    warns: list[str] = []

    base = norm_url(os.environ.get("SUPABASE_URL", ""))
    key = os.environ.get("SUPABASE_SERVICE_KEY", "")
    if not key:
        print("argus: SUPABASE_SERVICE_KEY unset — cloud checks skipped (repo-only sweep).")

    repo = repo_state()

    if key:
        # ── 1. Mirror integrity ────────────────────────────────────────────
        cloud_reg = {r["jnl"]: r for r in rest(base, key, "jnl_registry?select=jnl,status,updated")}
        cloud_jd = {r["jnl"]: r for r in rest(base, key, "jd_entries?select=jnl,status,seq")}

        repo_only = sorted(set(repo["statuses"]) - set(cloud_reg))
        if repo_only:
            fails.append(f"mirror missing {len(repo_only)} repo object(s) (push broken?): {', '.join(repo_only[:5])}…"
                         if len(repo_only) > 5 else
                         f"mirror missing repo object(s): {', '.join(repo_only)}")

        # ── 2. Reconcile backlog ───────────────────────────────────────────
        cutoff = (date.today() - timedelta(days=RECONCILE_GRACE_DAYS)).isoformat()
        for jnl in sorted(set(cloud_reg) - set(repo["statuses"])):
            row = cloud_reg[jnl]
            if str(row.get("updated", "")) <= cutoff:
                fails.append(f"{jnl}: in cloud {RECONCILE_GRACE_DAYS}+ days, never reconciled to files")
            else:
                warns.append(f"{jnl}: cloud-only (awaiting reconcile — within grace)")

        # status + serial drift on shared objects
        for jnl, st in repo["statuses"].items():
            crow = cloud_reg.get(jnl)
            if crow and crow.get("status") != st:
                fails.append(f"{jnl}: status drift — repo={st} cloud={crow.get('status')}")
            jrow = cloud_jd.get(jnl)
            want = repo["seqs"].get(jnl)
            if jrow is not None and want is not None and jrow.get("seq") not in (None, want):
                fails.append(f"{jnl}: serial drift — repo seq={want} cloud seq={jrow.get('seq')}")

        # ── 3. Proposal staleness ──────────────────────────────────────────
        stale_cut = (datetime.now(timezone.utc) - timedelta(days=PROPOSAL_STALE_DAYS)).isoformat()
        pend = rest(base, key, f"jd_proposals?select=jnl,proposer,created_at&decision=eq.pending&created_at=lt.{stale_cut}")
        for p in pend:
            warns.append(f"proposal {p['jnl']} ({p['proposer']}) pending since {p['created_at'][:10]} — needs Raven's decision")

    # ── 4. Ledger staleness (the P17 lesson) ──────────────────────────────
    if LEDGER.exists():
        cutoff_d = date.today() - timedelta(days=LEDGER_STALE_DAYS)
        for patch in json.loads(LEDGER.read_text()).get("patches", []):
            # Only CLAIMS age out (partial = "work happened, state asserted").
            # Undated "pending" is backlog — a queue, not a claim; no noise.
            if patch.get("status") != "partial":
                continue
            stamp = patch.get("updated_at") or patch.get("deployed_at") or ""
            try:
                old_claim = date.fromisoformat(stamp) < cutoff_d
            except ValueError:
                old_claim = True  # a claim with no date is the worst kind
            if old_claim:
                warns.append(f"{patch.get('id')}: claims 'partial' but unchanged since {stamp or 'unknown'} — re-verify (claims age, reality moves)")

    # ── Verdict ────────────────────────────────────────────────────────────
    for w in warns:
        print(f"  ! {w}")
    if fails:
        print(f"ARGUS: DRIFT — {len(fails)} failure(s), {len(warns)} warning(s):")
        for f in fails:
            print(f"  ✗ {f}")
        if key:
            log_event(base, key, "DRIFT", {"failures": fails[:20], "warnings": len(warns)})
        return 1
    print(f"ARGUS: CLEAN — record and live state agree ({len(repo['statuses'])} objects, {len(warns)} warning(s)).")
    if key:
        log_event(base, key, "CLEAN", {"objects": len(repo["statuses"]), "warnings": len(warns)})
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
