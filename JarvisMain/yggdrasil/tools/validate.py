"""Validate the Yggdrasil substrate against the JNL grammar, GL12, and JMS mirror law.

Run from repo root:  python JarvisMain/yggdrasil/tools/validate.py
Exit 0 = green; exit 1 = violations found.
"""
from __future__ import annotations
import json
import subprocess
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import jnl as jnllib  # noqa: E402

ROOT = Path(__file__).resolve().parents[3]
JD_DIR = ROOT / "JarvisMain" / "yggdrasil" / "jd" / "entries"
LAL_DIR = ROOT / "JarvisMain" / "yggdrasil" / "lal"

FM_RE = re.compile(r"^---\n(.*?)\n---", re.DOTALL)

# JSE — Jarvis Schema Envelope (ARCH-JSE-SPEC-0001): the canonical frontmatter every JD entry
# carries. GL12 requires 10 of these; JSE requires ALL 19 keys PRESENT — empty is fine (roots have
# no parent/steward; [] lists), a MISSING key is the defect (the steward:null-class gap JSE kills).
JSE_ENVELOPE = ("name", "type", "class", "tier", "authority", "owner", "steward", "parent",
                "jnl", "seq", "status", "created", "updated", "source", "related", "references",
                "tags", "aliases", "ref", "memory_tier")

# JMMS — Jarvis Memory Model Schema: path → (tier, grade) mapping for grade validation.
# The tier/grade declared in frontmatter should match what the path implies.
TIER_GRADE_PATHS = {
    "JarvisMain/Architecture/canon/":     ("JATM", "system"),
    "JarvisMain/Architecture/specs/":     ("JLTM", "system"),
    "JarvisMain/Connectors/":            ("JLTM", "system"),
    "JarvisMain/god_systems/":           ("JLTM", "system"),
    "JarvisMain/yggdrasil/":            ("JLTM", "system"),
    "JarvisSide/Projects/":             ("JLTM", "system"),
    "JarvisSide/Ideas/":               ("JSTM", "system"),
    "JarvisSide/Archive/":             ("JHTM", "system"),
    "audit/starlogs/":               ("JHTM", "system"),
    "mnemos/knowledge/":           ("JLTM", "system"),
    "JarvisMain/Manual/":          ("JLTM", "system"),
    "JarvisMain/Implementation/Active/": ("JSTM", "system"),
    "JarvisMain/Patches/":         ("JSTM", "system"),
}


