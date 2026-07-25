# 1. OBJECTIVE

Perform a complete system audit of JARVIS — architecture layer, all 27 god systems, MCP/edge runtime, memory subsystem, and governance/intake workflow — and produce a per-system verdict (keep / rework / archive / build). The audit must be **bounded and phase-gated** so it cannot loop or hang: each phase produces a named output, the next phase consumes only that output, and the planner never re-reads the whole repo.

# 2. CONTEXT SUMMARY

**JARVIS architecture (known state):**
- **Yggdrasil / JFS / JNL / JSE** — governed in `core/JarvisMain/yggdrasil/`: tools (`validate.py`, `seed.py`, `grimoire.py`, `dex.py`, `autosort.py`, `extend.py`), registries (`lal/master-index.json`, `lal/address-registry.json`, `lal/tag-registry.json`, `lal/graph.json`), specs (`JFS-SPEC.md`, `jnl-grammar.md`, `jse-schema.md`, `JSS-SPEC.md`, `JMMS-SPEC.md`)
- **Council** — defined in `core/supabase/functions/jarvis-mcp/council.ts`: TIERS (T0–T9, 27 systems), TIER_WEIGHT, ROLE, COMMENTARY set, LENS_SIGNALS, deliberation logic
- **GRIMOIRE** — `core/JarvisMain/yggdrasil/lal/GRIMOIRE.md` (230 governed objects, 351 edges, 9 domains) + `core/JarvisMain/yggdrasil/tools/grimoire.py` (generator)
- **27 God Systems** — 28 README contracts under `core/JarvisMain/god_systems/T*_*/README.md`; council.ts is the canonical runtime implementation
- **Forbidden edges** (CLAUDE.md + council.ts): `SKADI→AEGIS`, `DANTE→SKADI`, `JANUS→SKADI`, `LOKI→HADES`
- **Active/dormant** (GRIMOIRE catalog): CHAOS, POSEIDON, HADES, HERMES = INACTIVE; all others ACTIVE
- **MCP connector** — `core/supabase/functions/jarvis-mcp/index.ts` (Hono + MCP SDK, 30+ tools registered); Supabase edge functions under `core/supabase/functions/`
- **Memory** — MNEMOS (`core/supabase/functions/mnemos-*`), JMMS tiers (`jitm`/`jstm`/`jltm`/`jatm`), chaos state in `memory/chaos/` (seed.json excluded from git, `session_sync.py`)
- **Governance** — `dex_events` (Supabase live), `jd_entries` (git-first canon), `council.ts` (council vote/review/deliberation)

**The "stuck" problem:** A monolithic single-pass audit re-reads the entire repo on every sub-check, causing the planning/agent loop to exceed context limits or appear to hang. The fix is **phase-gated output-first audit**: each phase writes its findings to a named artifact, the next phase reads only that artifact.

# 3. APPROACH OVERVIEW

Run 6 independent audit phases in sequence. Each phase:
1. Reads only the files it needs (scoped, not full-repo)
2. Writes its findings to `memory/intake/audit-phase-N-*.md`
3. Produces a structured verdict table as its final line

The 6 phases map directly to the 6 requested audit categories. A final synthesis phase reads all 6 artifacts and produces the per-system verdict table.

**Why this avoids stuck:**
- Each phase is a bounded, single-pass read → no re-scanning
- Output is a file, not a held context slot — always verifiable
- The synthesis phase is the only one that reads broadly, and it reads only the 6 output files

# 4. IMPLEMENTATION STEPS

## Phase 1 — Architecture Audit
**Goal:** Verify Yggdrasil, JFS, JNL, JSE, Council, GRIMOIRE are consistent and complete.
**Method:** Read specs + tool output files, run `grimoire.py` card on root objects, check graph edges.
**Reference:** `core/JarvisMain/yggdrasil/`, `core/supabase/functions/jarvis-mcp/council.ts`

