"""new — mint a governed object in perfect JFS hygiene (the intake scaffolder).

Two ways an object is born (both land identically):
  1. This tool: mints the next JNL, writes the file with self-describing frontmatter
     at its JSL-correct location, then reseeds + validates. One command, fully governed.
  2. Drop-in: write the file yourself with the same frontmatter anywhere under a
     seed.py SCAN_ROOT and run seed.py — the file is its own manifest.

Usage:
  python core/JarvisMain/yggdrasil/tools/new.py --project Deoxys --type JIP \
      --name "Telemetry Pipeline" [--status TASK] [--tags a,b] \
      [--definition "..."] [--purpose "..."]
  python core/JarvisMain/yggdrasil/tools/new.py --new-project Grid --code GRD \
      [--definition "..."] [--purpose "..."]

Filename follows the FMT standard (IMPL-FMT-SPEC-0001 §3):
  <PROJECT><TYPE>-<MMDDYY>-<NNNN>-<SUBJECT>.md   e.g. DEOXYSJIP-060926-0001-TELEMETRY-PIPELINE.md
JNL: PROJ-<code>-<TYPE>-<NNNN>. Default status: TASK for JGPP (exploration), ACTIVE otherwise.
"""
from __future__ import annotations
import argparse
import json
import re
import subprocess
import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import jnl as jnllib  # noqa: E402

ROOT = Path(__file__).resolve().parents[3]
TOOLS = Path(__file__).resolve().parent
CODES_PATH = ROOT / "JarvisMain" / "yggdrasil" / "jfs" / "project-codes.json"
REG_PATH = ROOT / "JarvisMain" / "yggdrasil" / "lal" / "address-registry.json"
PROJECT_TYPES = ("JGPP", "JIP", "JD", "BIO")
TODAY = date.today()


def load_codes() -> dict:
    return json.loads(CODES_PATH.read_text())


def resolve_project(codes: dict, key: str) -> tuple[str, dict]:
    """Accept a project code or name, case-insensitive."""
    for code, info in codes["codes"].items():
        if key.upper() == code or key.lower() == info["name"].lower() \
                or key.lower() == Path(info["folder"]).name.lower():
            return code, info
    raise SystemExit(f"new: unknown project '{key}' — codes: {', '.join(sorted(codes['codes']))} "
                     f"(add one with --new-project)")


def next_log(code: str, typ: str, folder: Path) -> int:
    """Next free Log for PROJ-<code>-<typ>: max(registry, filenames in the type folder) + 1."""
    prefix = f"PROJ-{code}-{typ}-"
    n = 0
    if REG_PATH.exists():
        for rec in json.loads(REG_PATH.read_text())["records"]:
            if rec["jnl"].startswith(prefix):
                n = max(n, int(rec["jnl"][len(prefix):len(prefix) + 4]))
    for f in folder.glob("*.md"):
        m = re.search(r"-(\d{4})-", f.name)
        if m:
            n = max(n, int(m.group(1)))
    return n + 1


def slug(name: str) -> str:
    return re.sub(r"[^A-Za-z0-9]+", "-", name).strip("-").upper()


def write_entry(code: str, info: dict, typ: str, name: str, status: str,
                tags: list[str], definition: str, purpose: str) -> Path:
    folder = ROOT / info["folder"] / typ
    folder.mkdir(parents=True, exist_ok=True)
    log = next_log(code, typ, folder)
    addr = f"PROJ-{code}-{typ}-{log:04d}"
    jnllib.parse(addr)  # grammar gate before anything touches disk
    proj = Path(info["folder"]).name.upper()
    fname = f"{proj}{typ}-{TODAY.strftime('%m%d%y')}-{log:04d}-{slug(name)}.md"
    path = folder / fname
    body = "\n".join([
        "---",
        f"name: {name}",
        f"type: {typ}",
        f"jnl: {addr}",
        f"status: {status}",
        f"created: {TODAY.isoformat()}",
        f"tags: [{', '.join(tags)}]",
        f"definition: {definition}",
        f"purpose: {purpose}",
        "related: []",
        "---",
        "",
        f"# {addr} — {name}",
        "",
    ])
    path.write_text(body)
    print(f"new: {addr} -> {path.relative_to(ROOT)}")
    return path


def regenerate() -> None:
    for tool in ("seed.py", "validate.py", "graph_export.py"):
        subprocess.run([sys.executable, str(TOOLS / tool)], cwd=ROOT, check=True)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--project", help="project code or name (see jfs/project-codes.json)")
    ap.add_argument("--new-project", help="scaffold a new project node by name")
    ap.add_argument("--code", help="JNL System code for --new-project (2-4 chars A-Z0-9)")
    ap.add_argument("--type", choices=PROJECT_TYPES, help="artifact type")
    ap.add_argument("--name", help="human name of the object")
    ap.add_argument("--status", help="JSS status (default: TASK for JGPP, ACTIVE otherwise)")
    ap.add_argument("--tags", default="", help="comma-separated tags")
    ap.add_argument("--definition", default="", help="what it is")
    ap.add_argument("--purpose", default="", help="why it exists")
    args = ap.parse_args()
    codes = load_codes()

    if args.new_project:
        if not args.code or not re.fullmatch(r"[A-Z0-9]{2,4}", args.code):
            raise SystemExit("new: --new-project requires --code (2-4 chars A-Z0-9)")
        if args.code in codes["codes"]:
            raise SystemExit(f"new: code {args.code} already taken by {codes['codes'][args.code]['name']}")
        folder = f"JarvisSide/Projects/{args.new_project}"
        codes["codes"][args.code] = {"name": args.new_project, "folder": folder}
        codes["codes"] = dict(sorted(codes["codes"].items()))
        CODES_PATH.write_text(json.dumps(codes, indent=2) + "\n")
        for d in PROJECT_TYPES:
            sub = ROOT / folder / d
            sub.mkdir(parents=True, exist_ok=True)
            (sub / ".gitkeep").touch()
        write_entry(args.code, codes["codes"][args.code], "BIO", args.new_project, "ACTIVE",
                    [t for t in args.tags.split(",") if t] or ["project"],
                    args.definition or f"{args.new_project} project.",
                    args.purpose or "Project node bio.")
        regenerate()
        return

    if not (args.project and args.type and args.name):
        ap.error("--project, --type, and --name are required (or use --new-project)")
    status = args.status or ("TASK" if args.type == "JGPP" else "ACTIVE")
    if status not in jnllib.STATUSES:
        raise SystemExit(f"new: status '{status}' not in JSS vocabulary {sorted(jnllib.STATUSES)}")
    code, info = resolve_project(codes, args.project)
    write_entry(code, info, args.type, args.name, status,
                [t.strip() for t in args.tags.split(",") if t.strip()],
                args.definition, args.purpose)
    regenerate()


if __name__ == "__main__":
    main()
