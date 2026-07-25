#!/usr/bin/env python3
"""MNEMOS — the narrative log system. Record thoughts, ideas, and brainstorming
relentlessly, without bloat.

Design (Raven's spec):
  - Every log carries a SUMMARY (front-matter + visible) for fast retrieval.
  - Every section carries a NOTE — a one-line annotation for retrieval/audit.
  - Logs live chronologically: memory/mnemos/logs/YYYY/MM/YYYY-MM-DD_<slug>.md, named to
    match their summary.
  - INDEX.md is the map: summary + date + tags + path. Load it to find a log.
  - Old logs COMPACT: body reduced to summary + section notes + timestamp; the
    full text is archived for audit. Signal stays, bulk goes.

Commands:
  new "<title>" --summary "<one line>" [--tags a,b]   create a dated log scaffold
  reindex                                              rebuild INDEX.md from all logs
  compact --older-than <days>                          age old logs down to summaries
"""
import argparse
import re
import shutil
import sys
from datetime import datetime, timezone, date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LOGS = ROOT / "mnemos" / "logs"
ARCHIVE = LOGS / "archive"
INDEX = LOGS / "INDEX.md"


# ---------- pure helpers (unit tested) ----------

def slugify(text: str, maxlen: int = 48) -> str:
    s = re.sub(r"[^a-z0-9]+", "-", (text or "").lower()).strip("-")
    return (s[:maxlen].rstrip("-")) or "untitled"


def log_path(d: date, slug: str) -> Path:
    return LOGS / f"{d.year:04d}" / f"{d.month:02d}" / f"{d.isoformat()}_{slug}.md"


def render_front_matter(meta: dict) -> str:
    tags = ", ".join(meta.get("tags", []))
    return (
        "---\n"
        f"title: {meta.get('title','')}\n"
        f"date: {meta.get('date','')}\n"
        f"summary: {meta.get('summary','')}\n"
        f"tags: {tags}\n"
        f"status: {meta.get('status','active')}\n"
        "---\n"
    )


def parse_front_matter(text: str) -> dict:
    m = re.match(r"^---\n(.*?)\n---\n", text, re.S)
    meta = {"title": "", "date": "", "summary": "", "tags": [], "status": "active"}
    if not m:
        return meta
    for line in m.group(1).splitlines():
        if ":" not in line:
            continue
        k, v = line.split(":", 1)
        k, v = k.strip(), v.strip()
        if k == "tags":
            meta["tags"] = [t.strip() for t in v.split(",") if t.strip()]
        elif k in meta:
            meta[k] = v
    return meta


def section_notes(text: str) -> list:
    """Return [(section_title, note)] — the retrieval/audit annotations."""
    out = []
    cur = None
    for line in text.splitlines():
        h = re.match(r"^##\s+(.*)", line)
        if h:
            cur = h.group(1).strip()
            continue
        n = re.match(r"^\*[_ ]?[Nn]ote:\s*(.*?)\*\s*$", line)
        if n and cur:
            out.append((cur, n.group(1).strip()))
            cur = None  # one note per section
    return out


def index_row(meta: dict, rel_path: str) -> str:
    tags = ", ".join(meta.get("tags", []))
    return f"| {meta.get('date','')} | {meta.get('summary','')} | {tags} | [{Path(rel_path).name}]({rel_path}) | {meta.get('status','active')} |"


# ---------- file operations ----------

def _today() -> date:
    return datetime.now(timezone.utc).date()


def new_log(title: str, summary: str, tags: list) -> Path:
    d = _today()
    slug = slugify(summary or title)
    path = log_path(d, slug)
    path.parent.mkdir(parents=True, exist_ok=True)
    meta = {"title": title, "date": d.isoformat(), "summary": summary, "tags": tags, "status": "active"}
    body = (
        render_front_matter(meta)
        + f"\n# {title}\n\n> **Summary:** {summary}\n\n"
        + "## Context\n*Note: why this log exists, what prompted it.*\n\n\n"
        + "## Thoughts\n*Note: the raw thinking / brainstorming.*\n\n\n"
        + "## Decisions\n*Note: what we settled, if anything.*\n\n\n"
        + "## Next\n*Note: open threads to carry forward.*\n\n"
    )
    path.write_text(body, encoding="utf-8")
    reindex()
    return path


