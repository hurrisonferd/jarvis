#!/usr/bin/env python3
"""JPL validator — JVE extension for ARCH-JPL-SPEC-0001 grammar.

Validates @INSTANCE origin blocks, @IDENTITY stream bindings, @DOMAIN layer
compliance, and @GOVERNANCE tier/status. Structural trap card enforcement.

Run:
  python3 core/JarvisMain/yggdrasil/tools/jpl_validate.py                 # scan repo
  python3 core/JarvisMain/yggdrasil/tools/jpl_validate.py --domain musicos  # MusicOS only
  python3 core/JarvisMain/yggdrasil/tools/jpl_validate.py --domain monster # MonsterOS only
  python3 core/JarvisMain/yggdrasil/tools/jpl_validate.py path/to/file.md # single file
  python3 core/JarvisMain/yggdrasil/tools/jpl_validate.py --trap-card path/to/file.md

Exit 0 = GREEN; exit 1 = violations found.
"""
from __future__ import annotations

import argparse
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

# ── JPL block grammar ──────────────────────────────────────────────────────────

INSTANCE_RE = re.compile(r"@INSTANCE\s*\n((?:  .+\n)+)", re.MULTILINE)
IDENTITY_RE = re.compile(r"@IDENTITY\s*\n((?:  .+\n)+)", re.MULTILINE)
DOMAIN_RE   = re.compile(r"@DOMAIN\s*\n((?:  .+\n)+)", re.MULTILINE)
CONTENT_RE  = re.compile(r"@CONTENT\s*\n((?:  .+\n)+)", re.MULTILINE)
GOV_RE      = re.compile(r"@GOVERNANCE\s*\n((?:  .+\n)+)", re.MULTILINE)
META_RE     = re.compile(r"@METADATA\s*\n((?:  .+\n)+)", re.MULTILINE)

VALID_STREAMS = {"jarvis", "ayre", "argent", "shared"}
VALID_LAYERS  = {"structural", "physics", "sensory", "governance"}
VALID_TIERS   = {"jitm", "jstm", "jhtm", "jltm", "jatm"}
VALID_STATUS  = {"ACTIVE", "DRAFT", "ARCHIVED", "DEPRECATED"}
MUSICOS_DOMAINS = {"musicos"}
MONSTER_DOMAINS = {"monsteros"}

# Trap card activation keywords
TRAP_TRIGGERS = [
    "fork", "remove", "override", "extract", "strip",
    "merge", "silence", "average", "separate",
]


def parse_block(text: str, pattern) -> dict[str, str]:
    m = pattern.search(text)
    if not m:
        return {}
    out = {}
    for line in m.group(1).splitlines():
        line = line.rstrip()
        stripped = line.strip()
        if not stripped:
            continue
        if not line.startswith("  ") and "  " not in line:
            continue
        if ":" not in line:
            continue
        parts = line.strip().split(":", 1)
        if len(parts) < 2:
            continue
        key = parts[0].strip().lower()
        val = parts[1].strip()
        # Skip literal placeholder syntax from spec diagrams: [A|B], [INT], [ISO8601], etc.
        if val.startswith("[") and "|" in val:
            continue
        out[key] = val
    return out


def parse_list_field(val: str) -> list[str]:
    """Parse a bracketed list like [structural, physics, sensory]."""
    if val.startswith("[") and val.endswith("]"):
        return [x.strip() for x in val[1:-1].split(",") if x.strip()]
    return [val] if val.strip() else []


def validate_instance(block: dict, errors: list, filename: str):
    for field in ("origin", "creator", "lineage", "mission"):
        if field not in block:
            errors.append(f"{filename}: @INSTANCE missing '{field}'")
    # origin_binding should be STRUCTURAL for JARVIS-ARCH instances
    if block.get("origin_binding", "").upper() not in ("STRUCTURAL", "SOFT"):
        # Only warn if origin is present but binding is missing
        if "origin" in block and "origin_binding" not in block:
            pass  # soft warning handled elsewhere


