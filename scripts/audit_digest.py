#!/usr/bin/env python3
"""
audit_digest.py — generate weekly and monthly digests from audit/audit_log entries.
Run manually or via CI on Friday evenings / end of month.

Usage:
  python3 scripts/audit_digest.py --week 2026-W26
  python3 scripts/audit_digest.py --month 2026-M06
  python3 scripts/audit_digest.py --week 2026-W26 --dry-run
"""

import argparse
import json
import os
import re
import sys
from datetime import datetime, date, timedelta
from pathlib import Path

ROOT = Path(__file__).parent.parent
AUDIT_LOG = ROOT / "audit" / "audit_log"
WEEK_ROOT = ROOT / "audit"          # year/week folders live here
MONTH_ROOT = ROOT / "audit"         # year/month folders live here

ISO_MONTH_RE = re.compile(r"^(\d{4})-(\d{2})$")  # e.g. 2026-06


def iso_week_start(year: int, week: int) -> date:
    """Return the Monday of ISO week [year, week]."""
    jan4 = date(year, 1, 4)
    return jan4 + timedelta(weeks=week - 1, days=-jan4.weekday())


def iso_week_end(year: int, week: int) -> date:
    s = iso_week_start(year, week)
    return s + timedelta(days=6)


def parse_week_label(label: str):
    m = re.match(r"^(\d{4})-W(\d{2})$", label)
    if not m:
        raise ValueError(f"Bad week label: {label} (need YYYY-Www)")
    return int(m.group(1)), int(m.group(2))


def parse_month_label(label: str):
    m = ISO_MONTH_RE.match(label)
    if not m:
        raise ValueError(f"Bad month label: {label} (need YYYY-MM)")
    return int(m.group(1)), int(m.group(2))


def parse_audit_date(filename: str) -> date | None:
    """Extract date from '2026-06-25T0125-session-audit-...'."""
    m = re.match(r"^(\d{4}-\d{2}-\d{2})T", filename)
    if m:
        return date.fromisoformat(m.group(1))
    return None


def read_audit(path: Path) -> dict:
    lines = path.read_text().splitlines()
    # Title line
    title = lines[0].lstrip("# ").strip() if lines else path.name
    # Extract key fields from frontmatter-free style
    meta = {"commits": [], "items": []}
    in_items = False
    for i, line in enumerate(lines[1:], 1):
        if line.startswith("**Commit"):
            m = re.search(r"`([^`]+)`", line)
            if m: meta["commits"].append(m.group(1))
        if line.startswith("**Commits"):
            meta["commits"] = re.findall(r"`([^`]+)`", line)
        if line.strip().startswith("## Items completed") or line.strip().startswith("## Intent"):
            in_items = True
        if in_items and line.strip().startswith("##"):
            in_items = False
    return {"title": title, "meta": meta, "body": "\n".join(lines)}


def scan_for_week(year: int, week: int):
    start = iso_week_start(year, week)
    end = iso_week_end(year, week)
    entries = []
    for f in sorted(AUDIT_LOG.glob("*.md")):
        d = parse_audit_date(f.name)
        if d and start <= d <= end:
            entries.append(read_audit(f))
    return entries, start, end


def scan_for_month(year: int, month: int):
    start = date(year, month, 1)
    # Last day of month
    if month == 12:
        end = date(year + 1, 1, 1) - timedelta(days=1)
    else:
        end = date(year, month + 1, 1) - timedelta(days=1)
    entries = []
    for f in sorted(AUDIT_LOG.glob("*.md")):
        d = parse_audit_date(f.name)
        if d and start <= d <= end:
            entries.append(read_audit(f))
    return entries, start, end


def extract_intents(entries: list) -> list[str]:
    intents = []
    for e in entries:
        body = e["body"]
        # Find Intent section
        m = re.search(r"## Intent\s*\n(.*?)(?=\n##|\Z)", body, re.DOTALL)
        if m:
            items = re.findall(r"^\d+\.\s+(.+)$", m.group(1), re.MULTILINE)
            intents.extend(items)
    return intents


def extract_items(entries: list) -> list[tuple[str, str]]:
    """(section_header, item_text)"""
    results = []
    for e in entries:
        body = e["body"]
        # Find Items completed
        m = re.search(r"## Items completed\s*\n(.*?)(?=\n##|\n#|\Z)", body, re.DOTALL)
        if m:
            section = re.findall(r"###\s+(.+)$", m.group(1), re.MULTILINE)
            for s in section:
                results.append((s.strip(), e["title"]))
    return results


def all_commits(entries: list) -> list[str]:
    commits = []
    for e in entries:
        commits.extend(e["meta"]["commits"])
    return commits