def validate_memory_frontmatter(path: str, frontmatter: dict) -> list[str]:
    """Check that memory_tier and grade in frontmatter match path-derived expectations.

    Returns a list of warning messages (empty list if all is well).
    Special cases:
      - 'canon/' in path   → expect JATM tier
      - 'starlogs/' in path → expect JHTM tier
      - 'Archive/' in path  → expect JHTM tier
    """
    warnings = []
    rel_path = str(path)

    # Extract declared values (case-insensitive keys)
    declared_tier = None
    declared_grade = None
    for k, v in frontmatter.items():
        kl = k.lower()
        if kl == "memory_tier":
            declared_tier = v.strip() if isinstance(v, str) else str(v)
        elif kl == "grade":
            declared_grade = v.strip() if isinstance(v, str) else str(v)

    # Determine expected tier+grade from path
    expected_tier = None
    expected_grade = None

    # Special cases first (most specific)
    if "canon/" in rel_path:
        expected_tier = "JATM"
    elif "starlogs/" in rel_path or "Archive/" in rel_path:
        expected_tier = "JHTM"

    # Fall back to TIER_GRADE_PATHS prefix matching
    if expected_tier is None:
        for prefix, (tier, grade) in TIER_GRADE_PATHS.items():
            if rel_path.startswith(prefix):
                expected_tier = tier
                expected_grade = grade
                break

    # Compare declared vs expected
    if expected_tier and declared_tier and declared_tier != expected_tier:
        warnings.append(
            f"memory_tier '{declared_tier}' != path-derived tier '{expected_tier}' "
            f"(path suggests this should be {expected_tier})"
        )
    if expected_grade and declared_grade and declared_grade != expected_grade:
        warnings.append(
            f"grade '{declared_grade}' != path-derived grade '{expected_grade}' "
            f"(path suggests this should be {expected_grade})"
        )

    return warnings


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
        # JMMS: validate tier+grade match path-derived expectations.
        rel_path = f.relative_to(ROOT).as_posix()
        warnings.extend(validate_memory_frontmatter(rel_path, fm))
        # GL12: every entry needs jnl, status, class, tier, tags, ref, and resolvable location.
        for req in ("name", "type", "class", "tier", "jnl", "status", "created", "updated", "tags", "ref"):
            if not fm.get(req):
                errors.append(f"{f.name}: missing GL12 field '{req}'")
        # JSE completeness (ARCH-JSE-SPEC-0001): every entry carries the FULL envelope. A missing
        # KEY is a defect even when a present value is legitimately empty — visibility over silence.
        for key in JSE_ENVELOPE:
            if key not in fm:
                errors.append(f"{f.name}: JSE envelope missing key '{key}' (entries must carry all {len(JSE_ENVELOPE)} fields)")
        st, cls, tr = fm.get("status", ""), fm.get("class", ""), fm.get("tier", "")
        if st and st not in jnllib.STATUSES:
            errors.append(f"{f.name}: status '{st}' not in JSS vocabulary {sorted(jnllib.STATUSES)}")
        if cls and cls not in jnllib.CLASSES:
            errors.append(f"{f.name}: class '{cls}' not in ontology {sorted(jnllib.CLASSES)}")
        if tr and tr not in jnllib.TIERS:
            errors.append(f"{f.name}: tier '{tr}' not in {sorted(jnllib.TIERS)}")
        # type IS the JNL type token (Raven-approved 2026-06-11) — drift is a failure.
        typ = fm.get("type", "")
        if addr and typ and "-" in addr and typ != addr.split("-")[2]:
            errors.append(f"{f.name}: type '{typ}' != JNL token '{addr.split('-')[2]}' (type = address ontology)")
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

    # ── Semantic content audit (Copilot #3 / JARVIS-C audit 2026-06-25) ───────
    # GL12 validates the envelope. This validates the body: an agent could fill all 19
    # fields correctly (envelope passes) while subtly redefining governance in the body.
    # Classes that carry law, architecture, or system definitions are the critical surface.
    SENSITIVE_CLASSES = {
        "SPEC": {
            "immutable_fields": ["class", "tier", "authority"],
            "forbidden_patterns": [
                r"redefin(e|es|ing|ition)\s+(gl\d|gold\s+law|gold\s+law|goldlaw)",
                r"(remove|delete|drop)\s+gl\d",
                r"bypass\s+(aegis|a\.e\.g\.i\.s)",
                r"(revoke|rescind)\s+(raven|raven'?s)\s+(authority|approval|authorization)",
                r"overrid(e|ing|es)\s+(gl\d|aegis|governance)",
                r"(disable|deactivat(e|es|ing))\s+(aegis|skadi)",
                r"self[\-\s]mod(if|ify|ification)",
                r"unauthorized\s+(write|execute|modify)",
            ],
        },
        "SYSTEM": {
            "immutable_fields": ["jnl", "class"],
            "forbidden_patterns": [
                r"forbidden\s+edge\s*\(",
                r"(circumvent|bypass)\s+(edge|forbidden)",
                r"(add|insert)\s+(forbidden|skadi.*aegis|dante.*skadi)",
                r"self[\-\s]mod(if|ify|ification)",
            ],
        },
        "ARCH": {
            "immutable_fields": ["class", "tier", "authority"],
            "forbidden_patterns": [
                r"(remove|disable)\s+branch\s+protection",
                r"(allow|enable)\s+direct\s+push\s+to\s+main",
                r"(bypass|skip)\s+(ci|pull\s+request|pr)",
                r"unauthorized\s+git\s+(push|commit|merge)",
            ],
        },
        "GOD": {
            "immutable_fields": ["jnl", "class"],
            "forbidden_patterns": [
                r"add\s+(god\s+system|new\s+system)\s+without\s+(raven|gl7)",
                r"redesign\s+(forbidden|edge)",
                r"(delete|remove|deprecate)\s+(aegis|odin|skadi|mnem)",
            ],
        },
    }
    for f in entries:
        text = f.read_text()
        fm = parse_front_matter(text)
        body = FM_RE.split(text, 2)[-1]  # everything after the closing ---
        cls = fm.get("class", "")
        if cls not in SENSITIVE_CLASSES:
            continue
        rules = SENSITIVE_CLASSES[cls]
        for pat in rules["forbidden_patterns"]:
            hits = re.findall(pat, body, re.IGNORECASE)
            if hits:
                matched = [h for h in hits if h]  # filter empty
                if matched:
                    errors.append(
                        f"{f.name}: body contains forbidden pattern '{pat[:40]}...' "
                        f"(class={cls}, semantic drift — requires Raven sign-off)"
                    )
    # ── end semantic content audit ─────────────────────────────────────────────

    # JMMS: validate memory_tier+grade for all .md files (not just JD entries).
    for base in ("JarvisMain", "JarvisSide", "mnemos", "audit"):
        base_path = ROOT / base
        if not base_path.exists():
            continue
        for f in sorted(base_path.rglob("*.md")):
            if f.is_dir():
                continue
            if "yggdrasil" in f.parts:  # already validated in the JD loop above
                continue
            try:
                text = f.read_text()
            except Exception:
                continue
            fm = parse_front_matter(text)
            if not fm:
                continue  # no frontmatter, nothing to validate
            rel_path = f.relative_to(ROOT).as_posix()
            warnings.extend(validate_memory_frontmatter(rel_path, fm))

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

    # Class immutability (Raven-verdicted 2026-06-11): an existing JNL's class never
    # changes in place — identity evolves by mint-successor + deprecate, never overwrite.
    try:
        head = subprocess.run(
            ["git", "show", "HEAD:JarvisMain/yggdrasil/lal/address-registry.json"],
            capture_output=True, text=True, cwd=ROOT, check=True).stdout
        head_class = {r.get("jnl"): r.get("class") for r in json.loads(head).get("records", [])}
        for rec in records:
            a, c = rec.get("jnl"), rec.get("class")
            if a in head_class and head_class[a] and c != head_class[a]:
                errors.append(
                    f"{a}: class '{c}' != committed class '{head_class[a]}' "
                    "(class immutability — mint a successor + deprecate, never reclassify)")
    except Exception:
        pass  # no committed snapshot to compare (fresh repo)

    # Family tree (parent): every parent resolves to a real entry; no cycles.
    parents: dict[str, str] = {}
    for f in entries:
        fm = parse_front_matter(f.read_text())
        a, par = fm.get("jnl", ""), fm.get("parent", "")
        if not a or not par or not isinstance(par, str):
            continue
        parents[a] = par
        if not jnllib.is_valid(par):
            errors.append(f"{a}: parent '{par}' is not a valid JNL")
        elif par not in entry_jnls:
            errors.append(f"{a}: parent '{par}' has no JD entry (orphaned family)")
    for start in parents:
        node, hops = start, 0
        while node in parents and hops <= len(parents):
            node, hops = parents[node], hops + 1
        if hops > len(parents):
            errors.append(f"{start}: parent chain forms a cycle")
            break

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
    # location, inside a registered folder-location, inside a registered project node,
    # or in the Connectors class (governed as a system, not by per-entry location).
    locations = {r.get("location", "") for r in records}
    governed_dirs = {l for l in locations if (ROOT / l).is_dir()}
    codes_path = ROOT / "JarvisMain" / "yggdrasil" / "jfs" / "project-codes.json"
    if codes_path.exists():
        governed_dirs |= {i["folder"] for i in json.loads(codes_path.read_text())["codes"].values()}
    # Connector doc mirrors are governed as a class: CONN entries exist but per-entry location
    # is not practical (65 files). The CONNECTORS umbrella is the governed address.
    governed_dirs.add("JarvisMain/Connectors")
    governed_dirs.add("JarvisMain/Implementation")  # JIP series + logs + scripts
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

    # Map-matches-ground (Ayre's law, Raven-directed 2026-06-14): the wiring map's tool→god
    # routing must reference only tools the connector actually exposes. A map that names a dead
    # tool is a confident lie about the territory — caught here, ruthlessly.
    # TOOL_NAMES moved to core/env.ts (jarvis-mcp forge slice 1); read it there.
    conn_path = ROOT / "supabase" / "functions" / "jarvis-mcp" / "core" / "env.ts"
    wmap_path = ROOT / "JarvisMain" / "yggdrasil" / "tools" / "wiring_map.py"
    if conn_path.exists() and wmap_path.exists():
        conn = conn_path.read_text()
        m = re.search(r"const TOOL_NAMES = \[(.*?)\]", conn, re.DOTALL)
        conn_tools = set(re.findall(r'"(jarvis_[a-z_]+)"', m.group(1))) if m else set()
        map_tools = set(re.findall(r'"(jarvis_[a-z_]+)"', wmap_path.read_text()))
        dead = sorted(map_tools - conn_tools)
        if dead:
            errors.append(f"wiring-map references tools not in the connector (map drift): {dead}")

    # Creation serials (seq): present, integer, unique, and immutable against the
    # committed seq-registry. The serial is a birth certificate, never an address —
    # renumbering history is corruption (GL5).
    seq_file = ROOT / "JarvisMain" / "yggdrasil" / "lal" / "seq-registry.json"
    if not seq_file.exists():
        errors.append("lal/seq-registry.json missing — run tools/seed.py")
    else:
        seq_reg = json.loads(seq_file.read_text())
        seen_seq: dict[int, str] = {}
        for f in sorted(JD_DIR.glob("*.md")):
            fm = parse_front_matter(f.read_text())
            raw = fm.get("seq")
            if raw is None or not str(raw).isdigit():
                errors.append(f"{f.name}: missing/invalid seq (creation serial)")
                continue
            n = int(str(raw))
            if n in seen_seq:
                errors.append(f"{f.name}: seq {n} duplicates {seen_seq[n]} (serials are never reused)")
            seen_seq[n] = f.name
            reg_n = seq_reg.get("map", {}).get(f.stem)
            if reg_n != n:
                errors.append(f"{f.name}: seq {n} != seq-registry {reg_n} (serials are immutable)")
        if seen_seq and seq_reg.get("next", 0) <= max(seen_seq):
            errors.append(f"seq-registry: next={seq_reg.get('next')} not above max minted {max(seen_seq)}")

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
