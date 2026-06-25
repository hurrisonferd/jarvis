# Phase 4 — Memory Audit

**Generated:** 2026-06-24T23:32Z  
**Scope:** MNEMOS, JMMS tiers, session log, chaos state

---

## ✅ PHASE-4 COMPLETE: MNEMOS wired to MCP, JMMS defined in MCP layer, session logging active, chaos excluded from git

---

## MNEMOS Functions

| Function | Edge | MCP Tool | Status | Tier Stamping |
|----------|------|----------|--------|---------------|
| `mnemos-store` | ✅ | `jarvis_remember` stamps tiers | Partial | ❌ Edge does not stamp tier tags |
| `mnemos-recall` | ✅ | `jarvis_recall` | Partial | ❌ Edge does not filter by tier |
| `mnemos-search` | ✅ | via `jarvis_recall` | Partial | ❌ Edge does not filter by tier |
| `mnemos-embed` | ✅ | internal | Partial | ❌ Edge does not stamp tier |

**Verdict (MNEMOS):** ✅ All 4 mnemos functions exist as Supabase edge functions and are wired to MCP. ❌ But none of the direct edge functions implement JMMS tiering — only the `jarvis_remember` / `jarvis_jmms` tool wrappers in the MCP layer handle tier stamping and promotion.

---

## JMMS Tiers — Implementation Map

| Tier | Horizon | Defined in MCP | Edge Query | Recall Path | Status |
|------|---------|---------------|------------|-------------|--------|
| JITM | always-on / pinned | ✅ `tierTag()` | ✅ `tags=cs.jitm` | ✅ jarvis_query | KEEP |
| JSTM | working / session | ✅ | N/A | N/A (session-scoped) | PARTIAL — defined, not persisted to Supabase |
| JLTM | consolidated / default | ✅ | ❌ | ❌ (no active recall) | BUILD |
| JATM | ancestral / immutable | ✅ | ❌ | ❌ (git/PROMETHEUS path) | BUILD |

**JSTM behavior:** Session-scoped. Defined in `jarvis_mcp/index.ts` with `tierTag()` function. `jarvis_jmms` tool description says "JSTM is the live context-window: mark notes jstm to keep them in view." Not persisted to Supabase — correct per spec (JSTM = working/session).

**JATM behavior:** Immutable ancestral. Spec says backed by `event_spine`, git history, PROMETHEUS. No Supabase path. Correct — JATM doesn't belong in `mnemos_memories`.

**JLTM gap:** The "consolidated/durable" tier — the actual memory workhorse — has no dedicated edge function or recall path. This is the most significant gap.

**Verdict (JMMS):** ✅ JITM working. ⚠️ JLTM needs active recall path. JSTM/JATM architected correctly.

---

## Session Log

| Component | File | What It Logs | Git-Excluded |
|-----------|------|-------------|-------------|
| Session start | `chaos/session_sync.py` → `session_start()` | `session_id`, `platform`, `archetype`, `role`, `chaos_version`, `jarvis_version`, `mission`, `eris_active`, `entropy_score`, `gold_law_rules`, `pipeline_order` | ✅ `.gitignore` |
| Session end | `chaos/session_sync.py` → `session_end()` | `session_id`, `sealed_at`, `drift_score`, `huginn_diff`, `narrative`, `chaos_updated`, `fingerprint` | ✅ `.gitignore` |
| Drift guard | `session_end()` | Blocks update if drift < 0.85 or unauthorized changes | ✅ |
| Entropy | `_compute_entropy()` | `compute_entropy()` on session start/end | ✅ |
| HUGINN diff | `huginn_diff()` | Cross-session reconciliation snapshot | ✅ |

**Session log schema (written to `chaos/session_log.json`):**
```json
{
  "session_id": "uuid",
  "platform": "claude_code",
  "started_at": "ISO8601",
  "sealed_at": "ISO8601",
  "entropy_score": 0.0-1.0,
  "drift_score": 0.0-1.0,
  "huginn_diff": { ... },
  "narrative": "string",
  "chaos_updated": boolean,
  "fingerprint": "hash"
}
```

**Verdict (session_log):** ✅ Active, comprehensive, git-excluded.

---

## Chaos State

| File | Purpose | In .gitignore | Notes |
|------|---------|---------------|-------|
| `chaos/chaos_seed.json` | Live state cache (private) | ✅ YES | Local-only — never committed |
| `chaos/session_log.json` | Session logs | ✅ YES | Written by session_sync.py |
| `chaos/prometheus_log.json` | Decision log | ✅ YES | Local decision tracking |
| `chaos/mnemos_vectors.db` | (referenced in AGENTS.md) | ✅ implicitly excluded | Vector cache |
| `chaos/session_sync.py` | Session start/end helpers | ❌ NO | Code — committed to git |
| `chaos/chaos_seed.example.json` | Sanitized example | ❌ NO | Example — committed |

**Verdict (chaos):** ✅ Chaos state fully excluded from git. `chaos_seed.example.json` is a sanitized example, correctly committed.

---

## Supabase Memory Schema

**Table:** `public.mnemos_memories`

| Column | Source | Notes |
|--------|--------|-------|
| `id` | `uuid` PK | |
| `source_id` | `text` | |
| `source_type` | `text` | |
| `text` | `text` | main content |
| `entropy` | `real` | |
| `platform` | `text` | |
| `metadata` | `jsonb` | |
| `timestamp` | `timestamptz` | indexed |
| `tags` | `text[]` | JMMS tier tags (origin: later migration, not in initial schema) |
| `embedding` | `vector(1024)` | pgvector with HNSW index |

**Embedding dimension history:** 768 → 1536 → 1024. Latest migration sets 1024. The 1024 dimension is what the current `mnemos-embed` uses.

**Retention:** `20260618_mnemos_retention.sql` prunes `auto_ingest`-tagged rows older than N days.

**Verdict (schema):** ✅ Clean. Vector search + full-text + tags. Retention policy active.

---

## Critical Issues

| # | Issue | Severity | System | Action |
|---|-------|----------|--------|--------|
| 1 | **MNEMOS edges don't implement tier stamping** — `mnemos-store` does not call `tierTag()`; all memories land untiered. Only the MCP tool wrapper `jarvis_remember` adds tier tags. | **HIGH** | MNEMOS | `mnemos-store` edge should read a `tier:` param and stamp the tag |
| 2 | **JLTM has no active recall path** — JSTM→JLTM→JATM promotion exists in `jarvis_jmms` but JLTM itself has no dedicated query function. The consolidated tier is the default but nothing actively surfaces it. | **MEDIUM** | JMMS | Build a `mnemos-recall` tier filter or document the existing path |
| 3 | **`tags` column origin untracked** — the initial migration `20260524_create_mnemos_memories.sql` doesn't add `tags`. It must have been added in an untracked migration. | **LOW** | MNEMOS | Add a named migration for the `tags` column addition |
| 4 | **Embedding dimension churn** — 768 → 1536 → 1024 across migrations. Current state is stable (1024) but the migration history is confusing. | **LOW** | MNEMOS | Document the final dimension in JMMS-SPEC |

---

## Phase Gate

✅ `intake/audit-phase-4-memory.md` written — Phase 5 can proceed.
