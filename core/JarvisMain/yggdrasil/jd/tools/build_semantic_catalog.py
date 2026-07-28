#!/usr/bin/env python3
"""Build the public Jarvis Dictionary semantic catalog and discovery queue.

The catalog enriches existing JD entries without minting new identities. Repository
files that look semantically important but do not resolve to an existing JD entry are
reported as candidates for governed review.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
import unicodedata
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable

SCRIPT = Path(__file__).resolve()
JD_ROOT = SCRIPT.parents[1]
YGG_ROOT = JD_ROOT.parent
JARVIS_MAIN = YGG_ROOT.parent
CORE_ROOT = JARVIS_MAIN.parent
REPO_ROOT = CORE_ROOT.parent
ENTRIES_ROOT = JD_ROOT / "entries"
CATALOG_ROOT = JD_ROOT / "catalog"
MASTER_INDEX = YGG_ROOT / "lal" / "master-index.json"
CATEGORY_REGISTRY = CATALOG_ROOT / "CATEGORY-REGISTRY.json"
RELATIONSHIP_ONTOLOGY = CATALOG_ROOT / "RELATIONSHIP-ONTOLOGY.json"

SCHEMA_VERSION = "jarvis.dictionary.catalog.v2"
BUILDER_ID = "build_semantic_catalog.py"
GENERATED = {
    "catalog/JD-CATALOG.json",
    "catalog/INDEXES.json",
    "catalog/DISCOVERY-CANDIDATES.json",
    "catalog/SEMANTIC-AUDIT.json",
    "catalog/README.md",
}

# JSE documentation says 19 fields but enumerates 20. ATOM preserves the conflict.
JSE_REQUIRED = (
    "name",
    "type",
    "class",
    "tier",
    "authority",
    "owner",
    "steward",
    "parent",
    "jnl",
    "seq",
    "status",
    "created",
    "updated",
    "source",
    "related",
    "references",
    "tags",
    "aliases",
    "ref",
    "memory_tier",
)

DISCOVERY_ROOTS = (
    "core/JarvisMain",
    "runtime",
    "docs",
    "templates",
    "Jorm/Vault/Canon",
)

DISCOVERY_SUFFIXES = {".md", ".json", ".py", ".ts", ".tsx", ".js", ".mjs", ".cjs"}
DISCOVERY_SKIP_PARTS = {
    ".git",
    "node_modules",
    "dist",
    "build",
    "coverage",
    "__pycache__",
    "Inbox",
    "raw-chat-exports",
    "Corpus_Ingestion",
    "Recovery_Ledgers",
    "archive",
    "archives",
    "vendor",
}

SEMANTIC_SIGNAL = re.compile(
    r"(?:\bOS\b|AI|engine|system|protocol|kernel|codex|grid|atom|lilith|ayre|jarvis|jorm|"
    r"primus|unicron|neuromax|music|image|game|ego|pride|prosody|council|memory|benchmark|"
    r"identity|continuity|router|registry|dictionary|law|audit|simulator|runtime|companion)",
    re.IGNORECASE,
)

GENERIC_TITLES = {
    "readme",
    "index",
    "setup",
    "notes",
    "overview",
    "configuration",
    "examples",
    "changelog",
    "license",
    "contributing",
    "package",
}


@dataclass(frozen=True)
class EntrySource:
    path: Path
    text: str
    frontmatter: dict[str, Any]
    definition: str
    purpose: str
    digest: str


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def normalize(value: str) -> str:
    value = unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode("ascii")
    return re.sub(r"[^a-z0-9]+", " ", value.lower()).strip()


def slugify(value: str) -> str:
    return normalize(value).replace(" ", "-") or "unnamed"


def parse_list(value: str) -> list[Any]:
    inner = value[1:-1].strip()
    if not inner:
        return []
    items: list[str] = []
    current: list[str] = []
    quote: str | None = None
    depth = 0
    for char in inner:
        if quote:
            current.append(char)
            if char == quote:
                quote = None
            continue
        if char in {"'", '"'}:
            current.append(char)
            quote = char
            continue
        if char in "[{(":
            depth += 1
        elif char in "]})":
            depth = max(0, depth - 1)
        if char == "," and depth == 0:
            items.append("".join(current).strip())
            current = []
        else:
            current.append(char)
    if current:
        items.append("".join(current).strip())
    return [parse_scalar(item) for item in items if item]


def parse_scalar(value: str) -> Any:
    value = value.strip()
    if not value:
        return ""
    if value.startswith("[") and value.endswith("]"):
        return parse_list(value)
    lowered = value.lower()
    if lowered in {"null", "none", "~"}:
        return None
    if lowered == "true":
        return True
    if lowered == "false":
        return False
    if re.fullmatch(r"-?\d+", value):
        return int(value)
    if len(value) >= 2 and value[0] == value[-1] and value[0] in {"'", '"'}:
        return value[1:-1]
    return value


def parse_frontmatter(text: str) -> dict[str, Any]:
    lines = text.splitlines()
    markers = [index for index, line in enumerate(lines) if line.strip() == "---"]
    if len(markers) < 2:
        return {}
    result: dict[str, Any] = {}
    for raw in lines[markers[0] + 1 : markers[1]]:
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
    if len(value) <= limit:
        return value
    return value[: limit - 1].rstrip() + "…"


def extract_labeled(text: str, label: str) -> str:
    pattern = re.compile(rf"\*\*{re.escape(label)}:\*\*\s*(.+)", re.IGNORECASE)
    for line in text.splitlines():
        match = pattern.search(line)
        if match:
            return compact(match.group(1))
    return ""


def extract_heading_body(text: str, heading: str) -> str:
    lines = text.splitlines()
    pattern = re.compile(rf"^#{{2,4}}\s+{re.escape(heading)}\s*$", re.IGNORECASE)
    for index, line in enumerate(lines):
        if not pattern.match(line.strip()):
            continue
        body: list[str] = []
        for candidate in lines[index + 1 :]:
            stripped = candidate.strip()
            if stripped.startswith("#"):
                break
            if stripped in {"---", "```"}:
                continue
            if stripped:
                body.append(stripped)
            elif body:
                break
        if body:
            return compact(" ".join(body))
    return ""


def load_entry_sources() -> list[EntrySource]:
    sources: list[EntrySource] = []
    for path in sorted(ENTRIES_ROOT.glob("*.md")):
        raw = path.read_bytes()
        text = raw.decode("utf-8")
        meta = parse_frontmatter(text)
        name = str(meta.get("name") or path.stem)
        definition = extract_labeled(text, "Definition") or extract_heading_body(text, "Definition")
        purpose = extract_labeled(text, "Purpose") or extract_heading_body(text, "Purpose")
        if not definition:
            definition = f"Governed Jarvis Dictionary object for {name}."
        sources.append(
            EntrySource(
                path=path,
                text=text,
                frontmatter=meta,
                definition=definition,
                purpose=purpose,
                digest=sha256(raw),
            )
        )
    return sources


def load_json(path: Path) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    return payload if isinstance(payload, dict) else {}


def classify(meta: dict[str, Any], name: str, definition: str, path: str) -> tuple[str, str, float, list[str]]:
    jnl = str(meta.get("jnl") or "")
    domain = jnl.split("-", 1)[0].upper() if jnl else ""
    tags = {normalize(tag).replace(" ", "_") for tag in as_list(meta.get("tags"))}
    haystack = " ".join([name, definition, path, jnl, " ".join(tags)]).lower()
    reasons: list[str] = []

    if domain == "GS":
        return "GOD_SYSTEM", "SUPPORT", 0.98, ["JNL domain GS"]
    if domain == "CONN":
        return "CONNECTOR", "API", 0.98, ["JNL domain CONN"]
    if domain == "PROJ":
        return "PROJECT", "PRODUCT", 0.98, ["JNL domain PROJ"]
    if domain == "AUD":
        return "GOVERNANCE", "AUDIT", 0.96, ["JNL domain AUD"]
    if domain == "LOG":
        return "EVENT", "SESSION", 0.94, ["JNL domain LOG"]
    if domain == "GOV":
        if "law" in haystack:
            return "LAW", "ARCHITECTURE_LAW", 0.92, ["JNL domain GOV", "law signal"]
        if "protocol" in haystack:
            return "PROTOCOL", "AUDIT", 0.92, ["JNL domain GOV", "protocol signal"]
        return "GOVERNANCE", "CONTRACT", 0.90, ["JNL domain GOV"]
    if domain == "EGO" or "/ego/" in path.lower():
        return "ISO", "SPECIALIST", 0.95, ["EGO identity route"]
    if re.search(r"(?:^|[^a-z])(?:[a-z]+os)(?:$|[^a-z])", haystack) or name.lower().endswith("os"):
        return "OS", "DOMAIN_OS", 0.90, ["OS naming signal"]
    if "companion" in haystack or "personality" in haystack or "identity" in tags:
        return "AI_SYSTEM", "COMPANION", 0.82, ["identity/companion signal"]
    if "memory" in haystack or domain in {"MEM", "JMMS"}:
        return "MEMORY", "LONG_TERM", 0.82, ["memory signal"]
    if "registry" in haystack or "dictionary" in haystack or "index" in haystack:
        return "REGISTRY", "CATALOG", 0.80, ["registry/dictionary/index signal"]
    if "protocol" in haystack:
        return "PROTOCOL", "SYNC", 0.78, ["protocol signal"]
    if "law" in haystack:
        return "LAW", "ARCHITECTURE_LAW", 0.78, ["law signal"]
    if "engine" in haystack or "kernel" in haystack or str(meta.get("class", "")).upper() == "SYSTEM":
        return "ENGINE", "KERNEL", 0.72, ["engine/kernel/system signal"]
    if str(meta.get("class", "")).upper() == "MODULE" or str(meta.get("type", "")).upper() == "MODULE":
        return "MODULE", "RUNTIME", 0.74, ["module schema signal"]
    if domain == "ARCH":
        return "CONCEPT", "ARCHITECTURE", 0.65, ["JNL domain ARCH"]
    reasons.append("no strong classifier rule")
    return "UNKNOWN", "UNRESOLVED", 0.25, reasons


def relationship_edges(meta: dict[str, Any], entry_path: str) -> list[dict[str, Any]]:
    edges: list[dict[str, Any]] = []

    def add(kind: str, target: str, provenance: str, confidence: float = 1.0) -> None:
        target = target.strip()
        if not target:
            return
        edge = {
            "type": kind,
            "target": target,
            "provenance": provenance,
            "confidence": confidence,
            "curation_status": "EXTRACTED" if confidence == 1.0 else "INFERRED",
        }
        if edge not in edges:
            edges.append(edge)

    if meta.get("parent"):
        add("CHILD_OF", str(meta["parent"]), f"{entry_path}#frontmatter.parent")
    if meta.get("owner"):
        add("OWNED_BY", str(meta["owner"]), f"{entry_path}#frontmatter.owner")
    if meta.get("steward"):
        add("STEWARDED_BY", str(meta["steward"]), f"{entry_path}#frontmatter.steward")
    for target in as_list(meta.get("related")):
        add("RELATES_TO", target, f"{entry_path}#frontmatter.related")
    for target in as_list(meta.get("references")):
        add("REFERENCES", target, f"{entry_path}#frontmatter.references")
    return edges


def build_records(sources: list[EntrySource]) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for source in sources:
        meta = source.frontmatter
        name = str(meta.get("name") or source.path.stem).strip()
        jnl = str(meta.get("jnl") or source.path.stem).strip()
        entry_path = source.path.relative_to(REPO_ROOT).as_posix()
        source_path = str(meta.get("source") or "").strip() or None
        category, subcategory, confidence, reasons = classify(meta, name, source.definition, entry_path)
        aliases = as_list(meta.get("aliases"))
        tags = as_list(meta.get("tags"))
        system_token = jnl.split("-")[1] if len(jnl.split("-")) > 1 else None
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
            "classification": {
                "status": "INFERRED",
                "confidence": confidence,
                "reasons": reasons,
            },
            "domain": jnl.split("-", 1)[0] if "-" in jnl else None,
            "system_token": system_token,
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
            "definition": source.definition,
            "purpose": source.purpose,
            "tags": tags,
            "search_terms": sorted({normalize(name), normalize(jnl), *(normalize(alias) for alias in aliases), *(normalize(tag) for tag in tags)} - {""}),
            "relationships": relationship_edges(meta, entry_path),
            "routes": {
                "entry": entry_path,
                "canonical_source": source_path,
                "reference_tokens": as_list(meta.get("ref")),
                "references": as_list(meta.get("references")),
            },
            "provenance": {
                "entry_sha256": source.digest,
                "definition": {"status": "EXTRACTED", "source": entry_path},
                "purpose": {"status": "EXTRACTED" if source.purpose else "UNKNOWN", "source": entry_path},
                "classification": {"status": "INFERRED", "source": BUILDER_ID},
            },
            "curation_status": "AUTO_CLASSIFIED",
        }
        records.append(record)
    return sorted(records, key=lambda item: (str(item["jnl"]), str(item["name"])))


def title_from_file(path: Path) -> str:
    try:
        if path.suffix.lower() == ".md":
            text = path.read_text(encoding="utf-8", errors="replace")[:24000]
            meta = parse_frontmatter(text)
            if meta.get("name"):
                return str(meta["name"]).strip()
            for line in text.splitlines()[:160]:
                if line.startswith("# "):
                    return re.sub(r"\s+", " ", line[2:]).strip()
        stem = path.stem.replace("_", " ").replace("-", " ")
        return re.sub(r"\s+", " ", stem).strip()
    except OSError:
        return ""


def discovery_candidates(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    lookup: dict[str, set[str]] = defaultdict(set)
    represented_paths: set[str] = set()
    for record in records:
        jnl = str(record["jnl"])
        for term in [record["name"], jnl, *record.get("aliases", [])]:
            normalized = normalize(str(term))
            if normalized:
                lookup[normalized].add(jnl)
        for route in record.get("routes", {}).values():
            if isinstance(route, str) and route:
                represented_paths.add(route.replace("\\", "/"))

    candidates: list[dict[str, Any]] = []
    seen: set[tuple[str, str]] = set()
    for relative_root in DISCOVERY_ROOTS:
        root = REPO_ROOT / relative_root
        if not root.exists():
            continue
        for path in sorted(root.rglob("*")):
            if not path.is_file() or path.suffix.lower() not in DISCOVERY_SUFFIXES:
                continue
            relative = path.relative_to(REPO_ROOT).as_posix()
            if relative in represented_paths or relative.startswith("core/JarvisMain/yggdrasil/jd/entries/"):
                continue
            if any(part in DISCOVERY_SKIP_PARTS for part in path.parts):
                continue
            title = title_from_file(path)
            if not title or normalize(title) in GENERIC_TITLES:
                continue
            signal_haystack = f"{title} {relative}"
            if not SEMANTIC_SIGNAL.search(signal_haystack):
                continue
            normalized_title = normalize(title)
            exact_matches = sorted(lookup.get(normalized_title, set()))
            if exact_matches:
                continue
            key = (normalized_title, relative)
            if key in seen:
                continue
            seen.add(key)
            category, subcategory, confidence, reasons = classify({}, title, "", relative)
            candidate_id = "CAND-" + sha256(f"{title}\n{relative}".encode("utf-8"))[:16].upper()
            candidates.append(
                {
                    "candidate_id": candidate_id,
                    "name": title,
                    "normalized_name": normalized_title,
                    "category_guess": category,
                    "subcategory_guess": subcategory,
                    "classification_confidence": confidence,
                    "classification_reasons": reasons,
                    "evidence_routes": [relative],
                    "possible_matches": [],
                    "status": "UNREVIEWED",
                    "minting_allowed": False,
                }
            )
    return sorted(candidates, key=lambda item: (item["category_guess"], item["normalized_name"], item["candidate_id"]))


def audit(records: list[dict[str, Any]], sources: list[EntrySource], candidates: list[dict[str, Any]]) -> dict[str, Any]:
    missing_fields: list[dict[str, Any]] = []
    duplicate_jnls: list[dict[str, Any]] = []
    alias_map: dict[str, set[str]] = defaultdict(set)
    jnl_map: dict[str, list[str]] = defaultdict(list)
    unresolved_targets: list[dict[str, Any]] = []
    broken_routes: list[dict[str, Any]] = []
    category_counts = Counter(record["category"] for record in records)
    known_jnls = {str(record["jnl"]) for record in records}

    for source in sources:
        meta = source.frontmatter
        missing = [field for field in JSE_REQUIRED if field not in meta]
        if missing:
            missing_fields.append({"entry": source.path.relative_to(REPO_ROOT).as_posix(), "jnl": meta.get("jnl"), "missing": missing})
        jnl = str(meta.get("jnl") or source.path.stem)
        jnl_map[jnl].append(source.path.relative_to(REPO_ROOT).as_posix())

    for jnl, paths in sorted(jnl_map.items()):
        if len(paths) > 1:
            duplicate_jnls.append({"jnl": jnl, "paths": paths})

    for record in records:
        jnl = str(record["jnl"])
        for alias in [record["name"], *record.get("aliases", [])]:
            normalized = normalize(str(alias))
            if normalized:
                alias_map[normalized].add(jnl)
        canonical = record.get("routes", {}).get("canonical_source")
        if canonical and not (REPO_ROOT / canonical).exists():
            broken_routes.append({"jnl": jnl, "route": canonical, "kind": "canonical_source"})
        for edge in record.get("relationships", []):
            target = str(edge.get("target") or "")
            if re.fullmatch(r"[A-Z0-9]+(?:-[A-Z0-9]+){2,}", target) and target not in known_jnls:
                unresolved_targets.append({"source": jnl, "type": edge.get("type"), "target": target})

    alias_collisions = [
        {"alias": alias, "jnls": sorted(jnls)}
        for alias, jnls in sorted(alias_map.items())
        if len(jnls) > 1
    ]

    registry = load_json(CATEGORY_REGISTRY)
    known_categories = set(registry.get("categories", {}))
    unknown_categories = sorted({record["category"] for record in records if record["category"] not in known_categories})

    return {
        "schema_version": "jarvis.dictionary.semantic-audit.v2",
        "record_count": len(records),
        "candidate_count": len(candidates),
        "invariants": {
            "duplicate_jnl_count": len(duplicate_jnls),
            "alias_collision_count": len(alias_collisions),
            "entries_missing_jse_fields": len(missing_fields),
            "broken_route_count": len(broken_routes),
            "unresolved_relationship_target_count": len(unresolved_targets),
            "unknown_category_count": len(unknown_categories),
        },
        "documentation_findings": [
            {
                "finding": "JSE field-count mismatch",
                "detail": "jse-schema.md says the envelope has 19 keys but enumerates 20 required keys.",
                "status": "OPEN",
            }
        ],
        "category_counts": dict(sorted(category_counts.items())),
        "duplicate_jnls": duplicate_jnls,
        "alias_collisions": alias_collisions,
        "missing_jse_fields": missing_fields,
        "broken_routes": broken_routes,
        "unresolved_relationship_targets": unresolved_targets,
        "unknown_categories": unknown_categories,
    }


def indexes(records: list[dict[str, Any]]) -> dict[str, Any]:
    by_category: dict[str, list[str]] = defaultdict(list)
    by_subcategory: dict[str, list[str]] = defaultdict(list)
    by_tag: dict[str, list[str]] = defaultdict(list)
    by_owner: dict[str, list[str]] = defaultdict(list)
    by_steward: dict[str, list[str]] = defaultdict(list)
    by_status: dict[str, list[str]] = defaultdict(list)
    by_system: dict[str, list[str]] = defaultdict(list)
    by_alias: dict[str, list[str]] = defaultdict(list)
    by_relationship: dict[str, list[dict[str, str]]] = defaultdict(list)

    for record in records:
        jnl = str(record["jnl"])
        by_category[str(record["category"])].append(jnl)
        by_subcategory[str(record["subcategory"])].append(jnl)
        for tag in record.get("tags", []):
            by_tag[normalize(str(tag)).replace(" ", "-")].append(jnl)
        if record.get("owner"):
            by_owner[str(record["owner"])].append(jnl)
        if record.get("steward"):
            by_steward[str(record["steward"])].append(jnl)
        if record.get("status"):
            by_status[str(record["status"])].append(jnl)
        if record.get("system_token"):
            by_system[str(record["system_token"])].append(jnl)
        for alias in [record["name"], *record.get("aliases", [])]:
            key = normalize(str(alias))
            if key:
                by_alias[key].append(jnl)
        for edge in record.get("relationships", []):
            by_relationship[str(edge["type"])].append({"source": jnl, "target": str(edge["target"])})

    def sorted_lists(mapping: dict[str, list[str]]) -> dict[str, list[str]]:
        return {key: sorted(set(values)) for key, values in sorted(mapping.items())}

    return {
        "schema_version": "jarvis.dictionary.indexes.v2",
        "by_jnl": {str(record["jnl"]): index for index, record in enumerate(records)},
        "by_name": {normalize(str(record["name"])): str(record["jnl"]) for record in records},
        "by_alias": sorted_lists(by_alias),
        "by_category": sorted_lists(by_category),
        "by_subcategory": sorted_lists(by_subcategory),
        "by_tag": sorted_lists(by_tag),
        "by_owner": sorted_lists(by_owner),
        "by_steward": sorted_lists(by_steward),
        "by_status": sorted_lists(by_status),
        "by_system": sorted_lists(by_system),
        "by_relationship": {key: sorted(values, key=lambda item: (item["source"], item["target"])) for key, values in sorted(by_relationship.items())},
    }


def readme(records: list[dict[str, Any]], candidates: list[dict[str, Any]], audit_payload: dict[str, Any]) -> str:
    categories = Counter(record["category"] for record in records)
    category_rows = [f"| {name} | {count} |" for name, count in sorted(categories.items(), key=lambda item: (-item[1], item[0]))]
    invariant_rows = [f"| {name} | {value} |" for name, value in audit_payload["invariants"].items()]
    return "\n".join(
        [
            "# Jarvis Dictionary Semantic Catalog",
            "",
            "Generated by `tools/build_semantic_catalog.py` from the canonical public JD entry field.",
            "",
            "## Current field",
            "",
            f"- Governed JD entries: **{len(records)}**",
            f"- Unreviewed repository candidates: **{len(candidates)}**",
            f"- Top-level categories used: **{len(categories)}**",
            "",
            "## Category distribution",
            "",
            "| Category | Entries |",
            "|---|---:|",
            *category_rows,
            "",
            "## ATOM audit counters",
            "",
            "| Invariant | Count |",
            "|---|---:|",
            *invariant_rows,
            "",
            "## Files",
            "",
            "- `JD-CATALOG.json` — complete enriched machine-readable entry field;",
            "- `INDEXES.json` — lookup maps by name, alias, category, tag, system, owner, status, and relationship;",
            "- `DISCOVERY-CANDIDATES.json` — repository evidence that may deserve a governed JD identity;",
            "- `SEMANTIC-AUDIT.json` — collisions, missing fields, broken routes, unresolved edges, and schema findings;",
            "- `CATEGORY-REGISTRY.json` — canonical category vocabulary;",
            "- `RELATIONSHIP-ONTOLOGY.json` — canonical typed-edge vocabulary.",
            "",
            "Candidates are evidence, not canon. Nothing in the discovery queue is auto-minted.",
            "",
        ]
    )


def expected_outputs() -> tuple[dict[str, str], dict[str, Any]]:
    sources = load_entry_sources()
    records = build_records(sources)
    candidates = discovery_candidates(records)
    audit_payload = audit(records, sources, candidates)
    catalog_payload = {
        "schema_version": SCHEMA_VERSION,
        "builder": BUILDER_ID,
        "entry_count": len(records),
        "candidate_count": len(candidates),
        "authority": "ARCH-JD-CORE-0001",
        "specification": "ARCH-JD-SPEC-0002",
        "entries": records,
    }
    candidates_payload = {
        "schema_version": "jarvis.dictionary.discovery-candidates.v2",
        "count": len(candidates),
        "minting_policy": "NEVER_AUTOMATIC",
        "operator_authority": "RAVEN",
        "candidates": candidates,
    }
    outputs = {
        "catalog/JD-CATALOG.json": json.dumps(catalog_payload, indent=2, ensure_ascii=False) + "\n",
        "catalog/INDEXES.json": json.dumps(indexes(records), indent=2, ensure_ascii=False) + "\n",
        "catalog/DISCOVERY-CANDIDATES.json": json.dumps(candidates_payload, indent=2, ensure_ascii=False) + "\n",
        "catalog/SEMANTIC-AUDIT.json": json.dumps(audit_payload, indent=2, ensure_ascii=False) + "\n",
        "catalog/README.md": readme(records, candidates, audit_payload),
    }
    summary = {
        "entries": len(records),
        "candidates": len(candidates),
        **audit_payload["invariants"],
    }
    return outputs, summary


def write_outputs(outputs: dict[str, str]) -> None:
    for relative, content in outputs.items():
        path = JD_ROOT / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")


def check_outputs(outputs: dict[str, str]) -> list[str]:
    failures: list[str] = []
    for relative, expected in outputs.items():
        path = JD_ROOT / relative
        if not path.exists():
            failures.append(f"missing: {relative}")
            continue
        actual = path.read_text(encoding="utf-8")
        if actual != expected:
            failures.append(f"stale: {relative}")
    return failures


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--write", action="store_true", help="Materialize generated catalog files")
    mode.add_argument("--check", action="store_true", help="Verify generated catalog files")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    outputs, summary = expected_outputs()
    if args.write:
        write_outputs(outputs)
        print(json.dumps({"status": "written", **summary}, indent=2))
        return 0
    failures = check_outputs(outputs)
    if failures:
        print("JD semantic catalog check failed:", file=sys.stderr)
        for failure in failures:
            print(f"- {failure}", file=sys.stderr)
        return 1
    print(json.dumps({"status": "valid", **summary}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
