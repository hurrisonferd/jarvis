#!/usr/bin/env python3
"""MNEMOS — the remember loop. Folds a session insight into the right knowledge
partition AND queues it for the live memory, so the entity gets richer every
session instead of forgetting.

The companion grows three ways and this wires all three from one call:
  1. the partitioned record  -> mnemos/knowledge/<category>.md (durable, in repo)
  2. the learned ledger       -> mnemos/memories/learned.jsonl (append-only trail)
  3. the live memory          -> prints a ready MNEMOS insert (seed + embed)

Usage:
  python3 scripts/companion_remember.py raven "Raven prefers X over Y"
  python3 scripts/companion_remember.py project:grid "GNPL is the node handshake"
  python3 scripts/companion_remember.py session "Wired the remember loop"

Categories: raven jarvis mission relationship governance session  (or project:<name>)
"""
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
KNOWLEDGE = ROOT / "mnemos" / "knowledge"
SESSIONS = ROOT / "mnemos" / "sessions"
LEDGER = ROOT / "mnemos" / "memories" / "learned.jsonl"

# category -> (file path, MNEMOS source_type for the live-memory seed)
CATEGORIES = {
    "raven":        (KNOWLEDGE / "raven.md",        "raven_profile"),
    "jarvis":       (KNOWLEDGE / "jarvis.md",       "jarvis_identity"),
    "mission":      (KNOWLEDGE / "mission.md",      "mission"),
    "relationship": (KNOWLEDGE / "relationship.md", "decision"),
    "governance":   (KNOWLEDGE / "governance.md",   "governance"),
}


def resolve(category: str):
    """Return (path, source_type, normalized_category). Pure — unit tested."""
    cat = (category or "").strip().lower()
    if cat.startswith("project:"):
        name = cat.split(":", 1)[1].strip().replace(" ", "-")
        if not name:
            return None
        return (KNOWLEDGE / "projects" / f"{name}.md", "raven_profile", f"project:{name}")
    if cat == "session":
        day = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        return (SESSIONS / f"{day}.md", "session_summary", "session")
    if cat in CATEGORIES:
        path, st = CATEGORIES[cat]
        return (path, st, cat)
    return None


def ledger_entry(category: str, text: str, source_type: str) -> dict:
    return {
        "ts": datetime.now(timezone.utc).isoformat()[:19] + "Z",
        "category": category,
        "text": text.strip()[:500],
        "source_type": source_type,
    }


def _append_md(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    if not path.exists():
        title = path.stem.replace("-", " ").title()
        path.write_text(f"# {title}\n\n*Partition of the companion memory. Grown by the remember loop.*\n\n", encoding="utf-8")
    with path.open("a", encoding="utf-8") as f:
        f.write(f"- [{stamp}] {text.strip()}\n")


def _append_ledger(entry: dict) -> None:
    LEDGER.parent.mkdir(parents=True, exist_ok=True)
    with LEDGER.open("a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")


def main(argv: list) -> int:
    if len(argv) < 2:
        print(__doc__)
        return 2
    category, text = argv[0], " ".join(argv[1:]).strip()
    r = resolve(category)
    if r is None:
        print(f"Unknown category '{category}'. Use: {', '.join(CATEGORIES)} session project:<name>")
        return 2
    path, source_type, norm = r
    if not text:
        print("Nothing to remember — empty text.")
        return 2

    _append_md(path, text)
    entry = ledger_entry(norm, text, source_type)
    _append_ledger(entry)

    rel = path.relative_to(ROOT)
    print(f"remembered -> {rel}  (live-memory source_type: {source_type})")
    # The seed for the live brain: paste into execute_sql, then run mnemos-embed backfill.
    safe = text.replace("'", "''")
    print("MNEMOS seed:")
    print(f"  insert into public.mnemos_memories (id, source_id, source_type, text, tags, timestamp, metadata)")
    print(f"  values (gen_random_uuid(), gen_random_uuid(), '{source_type}', '{safe}', "
          f"array['learned','{norm.split(':')[0]}'], now(), '{{\"via\":\"remember_loop\"}}'::jsonb);")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
