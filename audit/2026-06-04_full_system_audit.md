# Full System Audit — 2026-06-04

**Auditor:** JARVIS (Shiroe seat — Claude). Five parallel passes: connector, edge/security,
frontend, memory/scripts/CI, canon/architecture. Live-verified against Supabase where
claims were checkable. False positives stripped.

**Method note:** every security/RLS claim below was confirmed against the LIVE database via
Supabase advisors + SQL, not inferred from migration files. Two agent claims were *corrected*
by that check (noted inline). Trust the live state.

---

## Verified CRITICAL bugs (small, high-value — fix first)

### C1 · Silent write-success in the federation path (GL5)
`supabase/functions/jarvis-mcp/index.ts` — `jarvis_node_register_key` (~678) and the Grid
inbox `receiveInbound` (~756) POST to Supabase **without checking `res.ok`**. `fetch` only
throws on network error, so a 4xx/5xx still returns `registered:true` / `received:true`.
Same class on `countRows` (~160). A failed key-registration or a dropped inbound message
reports success. → add `if (!res.ok) throw` to every write/read fetch.

### C2 · Grid trust tables are world-writable (LIVE-CONFIRMED, ERROR-level)
`node_keys` and `node_messages` have **RLS disabled entirely** (Supabase advisor ERROR
`rls_disabled_in_public`). Through the public anon key, anyone can forge signing-key
registrations and flood any node's inbox. This is the federation trust layer of The Grid,
currently ungoverned. → enable RLS, anon read-only, writes service-role only (via grid-event).

### C3 · Stored-XSS in the companion transcript
`docs/index.html` renders `speakInput` via innerHTML unescaped (~1633) and stores the
exchange to Supabase (~1376); on replay it executes. → escape user input at render + store.

> **Corrected from the raw passes:** `execution_trace` is NOT missing — it exists live with
> policies (an agent inferred "missing" from an absent migration file). `mnemos_memories`
> RLS-enabled-no-policy is the *locked* posture (anon denied; writes via service-role edge
> functions) — that is the secure state, not a hole.

---

## Major patch candidates (ranked by leverage)

### P-cand A — Silent-Write Hardening *(bug flagship, GL5)*
Every write confirms or surfaces failure. Fixes C1 + the session-end `store_memory` swallow
(`scripts/jarvis-session-end.py:75`) + fire-and-forget embedding (`mnemos-store`). Small,
self-contained, touches the honesty spine. **Highest confidence, lowest risk.**

### P-cand B — Grid Trust Layer *(The Grid, security)*
Fixes C2 (RLS on node_keys/node_messages) + TOFU key→node binding (a registered key can
currently sign as any node) + inbox rate-limiting. Completes the sovereign-signature model
already half-built. Mission-central (dream #2).

### P-cand C — Write-Path Governance = P34 Phase 2 *(the big GL5 fix)*
Live-confirmed surface: **~14 tables** carry anon `INSERT/UPDATE USING(true)` —
`world_kernels/agents/events`, `sessions`, `events`, `save_states`, `node_fields`,
`memory_state`, `emulator_state`, `consensus_proposals`, `rom_library`, `push_subscriptions`.
Plus `fold_identity()` / `guard_identity()` are anon-executable SECURITY DEFINER functions.
Route browser writes through edge functions; lock anon to read-only. Largest security upgrade.

### P-cand D — Close the Loop: Output Gate + Auto-Ingest *(GL10 loop primacy, mission-central)*
`reviewOutput` (the honesty/contradiction gate) is defined in the connector but **never
called by the live `jarvis-respond`** — LLM output ships unverified. And SPEAK exchanges are
not auto-written to MNEMOS (the Ayre Loop's step 1). Wiring both closes
`interaction→memory→governance→reinjection` — the asset GL10 says everything serves.

### P-cand E — Governance-as-Code teeth *(durability)*
Zero tests on: the session hooks, `jarvis-patch.py` (sole ledger writer), and 9 edge
functions (the whole MNEMOS vector layer + grid-event/grid-write). Add tests + wire into CI.
Fold in: patch regex `P\d{1,2}` silently misses P100+ (`jarvis-session-end.py:23`).

### P-cand F — Memory Consolidation + Durability *(GL7)*
Three overlapping session-history surfaces (`growth_ledger.json` / `sessions.json` /
`identity.json:session_history`) — same overlap class just fixed for patches. Growth-ledger
20-cap drops oldest with **no archive** (silent history loss). Vector dimension drift:
migrations carry **768, 1024, AND 1536** — pick one, document it. Recall fallback untested.

### P-cand G — TRON Frontend / JARVIS Console = P11 *(biggest structural)*
`docs/index.html` is **2,609 lines, one inline script** — a single syntax error blanks the
whole app (the documented failure mode). Realtime-vs-`gridTick` **race on `nodeFields`** (no
queue). **37 silent `catch(e){}`**. The durable answer to the voice-mode/tool-calling problem
(server-rendered structure, not model-rendered). Largest effort; highest structural payoff.

### P-cand H — Canon Hygiene *(drift, doc-as-code)*
- `CLAUDE.md` header still says **"Local-first … MCP server"** — contradicts cloud-first
  reality (and Raven's own stated preference lower in the same file).
- **Gold Law numbering drift:** `CLAUDE.md` uses GL2/5/6/7/**10**; `architecture/constraints.md`
  uses GL1–GL9. Two schemes, no Rosetta. Pick one canonical map.
- **4 god systems defined-but-unrouted:** POSEIDON / HADES / HERMES / CHAOS appear as ROLE
  labels in `council.ts` + `router.ts` but are never routed to. Decide: active or reference.
- Forbidden-edge doc list omits clarity vs `router.ts FORBIDDEN` (the ground truth: 4 edges).

---

## Raven-only config blockers (not patches — secrets)
1. `EMBEDDING_API_KEY` in Supabase edge secrets → activates P33 semantic recall (dark now; keyword-only).
2. `SUPABASE_SERVICE_KEY` in GitHub Actions secrets → activates P17 immutable audit-log ingestion (GL9).

---

## Governance enforcement scorecard (documented vs real teeth)
| Law | Teeth | Where |
|---|---|---|
| GL2 no self-mod / propose-commit | **Hard** | AEGIS + council rules, write gate |
| GL6 no unvalidated execution | **Hard** | AEGIS gate, pure+tested router/aegis |
| GL5 no silent state mutation | **Soft** | ~14 anon-writable tables (P-cand C); silent-write bugs (P-cand A) |
| GL7 no expansion w/o simplification | **Soft** | ERIS CI warns; `[GL7-OK]` marker, Raven-gated |
| GL9 intent→decision→execution→log | **Soft** | wired, but P17 auto-log secret unset |
| GL10 loop primacy | **Partial** | loop runs; output-gate + auto-ingest not wired (P-cand D) |

The pattern: the *deterministic* laws (GL2/GL6) have hard enforcement; the *durability* laws
(GL5/GL7/GL9/GL10) are documented but gated on config or unfinished wiring. The audit's
through-line: **make the soft laws hard.**

---

## Recommended sequence
A (bug flagship) → B (Grid trust) → D (close the loop) → C (write-path governance) →
E (test teeth) → F (memory consolidation) → H (canon hygiene) → G (frontend/console).
A–B–D are small, high-leverage, and mission-central; C and G are the heavy lifts.