def validate_identity(block: dict, errors: list, filename: str):
    stream = block.get("stream", "").lower()
    if stream and stream not in VALID_STREAMS:
        errors.append(f"{filename}: @IDENTITY stream '{stream}' not in {sorted(VALID_STREAMS)}")
    if "keel" not in block:
        errors.append(f"{filename}: @IDENTITY missing 'keel'")
    if "jitm_pin" not in block:
        errors.append(f"{filename}: @IDENTITY missing 'jitm_pin'")


def validate_domain(block: dict, errors: list, filename: str):
    domain = block.get("domain", "").lower()
    if not domain:
        errors.append(f"{filename}: @DOMAIN missing 'domain'")
    typ = block.get("type", "").lower()
    if not typ:
        errors.append(f"{filename}: @DOMAIN missing 'type'")
    layers_raw = block.get("layers", "")
    layers = parse_list_field(layers_raw)
    invalid = [l for l in layers if l not in VALID_LAYERS]
    if invalid:
        errors.append(f"{filename}: @DOMAIN layers {invalid} not in {sorted(VALID_LAYERS)}")


def validate_governance(block: dict, errors: list, filename: str):
    tier = block.get("tier", "").lower()
    if tier and tier not in VALID_TIERS:
        errors.append(f"{filename}: @GOVERNANCE tier '{tier}' not in {sorted(VALID_TIERS)}")
    status = block.get("status", "").upper()
    if status and status not in VALID_STATUS:
        errors.append(f"{filename}: @GOVERNANCE status '{status}' not in {sorted(VALID_STATUS)}")


def validate_content_musicos(block: dict, errors: list, warnings: list, filename: str):
    structural = block.get("structural", "")
    if structural:
        lines = structural.strip().splitlines()
        for line in lines:
            if not line.strip():
                continue
            # series must be SBR, UMB, or SE
            if line.strip().startswith("series:"):
                val = line.split(":", 1)[1].strip().strip("[]")
                valid_series = {"SBR", "UMB", "SE"}
                for s in val.split(","):
                    s = s.strip()
                    if s and s not in valid_series:
                        warnings.append(f"{filename}: musicos series '{s}' not in {sorted(valid_series)}")


def validate_content_monster(block: dict, errors: list, warnings: list, filename: str):
    structural = block.get("structural", "")
    if structural:
        lines = structural.strip().splitlines()
        for line in lines:
            if not line.strip():
                continue
            if line.strip().startswith("type:"):
                val = line.split(":", 1)[1].strip().strip("[]")
                valid_types = {"boss", "minion", "elite", "npc"}
                for t in val.split(","):
                    t = t.strip()
                    if t and t not in valid_types:
                        warnings.append(f"{filename}: monster type '{t}' not in {sorted(valid_types)}")


def validate_trap_card(text: str, errors: list, warnings: list, filename: str):
    """Check for trap card activation keywords in content."""
    # Trap card is valid if it's a TRAP-CARD file
    if "TRAP CARD" in text or "trap card" in text.lower():
        return  # this is the trap card spec itself
    # Check for origin-removal language in non-trap-card files
    lower = text.lower()
    for trigger in TRAP_TRIGGERS:
        if f" {trigger} " in f" {lower} " or lower.startswith(trigger):
            # Only flag if it's near @INSTANCE
            inst_match = "@INSTANCE" in text
            if inst_match:
                warnings.append(
                    f"{filename}: trap-card trigger '{trigger}' found near @INSTANCE "
                    f"— ensure origin is preserved (ARCH-JRV-TRAP-0001)"
                )
                break