def format_week_digest(entries, start, end, week_label, dry_run=False):
    if not entries:
        print(f"No entries for {week_label} ({start} – {end})")
        return
    intents = extract_intents(entries)
    items = extract_items(entries)
    commits = all_commits(entries)

    body_lines = [
        f"# Audit Digest — {week_label}",
        f"**Period:** {start.strftime('%Y-%m-%d')} → {end.strftime('%Y-%m-%d')} (ISO week)",
        f"**Sessions:** {len(entries)}",
        "",
        "## Commits",
    ]
    body_lines += [f"- `{c}`" for c in commits] if commits else body_lines.append("_none committed_")
    body_lines += ["", "## What We Built"]
    if items:
        seen = set()
        for item, session in items:
            short = item.split("\n")[0].strip()
            if short not in seen:
                body_lines.append(f"- {short}")
                seen.add(short)
    else:
        body_lines.append("_no item records found_")
    body_lines += ["", "## Session Records"]
    for e in entries:
        body_lines.append(f"- [[audit_log/{e['title'].split('—')[0].strip()}.md|{e['title']}]]")
    body_lines += ["", "## Intents (what was asked for)"]
    body_lines += [f"- {i}" for i in intents] if intents else body_lines.append("_none extracted_")
    body_lines.append(f"_Generated {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')} · `scripts/audit_digest.py`_")

    out = "\n".join(body_lines)
    year_dir = WEEK_ROOT / str(start.year)
    out_path = year_dir / f"{week_label}-WEEKLY-DIGEST.md"
    year_dir.mkdir(exist_ok=True)

    if dry_run:
        print(f"[DRY RUN] Would write {out_path}")
        print(out[:500] + "...")
        return

    out_path.write_text(out)
    print(f"Wrote {out_path} ({len(out):,} bytes, {len(entries)} sessions)")
    return out_path


def format_month_digest(entries, start, end, month_label, dry_run=False):
    if not entries:
        print(f"No entries for {month_label} ({start} – {end})")
        return

    intents = extract_intents(entries)
    items = extract_items(entries)
    commits = all_commits(entries)
    weeks: dict[str, list] = {}
    for e in entries:
        d = parse_audit_date(e["title"].split("—")[0].strip() + ".md")
        if d:
            w = d.isocalendar()[1]
            wl = f"{d.year}-W{w:02d}"
            weeks.setdefault(wl, []).append(e)

    body_lines = [
        f"# Audit Digest — {month_label}",
        f"**Period:** {start.strftime('%Y-%m-%d')} → {end.strftime('%Y-%m-%d')}",
        f"**Sessions:** {len(entries)} · **Commits:** {len(commits)} · **Weeks:** {len(weeks)}",
        "",
        "## Commits",
    ]
    body_lines += [f"- `{c}`" for c in commits] if commits else body_lines.append("_none committed_")
    body_lines += ["", "## What We Built"]
    if items:
        seen = set()
        for item, session in items:
            short = item.split("\n")[0].strip()
            if short not in seen:
                body_lines.append(f"- {short}")
                seen.add(short)
    else:
        body_lines.append("_no item records found_")
    body_lines += ["", "## By Week"]
    for wl in sorted(weeks.keys()):
        body_lines.append(f"### {wl} ({len(weeks[wl])} session{'s' if len(weeks[wl]) > 1 else ''})")
        for e in weeks[wl]:
            body_lines.append(f"- [[audit_log/{e['title'].split('—')[0].strip()}.md|{e['title']}]]")
    body_lines.append(f"_Generated {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')} · `scripts/audit_digest.py`_")

    out = "\n".join(body_lines)
    month_dir = MONTH_ROOT / f"{start.year}"
    out_path = month_dir / f"{month_label}-MONTHLY-DIGEST.md"
    month_dir.mkdir(exist_ok=True)

    if dry_run:
        print(f"[DRY RUN] Would write {out_path}")
        print(out[:500] + "...")
        return

    out_path.write_text(out)
    print(f"Wrote {out_path} ({len(out):,} bytes, {len(entries)} sessions, {len(weeks)} weeks)")
    return out_path


def main():
    ap = argparse.ArgumentParser(description="Generate audit digests from audit_log entries.")
    ap.add_argument("--week", metavar="YYYY-Www", help="Generate weekly digest (e.g. 2026-W26)")
    ap.add_argument("--month", metavar="YYYY-MM", help="Generate monthly digest (e.g. 2026-06)")
    ap.add_argument("--dry-run", action="store_true", help="Print without writing")
    ap.add_argument("--ingest", action="store_true",
                    help="Move existing audit_log/*.md into year/week folders (one-time migration)")
    args = ap.parse_args()

    if args.ingest:
        ingest_existing()
        return

    if args.week:
        year, wk = parse_week_label(args.week)
        entries, start, end = scan_for_week(year, wk)
        format_week_digest(entries, start, end, args.week, args.dry_run)
    elif args.month:
        year, month = parse_month_label(args.month)
        entries, start, end = scan_for_month(year, month)
        format_month_digest(entries, start, end, args.month, args.dry_run)
    else:
        ap.print_help()
        sys.exit(1)


def ingest_existing():
    """One-time migration: move flat audit_log entries into year/week folders."""
    moved = 0
    for f in sorted(AUDIT_LOG.glob("*.md")):
        d = parse_audit_date(f.name)
        if not d:
            print(f"SKIP (can't parse date): {f.name}")
            continue
        iso = d.isocalendar()
        wl = f"{iso[0]}-W{iso[1]:02d}"
        dest = WEEK_ROOT / str(d.year) / wl / f.name
        dest.parent.mkdir(parents=True, exist_ok=True)
        if dest.exists():
            print(f"SKIP (already exists): {dest}")
            continue
        import shutil
        shutil.copy2(f, dest)
        print(f"  {f.name} → {dest.parent.name}/{dest.name}")
        moved += 1
    print(f"\nIngested {moved} audit entries into year/week folders.")


if __name__ == "__main__":
    main()
