"""Validate the Yggdrasil substrate against the JNL grammar, GL12, and JMS mirror law.

Run from repo root:  python JarvisMain/yggdrasil/tools/validate.py
Exit 0 = green; exit 1 = violations found.
"""
from __future__ import annotations
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import jnl as jnllib  # noqa: E402

ROOT = Path(__file__).resolve().parents[3]
JD_DIR = ROOT / "JarvisMain" / "yggdrasil" / "jd" / "entries"
LAL_DIR = ROOT / "JarvisMain" / "yggdrasil" / "lal"

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
    related_edges: list[tuple[str, str]] = []

    entries = sorted(JD_DIR.glob("*.md"))
    if not entries:
        print("FAIL: no JD entries found — run tools/seed.py first")
        return 1

    entry_jnls: set[str] = set()
    name_index: dict[str, str] = {}
    for f in entries:
        fm = parse_front_matter(f.read_text())
        addr = fm.get("jnl", "")
        # GL12: every entry needs jnl, status, class, tier, tags, ref, and resolvable location.
        for req in ("name", "type", "class", "tier", "jnl", "status", "created", "updated", "tags", "ref"):
            if not fm.get(req):
                errors.append(f"{f.name}: missing GL12 field '{req}'")
        st, cls, tr = fm.get("status", ""), fm.get("class", ""), fm.get("tier", "")
        if st and st not in jnllib.STATUSES:
            errors.append(f"{f.name}: status '{st}' not in JSS vocabulary {sorted(jnllib.STATUSES)}")
        if cls and cls not in jnllib.CLASSES:
            errors.append(f"{f.name}: class '{cls}' not in ontology {sorted(jnllib.CLASSES)}")
        if tr and tr not in jnllib.TIERS:
            errors.append(f"{f.name}: tier '{tr}' not in {sorted(jnllib.TIERS)}")
        # Redundancy (overlap_score Gold Law): two entries may not claim the same canonical name.
        nm = fm.get("name", "")
        if nm:
            if nm in name_index and name_index[nm] != addr:
                warnings.append(f"redundant name '{nm}': {addr} duplicates {name_index[nm]}")
            name_index[nm] = addr
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
        # Related must be valid grammar too; targets checked for existence after the scan.
        for rel in fm.get("related", []) or []:
            if not jnllib.is_valid(rel):
                errors.append(f"{f.name}: related '{rel}' is not a valid JNL")
            else:
                related_edges.append((addr, rel))
        # JSS discipline: JGPP is exploration — it should be TASK, or promoted to a JIP.
        if addr.split("-")[2] == "JGPP" and st == "ACTIVE":
            warnings.append(f"{addr}: JGPP with status ACTIVE — exploration should be TASK or promoted (JSS)")

    # LAL mirror consistency (JMS law): every address points to real truth; every entry indexed.
    reg_path = LAL_DIR / "address-registry.json"
    records: list[dict] = []
    if not reg_path.exists():
        errors.append("lal/address-registry.json missing — run tools/seed.py")
    else:
        reg = json.loads(reg_path.read_text())
        records = reg.get("records", [])
        reg_jnls = set()
        for rec in records:
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

    # The dex web must not dangle: every related edge resolves to a real entry.
    for src, tgt in related_edges:
        if tgt not in entry_jnls:
            errors.append(f"{src}: related '{tgt}' has no JD entry (dangling edge)")

    # JNS lock (FMT spec §3): project artifacts must carry the canonical filename grammar
    # <PROJECT><TYPE>-<MMDDYY>-<NNNN>-<SUBJECT>.md, with NNNN == the JNL Log segment.
    jns_proj = re.compile(r"^[A-Z0-9]+(JGPP|JIP|JD|BIO)-\d{6}-(\d{4})-[A-Z0-9][A-Z0-9-]*\.md$")
    for rec in records:
        loc = rec.get("location", "")
        if not re.match(r"JarvisSide/Projects/[^/]+/(JGPP|JIP|JD|BIO)/[^/]+\.md$", loc):
            continue
        m = jns_proj.match(Path(loc).name)
        if not m:
            errors.append(f"{rec['jnl']}: filename '{Path(loc).name}' violates JNS project grammar (FMT §3)")
        elif m.group(2) != rec["jnl"].split("-")[3]:
            errors.append(f"{rec['jnl']}: filename sequence {m.group(2)} != JNL Log segment (JNS/JNL must agree)")

    # GL12 closure: every file under the umbrellas must be governed — either a registered
    # location, inside a registered folder-location, or inside a registered project node.
    locations = {r.get("location", "") for r in records}
    governed_dirs = {l for l in locations if (ROOT / l).is_dir()}
    codes_path = ROOT / "JarvisMain" / "yggdrasil" / "jfs" / "project-codes.json"
    if codes_path.exists():
        governed_dirs |= {i["folder"] for i in json.loads(codes_path.read_text())["codes"].values()}
    for base in ("JarvisMain", "JarvisSide"):
        for f in sorted((ROOT / base).rglob("*")):
            if f.is_dir() or f.name == ".gitkeep":
                continue
            rel = f.relative_to(ROOT).as_posix()
            if rel.startswith("JarvisMain/yggdrasil/"):
                continue  # the substrate kernel governs itself (entries/registries/tools)
            if rel in locations or any(rel.startswith(d + "/") for d in governed_dirs):
                continue
            errors.append(f"{rel}: ungoverned — no JNL covers it (GL12)")

    # Grammar lockstep (YGG manifest law): jarvis-dex/jfs.ts mirrors jnl.py by hand.
    # If the token tables drift, the connector accepts addresses the validator rejects.
    ts_path = ROOT / "supabase" / "functions" / "jarvis-dex" / "jfs.ts"
    if ts_path.exists():
        ts = ts_path.read_text()
        ts_sets = {m.group(1): set(re.findall(r'"([^"]+)"', m.group(2)))
                   for m in re.finditer(r"export const (\w+) = new Set\(\[(.*?)\]\)", ts, re.DOTALL)}
        for name, py in (("DOMAINS", jnllib.DOMAINS), ("TYPES", jnllib.TYPES),
                         ("SUBSTRATE", jnllib.SUBSTRATE), ("GOD_SYSTEMS", jnllib.GOD_SYSTEMS),
                         ("STATUSES", jnllib.STATUSES), ("CLASSES", jnllib.CLASSES),
                         ("TIERS", jnllib.TIERS)):
            tsv = ts_sets.get(name)
            if tsv is None:
                errors.append(f"jfs.ts: token table {name} not found (grammar mirror broken)")
            elif tsv != py:
                drift = sorted((tsv - py) | (py - tsv))
                errors.append(f"grammar drift {name}: jnl.py and jfs.ts disagree on {drift}")

    total = len(entry_jnls)
    if errors:
        print(f"VALIDATION FAILED — {len(errors)} error(s) across {total} addresses:")
        for e in errors:
            print(f"  ✗ {e}")
        for w in warnings:
            print(f"  ! {w}")
        return 1
    for w in warnings:
        print(f"  ! {w}")
    print(f"GREEN — {total} governed objects: grammar OK, GL12 satisfied, LAL mirror consistent.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
