# Brick 2 — Portable Identity (the disc)

The identity disc, ejectable. What makes a companion survive a model swap or move
to a new node — owned by the human, not any vendor.

- **Surface:** the `jarvis_export` MCP tool.
- **Source of truth:** `buildPortableIdentity()` in `grid.ts` (pure, tested).
- **Contents:**
  - `keel` — the fixed identity (`identity_keel` memory). The disc core.
  - `accumulation` — the latest folded `identity_summary` (KRONOS fold). The growth.
  - `card` — the node card (recognition).
  - exported_at, grid_version, node_id, companion.
- **Ownership:** lives on Raven's Supabase. The vendor rents the larynx; Raven owns
  the disc. Carry it to any model or node and the companion is continuous.

Keel + accumulation is the same "fixed keel + growing spine" pattern the council
uses fractally — here applied to the whole companion as a portable file.