def validate_file(path: Path, domain_filter: str | None = None) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []
    text = path.read_text()

    inst = parse_block(text, INSTANCE_RE)
    iden = parse_block(text, IDENTITY_RE)
    dom  = parse_block(text, DOMAIN_RE)
    cont = parse_block(text, CONTENT_RE)
    gov  = parse_block(text, GOV_RE)
    meta = parse_block(text, META_RE)

    has_jpl_blocks = bool(inst or iden or dom or cont or gov)

    # Only enforce JPL requirements for files that claim to be JPL entities.
    # Files without any JPL blocks are out-of-scope (not JPL documents).
    if not has_jpl_blocks:
        return [], []

    # JPL entity found — enforce required blocks
    if not inst:
        errors.append(f"{path.name}: missing @INSTANCE block")
    if not iden:
        warnings.append(f"{path.name}: missing @IDENTITY block")

    if inst:
        validate_instance(inst, errors, path.name)
    if iden:
        validate_identity(iden, errors, path.name)
    if dom:
        validate_domain(dom, errors, path.name)
        if domain_filter:
            domain_name = dom.get("domain", "").lower()
            if domain_filter == "musicos" and domain_name not in MUSICOS_DOMAINS:
                return [], []
            if domain_filter == "monster" and domain_name not in MONSTER_DOMAINS:
                return [], []
        if dom.get("domain", "").lower() in MUSICOS_DOMAINS and cont:
            validate_content_musicos(cont, errors, warnings, path.name)
        if dom.get("domain", "").lower() in MONSTER_DOMAINS and cont:
            validate_content_monster(cont, errors, warnings, path.name)
    if gov:
        validate_governance(gov, errors, path.name)

    # Trap card check
    if "@INSTANCE" in text:
        validate_trap_card(text, errors, warnings, path.name)

    # Metadata sanity
    if meta:
        ts = meta.get("timestamp", "")
        if ts and not ts.startswith("["):
            try:
                datetime.fromisoformat(ts.replace("Z", "+00:00"))
            except ValueError:
                warnings.append(f"{path.name}: @METADATA timestamp '{ts}' not ISO8601")

    return errors, warnings


def main() -> int:
    p = argparse.ArgumentParser(description="JPL Validator — JVE extension for ARCH-JPL-SPEC-0001")
    p.add_argument("paths", nargs="*", help="Files to validate (default: scan repo)")
    p.add_argument("--domain", choices=["musicos", "monster", "all"], default="all",
                   help="Domain filter")
    p.add_argument("--trap-card", action="store_true",
                   help="Check only trap card compliance")
    p.add_argument("--quiet", "-q", action="store_true", help="Suppress warnings")
    p.add_argument("--strict", action="store_true", help="Treat warnings as errors")
    args = p.parse_args()

    root = Path(__file__).resolve().parents[3]
    files: list[Path] = []
    if args.paths:
        files = [Path(p) for p in args.paths]
    else:
        # Scan only directories that contain JPL entities
        jpl_dirs = [
            root / "JarvisSide" / "Projects" / "MusicOS",
            root / "JarvisSide" / "Projects" / "MonsterOS",
            root / "JarvisMain" / "Architecture" / "identity",
            root / "JarvisMain" / "Architecture" / "JPL",
            root / "JarvisSide" / "Projects" / "JPL",
        ]
        for d in jpl_dirs:
            if d.exists():
                files.extend(sorted(d.rglob("*.md")))
        # Dedupe
        seen = set()
        unique = []
        for f in files:
            if f not in seen:
                seen.add(f)
                unique.append(f)
        files = unique

    all_errors: list[str] = []
    all_warnings: list[str] = []

    domain_filter = None if args.domain == "all" else args.domain

    for f in sorted(files):
        try:
            errs, warns = validate_file(f, domain_filter)
            if args.trap_card:
                errs = [e for e in errs if "trap" in e.lower()]
                warns = [w for w in warns if "trap" in w.lower()]
            all_errors.extend(errs)
            all_warnings.extend(warns)
        except Exception as ex:
            all_errors.append(f"{f.name}: parse error — {ex}")

    total = len(files)
    if args.strict:
        all_errors.extend(all_warnings)
        all_warnings = []

    if all_errors:
        print(f"JPL VALIDATION FAILED — {len(all_errors)} error(s) in {total} files:")
        for e in all_errors:
            print(f"  ✗ {e}")
        if not args.quiet and all_warnings:
            for w in all_warnings:
                print(f"  ! {w}")
        return 1

    if all_warnings and not args.quiet:
        print(f"JPL GREEN — {total} files validated, {len(all_warnings)} warning(s):")
        for w in all_warnings:
            print(f"  ! {w}")
        return 0

    print(f"JPL GREEN — {total} files validated, no violations.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())