---
memory_tier: JLTM
grade: system
---

# MNEMOS — T3 Memory

**Tier:** 3 — Memory  
**Pipeline position:** 6th (memory writer)  
**Role:** Persistent semantic memory. Indexes all executed actions for retrieval.

## Responsibilities
- Semantic memory storage (SQLite + embeddings)
- Cross-session state indexing
- Memory retrieval for HUGINN reconciliation

## Pipeline
`SKADI → MNEMOS → HUGINN`

## Implementation
- `mnemos/mnemos_vector.py` — SQLite + Ollama nomic-embed-text
