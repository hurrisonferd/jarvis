#!/usr/bin/env python3
"""Build the public JD v2 semantic catalog and discovery queue."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
import unicodedata
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

SCRIPT = Path(__file__).resolve()
JD_ROOT = SCRIPT.parents[1]
YGG_ROOT = JD_ROOT.parent
REPO_ROOT = YGG_ROOT.parents[2]
ENTRIES_ROOT = JD_ROOT / "entries"
CATALOG_ROOT = JD_ROOT / "catalog"
CATEGORY_REGISTRY = CATALOG_ROOT / "CATEGORY-REGISTRY.json"

JSE_REQUIRED = (
    "name", "type", "class", "tier", "authority", "owner", "steward", "parent",
    "jnl", "seq", "status", "created", "updated", "source", "related", "references",
    "tags", "aliases", "ref", "memory_tier",
)

DISCOVERY_ROOTS = (
    REPO_ROOT / "core" / "JarvisMain",
    REPO_ROOT / "runtime",
    REPO_ROOT / "docs",
    REPO_ROOT / "templates",
    REPO_ROOT / "Jorm" / "Vault" / "Canon",
)

SKIP_PARTS = {
    ".git", "node_modules", "dist", "build", "coverage", "__pycache__", "Inbox",
    "raw-chat-exports", "Corpus_Ingestion", "Recovery_Ledgers", "archive", "archives",
    "vendor",
}

SEMANTIC_SIGNAL = re.compile(
    r"(?:\bOS\b|AI|engine|system|protocol|kernel|codex|grid|atom|lilith|ayre|jarvis|jorm|"
    r"primus|unicron|neuromax|music|image|game|ego|pride|prosody|council|memory|benchmark|"
    r"identity|continuity|router|registry|dictionary|law|audit|simulator|runtime|companion)",
    re.IGNORECASE,
)

GENERIC = {"readme", "index", "setup", "notes", "overview", "configuration", "examples", "changelog", "license", "contributing", "package"}


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def normalize(value: str) -> str:
    value = unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode("ascii")
    return re.sub(r"[^a-z0-9]+", " ", value.lower()).strip()


def slugify(value: str) -> str:
    return normalize(value).replace(" ", "-") or "unnamed"


def parse_scalar(value: str) -> Any:
    value = value.strip()
    if not value:
        return ""
    if value.startswith("[") and value.endswith("]"):
        inner = value[1:-1].strip()
        return [parse_scalar(item) for item in inner.split(",") if item.strip()]
    lowered = value.lower()
    if lowered in {"null", "none", "~"}:
        return None
    if lowered == "true":
        return True
    if lowered == "false":
        return False
    if re.fullmatch(r"-?\d+", value):
        return int(value)
    return value.strip("'\"")


def frontmatter(text: str) -> dict[str, Any]:
    lines = text.splitlines()
    marks = [i for i, line in enumerate(lines) if line.strip() == "---"]
    if len(marks) < 2:
        return {}
    result: dict[str, Any] = {}
    for raw in lines[marks[0] + 1 : marks[1]]:
        line = raw.strip()
        if not line or line.startswith("#") or ":" not in line:
            continue
        key, value = line.split(":", 1)
        key = key.strip()
        if re.fullmatch(r"[A-Za-z0-9_-]+", key):
            result[key] = parse_scalar(value)
    return result


def as_list(value: Any) -> list[str]:
    if value is None:
        return []
    values = value if isinstance(value, list) else [value]
    result: list[str] = []
    for item in values:
        text = str(item).strip().strip("'\"")
        if text and text not in result:
            result.append(text)
    return result


def compact(value: str, limit: int = 900) -> str:
    value = re.sub(r"\s+", " ", value).strip()
    return value if len(value) <= limit else value[: limit - 1].rstrip() + "…"


def extract(text: str, label: str) -> str:
    pattern = re.compile(rf"\*\*{re.escape(label)}:\*\*\s*(.+)", re.IGNORECASE)
    for line in text.splitlines():
        match = pattern.search(line)
        if match:
            return compact(match.group(1))
    return ""


def classify(meta: dict[str, Any], name: str, definition: str, path: str) -> tuple[str, str, float, list[str]]:
    jnl = str(meta.get("jnl") or "")
    domain = jnl.split("-", 1)[0].upper() if jnl else ""
    tags = {normalize(tag).replace(" ", "_") for tag in as_list(meta.get("tags"))}
    haystack = " ".join([name, definition, path, jnl, " ".join(tags)]).lower()
    if domain == "GS": return "GOD_SYSTEM", "SUPPORT", 0.98, ["JNL domain GS"]
    if domain == "CONN": return "CONNECTOR", "API", 0.98, ["JNL domain CONN"]
    if domain == "PROJ": return "PROJECT", "PRODUCT", 0.98, ["JNL domain PROJ"]
    if domain == "AUD": return "GOVERNANCE", "AUDIT", 0.96, ["JNL domain AUD"]
    if domain == "LOG": return "EVENT", "SESSION", 0.94, ["JNL domain LOG"]
    if domain == "GOV":
        if "law" in haystack: return "LAW", "ARCHITECTURE_LAW", 0.92, ["GOV domain", "law signal"]
        if "protocol" in haystack: return "PROTOCOL", "AUDIT", 0.92, ["GOV domain", "protocol signal"]
        return "GOVERNANCE", "CONTRACT", 0.90, ["JNL domain GOV"]
    if domain == "EGO" or "/ego/" in path.lower(): return "ISO", "SPECIALIST", 0.95, ["EGO route/domain"]
    if name.lower().endswith("os") or re.search(r"(?:^|[^a-z])[a-z]+os(?:$|[^a-z])", haystack): return "OS", "DOMAIN_OS", 0.90, ["OS naming signal"]
    if "companion" in haystack or "personality" in haystack or "identity" in tags: return "AI_SYSTEM", "COMPANION", 0.82, ["identity/companion signal"]
    if "memory" in haystack or domain in {"MEM", "JMMS"}: return "MEMORY", "LONG_TERM", 0.82, ["memory signal"]
    if "registry" in haystack or "dictionary" in haystack or "index" in haystack: return "REGISTRY", "CATALOG", 0.80, ["registry signal"]
    if "protocol" in haystack: return "PROTOCOL", "SYNC", 0.78, ["protocol signal"]
    if "law" in haystack: return "LAW", "ARCHITECTURE_LAW", 0.78, ["law signal"]
    if "engine" in haystack or "kernel" in haystack or str(meta.get("class", "")).upper() == "SYSTEM": return "ENGINE", "KERNEL", 0.72, ["engine/kernel/system signal"]
    if str(meta.get("class", "")).upper() == "MODULE" or str(meta.get("type", "")).upper() == "MODULE": return "MODULE", "RUNTIME", 0.74, ["module schema signal"]
    if domain == "ARCH": return "CONCEPT", "ARCHITECTURE", 0.65, ["JNL domain ARCH"]
    return "UNKNOWN", "UNRESOLVED", 0.25, ["no strong classifier rule"]


def edges(meta: dict[str, Any], path: str) -> list[dict[str, Any]]:
    result: list[dict[str, Any]] = []
    def add(kind: str, target: Any, field: str) -> None:
        value = str(target or "").strip()
        if value:
            result.append({"type": kind, "target": value, "provenance": f"{path}#frontmatter.{field}", "confidence": 1.0, "curation_status": "EXTRACTED"})
    add("CHILD_OF", meta.get("parent"), "parent")
    add("OWNED_BY", meta.get("owner"), "owner")
    add("STEWARDED_BY", meta.get("steward"), "steward")
    for target in as_list(meta.get("related")): add("RELATES_TO", target, "related")
    for target in as_list(meta.get("references")): add("REFERENCES", target, "references")
    return result


def load_records() -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    records: list[dict[str, Any]] = []
    source_meta: list[dict[str, Any]] = []
    for path in sorted(ENTRIES_ROOT.glob("*.md")):
        raw = path.read_bytes()
        text = raw.decode("utf-8", errors="replace")
        meta = frontmatter(text)
        name = str(meta.get("name") or path.stem).strip()
        jnl = str(meta.get("jnl") or path.stem).strip()
        definition = extract(text, "Definition") or f"Governed Jarvis Dictionary object for {name}."
        purpose = extract(text, "Purpose")
        entry_path = path.relative_to(REPO_ROOT).as_posix()
        category, subcategory, confidence, reasons = classify(meta, name, definition, entry_path)
        aliases = as_list(meta.get("aliases"))
        tags = as_list(meta.get("tags"))
        record = {
            "schema_version": "jarvis.dictionary.entry.v2",
            "jid": None,
            "jnl": jnl,
            "name": name,
            "display_name": name,
            "slug": slugify(name),
            "aliases": aliases,
            "category": category,
            "subcategory": subcategory,
            "classification": {"status": "INFERRED", "confidence": confidence, "reasons": reasons},
            "domain": jnl.split("-", 1)[0] if "-" in jnl else None,
            "system_token": jnl.split("-")[1] if len(jnl.split("-")) > 1 else None,
            "type": meta.get("type"),
            "class": meta.get("class"),
            "tier": meta.get("tier"),
            "authority": meta.get("authority"),
            "status": meta.get("status"),
            "owner": meta.get("owner"),
            "steward": meta.get("steward"),
            "memory_tier": meta.get("memory_tier"),
            "created": meta.get("created"),
            "updated": meta.get("updated"),
            "definition": definition,
            "purpose": purpose,
            "tags": tags,
            "search_terms": sorted({normalize(name), normalize(jnl), *(normalize(x) for x in aliases), *(normalize(x) for x in tags)} - {""}),
            "relationships": edges(meta, entry_path),
            "routes": {"entry": entry_path, "canonical_source": meta.get("source"), "references": as_list(meta.get("references")), "reference_tokens": as_list(meta.get("ref"))},
            "provenance": {"entry_sha256": sha256(raw), "definition": {"status": "EXTRACTED", "source": entry_path}, "purpose": {"status": "EXTRACTED" if purpose else "UNKNOWN", "source": entry_path}, "classification": {"status": "INFERRED", "source": "build_semantic_catalog.py"}},
            "curation_status": "AUTO_CLASSIFIED",
        }
        records.append(record)
        source_meta.append({"path": entry_path, "meta": meta})
    return sorted(records, key=lambda x: (x["jnl"], x["name"])), source_meta


def title(path: Path) -> str:
    if path.suffix.lower() == ".md":
        text = path.read_text(encoding="utf-8", errors="replace")[:24000]
        meta = frontmatter(text)
        if meta.get("name"): return str(meta["name"]).strip()
        for line in text.splitlines()[:160]:
            if line.startswith("# "): return re.sub(r"\s+", " ", line[2:]).strip()
    return re.sub(r"\s+", " ", path.stem.replace("_", " ").replace("-", " ")).strip()


def discover(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    names: dict[str, set[str]] = defaultdict(set)
    represented: set[str] = set()
    for record in records:
        for value in [record["name"], record["jnl"], *record["aliases"]]:
            key = normalize(str(value))
            if key: names[key].add(record["jnl"])
        for value in record["routes"].values():
            if isinstance(value, str) and value: represented.add(value)
    candidates: list[dict[str, Any]] = []
    seen: set[tuple[str, str]] = set()
    for root in DISCOVERY_ROOTS:
        if not root.exists(): continue
        for path in sorted(root.rglob("*")):
            if not path.is_file() or path.suffix.lower() not in {".md", ".json", ".py", ".ts", ".tsx", ".js", ".mjs", ".cjs"}: continue
            if path.is_relative_to(CATALOG_ROOT) or path.is_relative_to(ENTRIES_ROOT): continue
            if any(part in SKIP_PARTS for part in path.parts): continue
            route = path.relative_to(REPO_ROOT).as_posix()
            if route in represented: continue
            name = title(path)
            key = normalize(name)
            if not key or key in GENERIC or key in names: continue
            if not SEMANTIC_SIGNAL.search(f"{name} {route}"): continue
            marker = (key, route)
            if marker in seen: continue
            seen.add(marker)
            category, subcategory, confidence, reasons = classify({}, name, "", route)
            candidates.append({
                "candidate_id": "CAND-" + sha256(f"{name}\n{route}".encode())[:16].upper(),
                "name": name,
                "normalized_name": key,
                "category_guess": category,
                "subcategory_guess": subcategory,
                "classification_confidence": confidence,
                "classification_reasons": reasons,
                "evidence_routes": [route],
                "possible_matches": [],
                "status": "UNREVIEWED",
                "minting_allowed": False,
            })
    return sorted(candidates, key=lambda x: (x["category_guess"], x["normalized_name"], x["candidate_id"]))


def build_indexes(records: list[dict[str, Any]]) -> dict[str, Any]:
    maps: dict[str, dict[str, list[str]]] = {name: defaultdict(list) for name in ["category", "subcategory", "tag", "owner", "steward", "status", "system", "alias"]}
    relationships: dict[str, list[dict[str, str]]] = defaultdict(list)
    for record in records:
        jnl = record["jnl"]
        maps["category"][record["category"]].append(jnl)
        maps["subcategory"][record["subcategory"]].append(jnl)
        for tag in record["tags"]: maps["tag"][normalize(tag).replace(" ", "-")].append(jnl)
        if record.get("owner"): maps["owner"][str(record["owner"])].append(jnl)
        if record.get("steward"): maps["steward"][str(record["steward"])].append(jnl)
        if record.get("status"): maps["status"][str(record["status"])].append(jnl)
        if record.get("system_token"): maps["system"][str(record["system_token"])].append(jnl)
        for alias in [record["name"], *record["aliases"]]: maps["alias"][normalize(alias)].append(jnl)
        for edge in record["relationships"]: relationships[edge["type"]].append({"source": jnl, "target": edge["target"]})
    result: dict[str, Any] = {"schema_version": "jarvis.dictionary.indexes.v2", "by_jnl": {record["jnl"]: i for i, record in enumerate(records)}, "by_name": {normalize(record["name"]): record["jnl"] for record in records}}
    for name, mapping in maps.items(): result[f"by_{name}"] = {k: sorted(set(v)) for k, v in sorted(mapping.items())}
    result["by_relationship"] = {k: sorted(v, key=lambda x: (x["source"], x["target"])) for k, v in sorted(relationships.items())}
    return result


def audit(records: list[dict[str, Any]], source_meta: list[dict[str, Any]], candidates: list[dict[str, Any]]) -> dict[str, Any]:
    known = {record["jnl"] for record in records}
    jnls: dict[str, list[str]] = defaultdict(list)
    aliases: dict[str, set[str]] = defaultdict(set)
    missing: list[dict[str, Any]] = []
    broken: list[dict[str, str]] = []
    unresolved: list[dict[str, str]] = []
    for source in source_meta:
        meta = source["meta"]
        jnl = str(meta.get("jnl") or Path(source["path"]).stem)
        jnls[jnl].append(source["path"])
        absent = [field for field in JSE_REQUIRED if field not in meta]
        if absent: missing.append({"jnl": jnl, "entry": source["path"], "missing": absent})
    for record in records:
        for alias in [record["name"], *record["aliases"]]: aliases[normalize(alias)].add(record["jnl"])
        source = record["routes"].get("canonical_source")
        if source and not (REPO_ROOT / source).exists(): broken.append({"jnl": record["jnl"], "route": source})
        for edge in record["relationships"]:
            target = edge["target"]
            if re.fullmatch(r"[A-Z0-9]+(?:-[A-Z0-9]+){2,}", target) and target not in known: unresolved.append({"source": record["jnl"], "type": edge["type"], "target": target})
    registry = json.loads(CATEGORY_REGISTRY.read_text(encoding="utf-8"))
    valid_categories = set(registry.get("categories", {}))
    unknown = sorted({record["category"] for record in records if record["category"] not in valid_categories})
    duplicate_jnls = [{"jnl": k, "paths": v} for k, v in sorted(jnls.items()) if len(v) > 1]
    alias_collisions = [{"alias": k, "jnls": sorted(v)} for k, v in sorted(aliases.items()) if len(v) > 1]
    return {
        "schema_version": "jarvis.dictionary.semantic-audit.v2",
        "record_count": len(records),
        "candidate_count": len(candidates),
        "invariants": {
            "duplicate_jnl_count": len(duplicate_jnls),
            "alias_collision_count": len(alias_collisions),
            "entries_missing_jse_fields": len(missing),
            "broken_route_count": len(broken),
            "unresolved_relationship_target_count": len(unresolved),
            "unknown_category_count": len(unknown),
        },
        "documentation_findings": [{"finding": "JSE field-count mismatch", "detail": "jse-schema.md says 19 keys but enumerates 20.", "status": "OPEN"}],
        "category_counts": dict(sorted(Counter(record["category"] for record in records).items())),
        "duplicate_jnls": duplicate_jnls,
        "alias_collisions": alias_collisions,
        "missing_jse_fields": missing,
        "broken_routes": broken,
        "unresolved_relationship_targets": unresolved,
        "unknown_categories": unknown,
    }


def readme(records: list[dict[str, Any]], candidates: list[dict[str, Any]], report: dict[str, Any]) -> str:
    category_rows = [f"| {k} | {v} |" for k, v in sorted(Counter(record["category"] for record in records).items(), key=lambda x: (-x[1], x[0]))]
    invariant_rows = [f"| {k} | {v} |" for k, v in report["invariants"].items()]
    return "\n".join([
        "# Jarvis Dictionary Semantic Catalog", "",
        f"- Governed JD entries: **{len(records)}**",
        f"- Unreviewed repository candidates: **{len(candidates)}**", "",
        "## Category distribution", "", "| Category | Entries |", "|---|---:|", *category_rows, "",
        "## ATOM audit", "", "| Invariant | Count |", "|---|---:|", *invariant_rows, "",
        "## Files", "",
        "- `JD-CATALOG.json` — enriched machine-readable entries;",
        "- `INDEXES.json` — semantic lookup indexes;",
        "- `DISCOVERY-CANDIDATES.json` — evidence awaiting governed review;",
        "- `SEMANTIC-AUDIT.json` — contradictions, missing fields, broken routes, and unresolved edges;",
        "- `CATEGORY-REGISTRY.json` and `RELATIONSHIP-ONTOLOGY.json` — controlled vocabularies.", "",
        "Candidates are evidence, not canon. Nothing is auto-minted.", "",
    ])


def expected() -> tuple[dict[str, str], dict[str, Any]]:
    records, source_meta = load_records()
    candidates = discover(records)
    report = audit(records, source_meta, candidates)
    outputs = {
        "catalog/JD-CATALOG.json": json.dumps({"schema_version": "jarvis.dictionary.catalog.v2", "builder": "build_semantic_catalog.py", "entry_count": len(records), "candidate_count": len(candidates), "authority": "ARCH-JD-CORE-0001", "specification": "ARCH-JD-SPEC-0002", "entries": records}, indent=2, ensure_ascii=False) + "\n",
        "catalog/INDEXES.json": json.dumps(build_indexes(records), indent=2, ensure_ascii=False) + "\n",
        "catalog/DISCOVERY-CANDIDATES.json": json.dumps({"schema_version": "jarvis.dictionary.discovery-candidates.v2", "count": len(candidates), "minting_policy": "NEVER_AUTOMATIC", "operator_authority": "RAVEN", "candidates": candidates}, indent=2, ensure_ascii=False) + "\n",
        "catalog/SEMANTIC-AUDIT.json": json.dumps(report, indent=2, ensure_ascii=False) + "\n",
        "catalog/README.md": readme(records, candidates, report),
    }
    return outputs, {"entries": len(records), "candidates": len(candidates), **report["invariants"]}


def write(outputs: dict[str, str]) -> None:
    for relative, content in outputs.items():
        path = JD_ROOT / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")


def check(outputs: dict[str, str]) -> list[str]:
    failures: list[str] = []
    for relative, content in outputs.items():
        path = JD_ROOT / relative
        if not path.exists(): failures.append(f"missing: {relative}")
        elif path.read_text(encoding="utf-8") != content: failures.append(f"stale: {relative}")
    return failures


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--write", action="store_true")
    mode.add_argument("--check", action="store_true")
    args = parser.parse_args()
    outputs, summary = expected()
    if args.write:
        write(outputs)
        print(json.dumps({"status": "written", **summary}, indent=2))
        return 0
    failures = check(outputs)
    if failures:
        print("JD semantic catalog check failed:", file=sys.stderr)
        for failure in failures: print(f"- {failure}", file=sys.stderr)
        return 1
    print(json.dumps({"status": "valid", **summary}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
