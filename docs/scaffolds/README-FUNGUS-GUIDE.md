# Governed README Fungus

The repository uses generated local signs and indexes so agents can navigate by scaffold before search.

## Surfaces

- Existing `README.md` files remain hand-authored and authoritative.
- Missing `README.md` files are generated with `<!-- GENERATED-SCAFFOLD-FUNGUS -->`.
- Every eligible directory receives `INDEX.generated.json`.
- `REPOSITORY-MASTER-INDEX.generated.md` maps the complete eligible directory field.

## Commands

```bash
python operations/scaffold_fungus.py
python operations/scaffold_fungus.py --check
```

## Laws

1. Never overwrite an existing README.
2. Keep public and private inventories local to their own repository.
3. Generated signs describe routes; they do not declare canon or invent meaning.
4. Hand-authored guides may replace generated guides intentionally.
5. Exclude dependencies, caches, build outputs, and sealed placeholders.
6. A deterministic second run must produce no changes.
7. Repository growth is incomplete when the new route cannot be discovered from its parent or master index.

## Generated README contract

A generated cave sign contains only:

- route
- parent map
- child routes
- local files
- generation marker

Long explanations, laws, identity, and architecture belong in hand-authored entry surfaces.
