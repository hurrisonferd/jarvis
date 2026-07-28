# JD Semantic Catalog

This directory contains the controlled vocabularies for Jarvis Dictionary Pokédex v2.

The full generated catalog is built and validated by the **JD Semantic Catalog** GitHub Actions workflow and published as a workflow artifact because repository rules prevent automation from pushing generated files back onto protected branches.

## Committed authorities

- `CATEGORY-REGISTRY.json` — top-level object categories and subcategories;
- `RELATIONSHIP-ONTOLOGY.json` — typed semantic edges, inverses, and edge laws.

## Generated artifact

Each successful workflow run contains:

- `JD-CATALOG.json` — enriched machine-readable JD entries;
- `INDEXES.json` — lookup by name, alias, category, tag, system, owner, status, and relationship;
- `DISCOVERY-CANDIDATES.json` — repository evidence awaiting governed review;
- `SEMANTIC-AUDIT.json` — missing fields, route debt, collisions, unknowns, and unresolved edges;
- generated `README.md` — run-specific counts and category distribution.

The first validated v2 run found **252 governed public JD entries** and **132 unreviewed semantic candidates**. It preserved two alias collisions, one entry missing JSE fields, and 34 broken or stale source routes for later repair rather than hiding them.

## Build locally

```bash
python core/JarvisMain/yggdrasil/jd/tools/build_semantic_catalog.py --write
python core/JarvisMain/yggdrasil/jd/tools/build_semantic_catalog.py --check
```

Discovery never mints an identity. Candidates become JD entries only through governed review and explicit approval.