1. `jarvis-grimoire` → boot menu → capture object count + orphan count
2. `jarvis-dex {status:ACTIVE}` → count active ARCH/IMPL objects
3. Run `validate.py` → capture JGLF violations (orphans, broken parents, empty related)
4. Read `JFS-SPEC.md` → verify JNS/JNL/JSL/JMS/JSS/JMMS all present
5. Read `jnl-grammar.md` → verify address grammar matches actual entries
6. Read `council.ts` → verify TIERS has all 27, COMMENTARY set is correct
7. Read `lal/GRIMOIRE.md` header → verify generated timestamp, object/edge counts
8. Write `memory/intake/audit-phase-1-architecture.md` with:
   - Object count from GRIMOIRE vs `jd/entries/*.md` count (should match)
   - Orphan count from JVE vs GRIMOIRE orphan lens
   - JNL grammar violations
   - Council TIERS count (should be 27)
   - Forbidden edges presence in code
   - Per-subsystem status: Yggdrasil / JFS / JNL / JSE / Council / GRIMOIRE

## Phase 2 — God Systems Audit
**Goal:** Verify all 27 god system contracts exist, forbidden edges are enforced, and active/dormant state is correct.
**Method:** Read each T*_*/README.md, cross-reference council.ts TIERS, verify forbidden edge enforcement.
**Reference:** `core/JarvisMain/god_systems/`, `core/supabase/functions/jarvis-mcp/council.ts`, `core/supabase/functions/jarvis-respond/router.ts`

1. List `core/JarvisMain/god_systems/T*_*/README.md` → should be exactly 28 (including README.md at root)
2. For each tier T0–T9: count READMEs, confirm matches council.ts TIERS
3. Read `council.ts` FORBIDDEN (grep for "forbidden" or check router.ts edge list) → confirm 4 edges: SKADI→AEGIS, DANTE→SKADI, JANUS→SKADI, LOKI→HADES
4. Verify INACTIVE systems from GRIMOIRE catalog: CHAOS, POSEIDON, HADES, HERMES = 4 dormant
5. Read `chaos_seed.example.json` → compare forbidden edges with council.ts (note: chaos_seed.json is local-only, do NOT read it)
6. Write `memory/intake/audit-phase-2-godsystems.md` with:
   - All 27 systems confirmed (yes/no per system)
   - Forbidden edge enforcement status (enforced in code / documented only / missing)
   - Active/dormant table from GRIMOIRE vs council.ts TIERS
   - Per-system verdict: KEEP (contract + runtime match) / REWORK (mismatch) / DORMANT (intentional)

## Phase 3 — MCP + Tools Audit
**Goal:** Verify MCP connector, all Supabase edge functions, and tool registrations are consistent and deployed.
**Method:** Read index.ts tool registrations, list edge functions, cross-reference with GRIMOIRE verbs page.
**Reference:** `core/supabase/functions/jarvis-mcp/index.ts`, `core/supabase/functions/`, `core/JarvisMain/Connectors/JarvisMCPSupabase/`

1. Count `registerTool` calls in `jarvis-mcp/index.ts` → tool count
2. List `core/supabase/functions/*/index.ts` → edge function list
3. Read `core/JarvisMain/Connectors/JarvisMCPSupabase/tools/` → doc mirrors for each tool
4. Cross-reference: for each tool in index.ts, verify a corresponding doc mirror exists
5. Read `jarvis-dex/jfs.ts` → verify JNL enforcement (VALID_DOMAINS, JGLF checks)
6. Check `router.ts` → verify ODIN routing + AEGIS gating wired
7. Write `memory/intake/audit-phase-3-mcp-tools.md` with:
   - Tool count: registered in index.ts vs documented in connectors
   - Edge function inventory (function name + purpose + last modified)
   - Undocumented tools (registered but no doc mirror)
   - Unregistered tools (doc mirrors but no registration)
   - Wire status: ORACLE→ODIN→SKADI→MNEMOS path verified (yes/no)

## Phase 4 — Memory Audit
**Goal:** Verify MNEMOS, JMMS tiers, session log, and chaos state are consistent.
**Method:** Read mnemos edge functions, check JMMS tiering in index.ts, verify chaos exclusion, audit session_sync.py.
**Reference:** `core/supabase/functions/mnemos-*/`, `core/supabase/functions/jarvis-mcp/index.ts`, `memory/chaos/session_sync.py`

