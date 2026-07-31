#!/usr/bin/env python3
"""Generate non-destructive README scaffolds and local indexes across the repo."""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path

MARKER = "<!-- GENERATED-SCAFFOLD-FUNGUS -->"
DEFAULT_EXCLUDES = {".git", ".venv", "venv", "node_modules", "__pycache__", ".pytest_cache", ".mypy_cache", "dist", "build"}


def load_config(root: Path) -> dict:
    path = root / "operations" / "scaffold-fungus.json"
    return json.loads(path.read_text()) if path.exists() else {}


def visible_entries(path: Path, excludes: set[str]) -> tuple[list[Path], list[Path]]:
    children = [p for p in path.iterdir() if p.name not in excludes and not p.is_symlink()]
    return sorted([p for p in children if p.is_dir()], key=lambda p: p.name.lower()), sorted([p for p in children if p.is_file()], key=lambda p: p.name.lower())


def title_for(root: Path, path: Path) -> str:
    return root.name if path == root else path.name.replace("-", " ").replace("_", " ").strip().title()


def readme_text(root: Path, path: Path, dirs: list[Path], files: list[Path]) -> str:
    rel = "." if path == root else path.relative_to(root).as_posix()
    parent = None if path == root else os.path.relpath(path.parent / "README.md", path).replace(os.sep, "/")
    lines = [MARKER, f"# {title_for(root, path)}", "", f"**Route:** `{rel}`", "", "Generated local scaffold. Add hand-authored purpose or laws above this marker only by replacing this file intentionally.", ""]
    if parent:
        lines += [f"**Parent map:** [{parent}]({parent})", ""]
    if dirs:
        lines += ["## Child routes", ""] + [f"- [`{d.name}/`]({d.name}/)" for d in dirs] + [""]
    if files:
        lines += ["## Local files", ""] + [f"- [`{f.name}`]({f.name})" for f in files if f.name not in {"README.md", "INDEX.generated.json"}] + [""]
    return "\n".join(lines).rstrip() + "\n"


def index_data(root: Path, path: Path, dirs: list[Path], files: list[Path]) -> dict:
    return {
        "schema": "repository.scaffold.index.v1",
        "route": "." if path == root else path.relative_to(root).as_posix(),
        "parent": None if path == root else ("." if path.parent == root else path.parent.relative_to(root).as_posix()),
        "directories": [d.name for d in dirs],
        "files": [f.name for f in files if f.name != "INDEX.generated.json"],
        "generated_by": "operations/scaffold_fungus.py",
    }


def eligible(root: Path, path: Path, excludes: set[str], excluded_routes: list[str]) -> bool:
    rel = "." if path == root else path.relative_to(root).as_posix()
    if any(part in excludes for part in path.relative_to(root).parts):
        return False
    return not any(rel == x or rel.startswith(x.rstrip("/") + "/") for x in excluded_routes)


def run(root: Path, check: bool) -> int:
    config = load_config(root)
    excludes = DEFAULT_EXCLUDES | set(config.get("exclude_names", []))
    excluded_routes = config.get("exclude_routes", [])
    changed: list[str] = []
    indexed: list[dict] = []

    paths = [root] + sorted([p for p in root.rglob("*") if p.is_dir()], key=lambda p: p.as_posix().lower())
    for path in paths:
        if not eligible(root, path, excludes, excluded_routes):
            continue
        dirs, files = visible_entries(path, excludes)
        if path != root and not dirs and not files:
            continue
        readme = path / "README.md"
        if not readme.exists():
            changed.append(readme.relative_to(root).as_posix())
            if not check:
                readme.write_text(readme_text(root, path, dirs, files))
        index = path / "INDEX.generated.json"
        payload = json.dumps(index_data(root, path, dirs, files), indent=2, ensure_ascii=False) + "\n"
        if not index.exists() or index.read_text() != payload:
            changed.append(index.relative_to(root).as_posix())
            if not check:
                index.write_text(payload)
        indexed.append(index_data(root, path, dirs, files))

    master = root / config.get("master_index", "docs/scaffolds/REPOSITORY-MASTER-INDEX.generated.md")
    master.parent.mkdir(parents=True, exist_ok=True)
    rows = ["# Repository Master Index", "", MARKER, "", "Generated route map. Existing authored READMEs remain authoritative.", ""]
    for item in indexed:
        route = item["route"]
        link = "../../" if route == "." else "../../" + route + "/"
        rows.append(f"- [`{route}`]({link}) — {len(item['directories'])} child directories, {len(item['files'])} files")
    master_text = "\n".join(rows) + "\n"
    if not master.exists() or master.read_text() != master_text:
        changed.append(master.relative_to(root).as_posix())
        if not check:
            master.write_text(master_text)

    if changed:
        print("Scaffold drift:")
        print("\n".join(f"- {p}" for p in changed))
        return 1 if check else 0
    print("Scaffold fungus is current.")
    return 0


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    raise SystemExit(run(Path(__file__).resolve().parents[1], args.check))
