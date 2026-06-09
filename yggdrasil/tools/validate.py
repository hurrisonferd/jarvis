"""Validate the Yggdrasil substrate against the JNL grammar, GL12, and JMS mirror law.

Run from repo root:  python yggdrasil/tools/validate.py
Exit 0 = green; exit 1 = violations found.
"""
from __future__ import annotations
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import jnl as jnllib  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
JD_DIR = ROOT / "yggdrasil" / "jd" / "entries"
LAL_DIR = ROOT / "yggdrasil" / "lal"

FM_RE = re.compile(r"^---\n(.*?)\n---", re.DOTALL)


def parse_front_matter(text: str) -> dict:
    m = FM_RE.match(text)
    if not m:
        return {}
    out = {}
    for line in m.group(1).splitlines():
        if ":" not in line:
            continue
        k, v = line.split(":", 1)
        v = v.strip()
        if v.startswith("[") and v.endswith("]"):
            v = [x.strip() for x in v[1:-1].split(",") if x.strip()]
        out[k.strip()] = v
    return out


def main() -> int:
    errors: list[str] = []
    warnings: list[str] = []
    seen: dict[str, Path] = {}

    entries = sorted(JD_DIR.glob("*.md"))
    if not entries:
        print("FAIL: no JD entries found — run tools/seed.py first")
        return 1

    entry_jnls: set[str] = set()
    for f in entries:
        fm = parse_front_matter(f.read_text())
        addr = fm.get("jnl", "")
        # GL12: every entry needs jnl, status, tags, ref (index ref), and resolvable location.
        for req in ("name", "type", "jnl", "status", "created", "updated", "tags", "ref"):
            if not fm.get(req):
                errors.append(f"{f.name}: missing GL12 field '{req}'")
        st = fm.get("status", "")
        if st and st not in jnllib.STATUSES:
            errors.append(f"{f.name}: status '{st}' not in JSS vocabulary {sorted(jnllib.STATUSES)}")
        if not addr:
            continue
        # Filename must equal the JNL (JNS determinism).
        if f.stem != addr:
            errors.append(f"{f.name}: filename != jnl '{addr}' (JNS rule)")
        # Grammar.
        try:
            jnllib.parse(addr)
        except ValueError as e:
            errors.append(f"{f.name}: {e}")
        # Uniqueness.
        if addr in seen:
            errors.append(f"{addr}: duplicate (also {seen[addr].name})")
        seen[addr] = f
        entry_jnls.add(addr)
        # Related must be valid grammar too.
        for rel in fm.get("related", []) or []:
            if not jnllib.is_valid(rel):
                errors.append(f"{f.name}: related '{rel}' is not a valid JNL")

    # LAL mirror consistency (JMS law): every address points to real truth; every entry indexed.
    reg_path = LAL_DIR / "address-registry.json"
    if not reg_path.exists():
        errors.append("lal/address-registry.json missing — run tools/seed.py")
    else:
        reg = json.loads(reg_path.read_text())
        reg_jnls = set()
        for rec in reg.get("records", []):
            a = rec.get("jnl", "")
            reg_jnls.add(a)
            if not jnllib.is_valid(a):
                errors.append(f"address-registry: invalid JNL '{a}'")
            loc = ROOT / rec.get("location", "")
            if not loc.exists():
                errors.append(f"address-registry: '{a}' location does not exist: {rec.get('location')}")
        missing = entry_jnls - reg_jnls
        for a in sorted(missing):
            errors.append(f"{a}: JD entry not indexed in LAL (GL12 IndexSummary ref)")

    total = len(entry_jnls)
    if errors:
        print(f"VALIDATION FAILED — {len(errors)} error(s) across {total} addresses:")
        for e in errors:
            print(f"  ✗ {e}")
        for w in warnings:
            print(f"  ! {w}")
        return 1
    print(f"GREEN — {total} governed objects: grammar OK, GL12 satisfied, LAL mirror consistent.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