1. List `core/supabase/functions/mnemos-*` → confirm: store, recall, search, embed
2. Read `jarvis-mcp/index.ts` JMMS_TIERS → verify 4 tiers: jitm, jstm, jltm, jatm
3. Verify `tierTag()` and `withTier()` functions handle all 4 tiers correctly
4. Check `memory/chaos/` exclusion: confirm chaos_seed.json, session_log.json, prometheus_log.json are in .gitignore
5. Read `session_sync.py` → verify session start/end logging works
6. Verify `memory/mnemos/` Supabase table schema (from migrations): content, tags, tier, source columns
7. Write `memory/intake/audit-phase-4-memory.md` with:
   - MNEMOS functions: which exist, which are wired to MCP
   - JMMS tier coverage (all 4 tiers implemented / partial)
   - Chaos local state: what's tracked, what's excluded from git
   - Session log: what gets written, retention
   - Per-component verdict: MNEMOS / JMMS / session_log / chaos

## Phase 5 — Intake / Governance Audit
**Goal:** Verify workflow, dex_events, and audit trails are wired correctly.
**Method:** Read governance specs, check dex_events table schema, verify council integration.
**Reference:** `core/JarvisMain/Architecture/`, `core/supabase/migrations/`, `core/supabase/functions/jarvis-respond/`

1. List `core/supabase/migrations/*` → identify: dex_events, jd_entries, jd_proposals, jip_entries schemas
2. Read `core/JarvisMain/Architecture/specs/dex-council-bridge.md` → verify domain→authority mapping
3. Check `jarvis-respond/router.ts` → verify councilVote called in the pipeline
4. Read `jarvis-respond/aegis.ts` → verify Gold Law gates (GL2, GL5, GL6, GL7, GL10, GL12)
5. Verify `governed workflow`: intake→context→implement→verify→log→commit→sync→recycle (CLAUDE.md)
6. Check `jarvis-action/index.ts` for GRIMOIRE integration (grep for GRIMOIRE)
7. Write `memory/intake/audit-phase-5-governance.md` with:
   - dex_events: schema, what writes it, what reads it
   - jd_entries: git-first canon verified (yes/no)
   - council bridge: domain→authority mapping completeness
   - Gold Law coverage in AEGIS
   - Workflow step coverage

## Phase 6 — Synthesis
**Goal:** Produce per-system verdict table from all 5 phase outputs.
**Method:** Read all 5 `memory/intake/audit-phase-*-*.md` files, produce verdict table.
**Reference:** All phase outputs

1. Read `memory/intake/audit-phase-1-architecture.md`
2. Read `memory/intake/audit-phase-2-godsystems.md`
3. Read `memory/intake/audit-phase-3-mcp-tools.md`
4. Read `memory/intake/audit-phase-4-memory.md`
5. Read `memory/intake/audit-phase-5-governance.md`
6. Write `memory/intake/audit-synthesis.md` with:
   - **Verdict table** — one row per system/subsystem: KEEP / REWORK / ARCHIVE / BUILD
   - **Critical gaps** — anything that must be addressed before next session
   - **Next actions** — one sentence per REWORK/ARCHIVE/BUILD item

# 5. TESTING AND VALIDATION

Each phase is validated by its output file existing and containing:
- A **status line** (`✓ PHASE-1 COMPLETE: N objects, N orphans, N violations`)
- A **per-subsystem status table** (subsystem | status | notes)
- A **phase-gate** that the next phase can assert exists before reading

**Phase gate check (between phases):**
```
# Before Phase 2: assert memory/intake/audit-phase-1-architecture.md exists
# Before Phase 3: assert memory/intake/audit-phase-2-godsystems.md exists
# ...
```

**Final validation:**
- `memory/intake/audit-synthesis.md` exists with a verdict table
- Every row in the verdict table has: system name, verdict, and one-sentence rationale
- No row is marked REWORK or BUILD without a next-action in the "Next actions" section
- The file is committed to git (audit trail preserved)
