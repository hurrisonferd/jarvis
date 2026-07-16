#!/usr/bin/env python3
"""MNEMOS + PROMETHEUS — decision capture.

Every commit is a dated proof of what was understood at that moment. This pulls
the governance-significant ones into a decision ledger so the "why" survives,
not just the "what". Run in CI on push to main; the workflow feeds it HEAD.

A commit is a DECISION when its subject carries an explicit governance marker
([DECISION] or [GL7-OK]) or is a feat/refactor (capability / structure change).
Chore, docs, ci, and test commits are noise for this ledger and skipped.

Pure function `extract_decision` is unit-tested. CLI mode reads git HEAD.

Run: python3 scripts/capture_decisions.py        # appends HEAD if a decision
     python3 scripts/test_capture_decisions.py    # tests
"""
import json
import re
import sys
from pathlib import Path

LEDGER = Path(__file__).resolve().parent.parent / "mnemos" / "memories" / "decisions.jsonl"

# Conventional types that count as decisions (capability / structure shifts).
DECISION_TYPES = {"feat", "fix", "refactor"}
MARKER = re.compile(r"\[(DECISION|GL7-OK)\]", re.IGNORECASE)
HEADER = re.compile(r"^(?P<type>\w+)(?:\((?P<scope>[^)]+)\))?(?P<bang>!)?:\s*(?P<subject>.+)$")


def extract_decision(sha: str, message: str, ts: str):
    """Return a decision dict if this commit is governance-significant, else None."""
    subject = (message or "").strip().splitlines()[0] if (message or "").strip() else ""
    if not subject:
        return None

    m = HEADER.match(subject)
    ctype = (m.group("type").lower() if m else "")
    scope = (m.group("scope") if m and m.group("scope") else "")
    clean_subject = (m.group("subject") if m else subject)

    is_marked = bool(MARKER.search(message or ""))
    is_decision_type = ctype in DECISION_TYPES

    if not (is_marked or is_decision_type):
        return None

    tags = ["decision"]
    if scope:
        tags.append(scope.split(":")[0].strip().lower())
    if MARKER.search(message or "") and "gl7" in MARKER.search(message or "").group(0).lower():
        tags.append("gl7")

    # Strip the marker tags out of the stored subject for a clean record.
    text = MARKER.sub("", clean_subject).strip().rstrip("[]").strip()

    return {
        "ts": ts,
        "sha": sha[:7],
        "text": text[:300],
        "tags": sorted(set(tags)),
        "source_type": "decision",
    }


def _git(cmd: str) -> str:
    import subprocess
    try:
        return subprocess.check_output(cmd, shell=True, text=True, stderr=subprocess.DEVNULL).strip()
    except Exception:
        return ""


def main() -> int:
    sha = _git("git rev-parse HEAD")
    message = _git("git log -1 --pretty=%B")
    ts = _git("git log -1 --pretty=%cI")[:19]
    if ts:
        ts += "Z"

    entry = extract_decision(sha, message, ts)
    if entry is None:
        print(f"Not a decision commit ({sha[:7]}) — skipping ledger.")
        return 0

    LEDGER.parent.mkdir(parents=True, exist_ok=True)
    existing = []
    if LEDGER.exists():
        for line in LEDGER.read_text().splitlines():
            line = line.strip()
            if line:
                try:
                    existing.append(json.loads(line))
                except Exception:
                    pass
    # Idempotent — don't double-record the same sha.
    if any(e.get("sha") == entry["sha"] for e in existing):
        print(f"Decision {entry['sha']} already in ledger — skipping.")
        return 0

    existing = existing[-299:]
    existing.append(entry)
    LEDGER.write_text("\n".join(json.dumps(e) for e in existing) + "\n")
    print(f"MNEMOS decision recorded: [{entry['sha']}] {entry['text'][:70]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