def _iter_logs():
    for p in sorted(LOGS.rglob("*.md")):
        if p.name == "INDEX.md" or ARCHIVE in p.parents:
            continue
        yield p


def reindex() -> int:
    rows = []
    for p in _iter_logs():
        meta = parse_front_matter(p.read_text(encoding="utf-8"))
        rows.append((meta.get("date", ""), index_row(meta, str(p.relative_to(LOGS)))))
    rows.sort(reverse=True)  # newest first
    body = [
        "# Logs Index",
        "",
        "The map of the narrative record. Load this, find the log, open it.",
        "Compacted logs keep their summary + section notes; full text is in `archive/`.",
        "",
        "| Date | Summary | Tags | Log | Status |",
        "|------|---------|------|-----|--------|",
    ]
    body += [r for _, r in rows]
    INDEX.parent.mkdir(parents=True, exist_ok=True)
    INDEX.write_text("\n".join(body) + "\n", encoding="utf-8")
    return len(rows)


def compact_log(path: Path) -> bool:
    text = path.read_text(encoding="utf-8")
    meta = parse_front_matter(text)
    if meta.get("status") == "compacted":
        return False
    # archive the full original
    rel = path.relative_to(LOGS)
    dest = ARCHIVE / rel
    dest.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(path, dest)
    # write the distilled version: summary + section notes + timestamp
    meta["status"] = "compacted"
    notes = section_notes(text)
    stamp = datetime.now(timezone.utc).isoformat()[:19] + "Z"
    out = [render_front_matter(meta), f"\n# {meta.get('title','')}\n",
           f"> **Summary:** {meta.get('summary','')}\n",
           f"*Compacted {stamp}. Full text archived at `archive/{rel}`.*\n",
           "## Distilled section notes"]
    for sec, note in notes:
        out.append(f"- **{sec}:** {note}")
    if not notes:
        out.append("- (no section notes captured)")
    path.write_text("\n".join(out) + "\n", encoding="utf-8")
    return True


def compact_older_than(days: int) -> int:
    cutoff = _today().toordinal() - days
    n = 0
    for p in _iter_logs():
        meta = parse_front_matter(p.read_text(encoding="utf-8"))
        try:
            d = date.fromisoformat(meta.get("date", ""))
        except ValueError:
            continue
        if d.toordinal() < cutoff and meta.get("status") != "compacted":
            if compact_log(p):
                n += 1
    if n:
        reindex()
    return n


def main(argv: list) -> int:
    ap = argparse.ArgumentParser(prog="companion_log")
    sub = ap.add_subparsers(dest="cmd")
    p_new = sub.add_parser("new")
    p_new.add_argument("title")
    p_new.add_argument("--summary", default="")
    p_new.add_argument("--tags", default="")
    sub.add_parser("reindex")
    p_comp = sub.add_parser("compact")
    p_comp.add_argument("--older-than", type=int, default=90)
    args = ap.parse_args(argv)

    if args.cmd == "new":
        tags = [t.strip() for t in args.tags.split(",") if t.strip()]
        path = new_log(args.title, args.summary or args.title, tags)
        print(f"log -> {path.relative_to(ROOT)}")
        print("INDEX.md updated. Fill the sections; each keeps a *Note:* for retrieval.")
    elif args.cmd == "reindex":
        print(f"indexed {reindex()} logs -> {INDEX.relative_to(ROOT)}")
    elif args.cmd == "compact":
        print(f"compacted {compact_older_than(args.older_than)} logs older than {args.older_than}d")
    else:
        print(__doc__)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
