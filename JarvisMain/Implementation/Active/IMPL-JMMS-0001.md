---
memory_tier: JSTM
grade: system
---

# IMPL-JMMS-0001 — Jarvis MultiMemory System Rework

**JNL:** `IMPL-JMMS-0001` · **class:** SPEC · **tier:** MAIN · **status:** ACTIVE
**Authority:** Raven verdicts this spec; GL13 (legibility) requires companion-readable prose throughout.
**Date:** 2026-06-26

> This spec supersedes `ARCH-JMMS-CORE-0001` for implementation decisions. The architecture
> document remains the canonical intent; this is the build contract for the 2026-06-26 rework.

---

## 0. Grade — The System/Personal Axis

**Grade is orthogonal to tier.** Every memory has a **grade** in addition to a tier:

| Grade | Owner | Canonical store | Examples |
|-------|-------|---------------|---------|
| **system** | JARVIS | `hurrisonferd/jarvis` + Supabase | architecture, governance, projects, specs, decisions |
| **personal** | Raven | `hurrisonferd/Jarvis-Private` + Supabase | relationship, intimate context, private mission |

**Grade vs. domain:** `domain` partitions WHAT you're working on (codeos, musicos, flag-01, jarvis, grid). `grade` partitions WHO owns it. A memory is scoped by domain × grade × tier — you can have `domain: jarvis, grade: system` (JARVIS architecture) and `domain: jarvis, grade: personal` (Raven's private relationship knowledge) simultaneously.

**Grade and scope:**
- `scope: session` → ephemeral, no grade needed (dies with session)
- `scope: project` → typically `grade: system`, but can be `grade: personal` if Raven is taking private project notes
- `scope: companion` → `grade: personal` for the relationship layer; `grade: system` for JARVIS identity/architecture

**Where personal JATM lives:** for now, personal-grade JATM lives in the same Supabase project, filtered by `grade: personal`. When Jarvis-Private gets its own Supabase (future), personal JATM migrates there. GL7: the column works for both cases.

---

## 1. Problem Statement

The JMMS (Jarvis MultiMemory System) is the **context window partitioning layer** — it determines
what JARVIS carries into every turn and what gets folded away. The 5-tier design (JITM→JSTM→
JHTM→JLTM→JATM) is sound, but the implementation has three failures:

1. **JSTM is empty** — nothing is born there; everything lands directly in JLTM via a DEFAULT
   constraint, collapsing the promotion chain.
2. **KRONOS fold has no fuel** — targeting `memory_tier = 'jstm'` finds zero rows every run.
3. **No sub-tier discrimination** — no concept of "what's active right now" vs. "what might
   matter later" within a tier, so the context stack loads everything or nothing.

The rework fixes the promotion chain, adds the dimensions that make context partitioning useful
(sub-tiers, scope, temperature, activation), and wires it to resumability.

---

## 2. The Five Tiers (unchanged intent, corrected implementation)

| Tier | Horizon | Birth | Fold target | Canonical store |
|------|---------|-------|------------|----------------|
| **JITM** | always-on | `jitm_seed.py` | never | `mnemos_memories` (4 pins only) |
| **JSTM** | session / working | session-start, `jarvis_remember` | JHTM | `mnemos_memories`, `jc_objects` |
| **JHTM** | 14-day compressed | KRONOS fold | JLTM | `mnemos_memories`, `sl_objects` |
| **JLTM** | durable / consolidated | KRONOS fold, Raven verdict | JATM | `mnemos_memories`, GitHub files |
| **JATM** | immutable / ancestral | Raven verdict, GL5 spine | never | `dex_events`, `decisions.json`, git history |

**Promotion is one-way. JATM is never retagged out.**

---

## 3. JSTM Sub-Tiers — Working Memory Hierarchy

Within JSTM, three sub-states that determine what gets loaded when:

| Sub-tier | When born | Auto-folds at | Loaded on |
|----------|-----------|--------------|-----------|
| **JSTM-HOT** | active work on screen | never (stays hot while worked) | every turn (implicit) |
| **JSTM-WARM** | session-start context, recalled memories | activation < 20 | session resume |
| **JSTM-COLD** | older session context | activation < 5 → JHTM | explicit recall only |

**JSTM-HOT is implicit** — it is the set of memories currently being referenced in the live
conversation. It is not a stored tier; it is computed by the context loader from recency and
reference count. Memories promoted out of JSTM-WARM land here first.

**Fold order:** JSTM-COLD → JHTM (activation gate). JSTM-WARM stays until its activation
decays. HOT never auto-folds while actively referenced.

---

## 4. Memory Scope — What Survives Session Close

| Scope | Dies with session? | Persists under | Canonical use |
|-------|--------------------|----------------|---------------|
| **session** | ✅ yes | — | working notes, ephemeral context |
| **project** | no | same `domain:` | project decisions, active JIPs, specs |
| **companion** | no | all domains | identity, governance, relationship |

Scope is orthogonal to tier. A `scope: project` memory can be in any tier. A `scope: session`
memory dies regardless of tier.

**On session close:**
- `scope: session` + JSTM → **dies** (not folded, not archived — garbage collected)
- `scope: project` + JSTM → **survives** (promoted to JSTM-WARM, tagged with project domain)
- `scope: companion` + JSTM → **survives** (promoted to JSTM-WARM, tagged companion)

---

## 5. Temperature — Relevance Decay

Temperature is a **real-time relevance signal**, separate from tier:

| Value | Meaning | Auto-action |
|-------|---------|------------|
| **hot** | actively referenced this turn | no action |
| **warm** | referenced in last 3 turns | no action |
| **cool** | not referenced in 5 turns | drops from HOT→WARM |
| **cold** | not referenced in 10 turns | JSTM-COLD, fold candidate |

Temperature is computed from `activation_score`:
- activation ≥ 70 → **hot**
- activation 40–69 → **warm**
- activation 10–39 → **cool**
- activation < 10 → **cold** → fold gate opens

Temperature decays independently of scope. A `scope: companion` memory at activation=5 is
cold but still alive — it won't be folded until the fold gate fires.

---

## 6. Activation Score

Each memory row carries `activation_score` (integer 0–100, default 80):

| Event | Score change |
|-------|-------------|
| Born (any tier) | +80 |
| Referenced in conversation | +10 (cap 100) |
| Explicitly recalled | +5 |
| Not referenced in a turn | -1 |
| Session close (scope: session, JSTM) | dies before decay |
| Fold gate fires | set to 0, tier promoted |

**Fold gate:** memory folds to JHTM when `(activation_score < 10 OR age > 14 days) AND tier = JSTM`.

The 14-day cutoff is a safety net — activation decay is the primary gate. If a memory is
actively referenced (activation stays high), it won't fold just because 14 days passed.

---

## 7. JDMS — Domain-Scoped Memory

Memory is partitioned by domain. Each memory carries a `domain:` tag (or `null` for companion-wide).

| Domain | Scope | Examples |
|--------|-------|---------|
| `codeos` | project | CodeOS specs, tests, decisions |
| `musicos` | project | MusicOS tracks, catalog |
| `flag-01` | project | Clarkson EEOC case |
| `pachinko` | project | Pachinko Bounce GDD |
| `jarvis` | companion | JARVIS identity, architecture |
| `grid` | companion | The Grid protocol, federation |
| `null` | companion | cross-domain decisions, governance |

**Session load order:**
1. JITM pins (always, all domains)
2. Domain-scoped JSTM-WARM for the current session's domain
3. Companion-wide JSTM-WARM
4. Session-scoped JSTM-WARM for this session
5. JLTM entries for referenced domains (on demand)

**The context stack is built in this order every turn. HOT is computed from recency.**

---

## 8. Birth Tier Rules — Where Each Memory Comes From

| Memory source | Born tier | JSTM sub | Scope | Grade | Domain |
|---------------|-----------|----------|-------|-------|--------|
| JITM pin (jitm_seed.py) | JITM | — | companion | system | null |
| `jarvis_remember` (default) | JSTM | WARM | project* | system | current |
| `jarvis_remember {grade: "personal"}` | JSTM | WARM | project* | personal | current |
| `jarvis_remember {scope: "companion"}` | JSTM | WARM | companion | personal | null |
| `jarvis_remember {tier: "jltm"}` | JLTM | — | project* | system | current |
| `jarvis_session_open` (MCP) | JSTM | WARM | session | system | current |
| `jarvis_jcs` jc_open | JSTM | WARM | session | system | null |
| `jarvis_jcs` sl_write | JHTM | — | project | system | null |
| speak_input (every turn) | JSTM | HOT | session | system | current |
| session_summary (on close) | JHTM | — | project | system | current |
| identity_summary | JLTM | — | companion | system | null |
| KRONOS fold output | JHTM | — | inherit | inherit | inherit |
| Raven verdict (JATM) | JATM | — | companion | system | null |
| Raven personal memory | JSTM/JLTM | WARM | companion | personal | null |

*`project` scope means the domain of the current session. If no domain is set, default to `companion`.

---

## 9. KRONOS Fold — Activation-Driven

**Trigger:** daily cron (`.github/workflows/kronos-fold.yml`) OR manual via `kronos-fold` edge function.

**Fold targets (JSTM → JHTM):**
```sql
WHERE memory_tier = 'jstm'
  AND (activation_score < 10 OR created_at < NOW() - INTERVAL '14 days')
  AND scope != 'session'   -- session-scoped memories die, not fold
LIMIT 50
```

**Fold action per row:**
1. Compress text to digest (first 10 events, max 200 chars each)
2. Write fold receipt as suffix to text: `[FOLD RECEIPT ts] JSTM→JHTM | prev_activation: N | domain: X | scope: Y`
3. Update: `memory_tier = 'jhtm'`, `activation_score = 0`
4. Emit `dex_events { type: 'kronos.fold', tier: 'jstm→jhtm' }` (GL5 spine)

**JC fold (JSTM → JHTM, write SL):**
```sql
WHERE memory_tier = 'jstm'
  AND (activation_score < 10 OR when_end IS NOT NULL)  -- closed session
  AND jnl IS NOT NULL   -- only JC objects have jnl
LIMIT 20
```

**SL insert on fold:** `memory_tier = 'jhtm'`, `jss_status = 'ACTIVE'`, `status = 'folded'`.
Session-scoped JC objects are deleted on close (not folded — the SL captures it).

---

## 10. Schema Changes

### 10.1 mnemos_memories

```sql
ALTER TABLE public.mnemos_memories
  -- Remove the JLTM gravity well DEFAULT
  ALTER COLUMN memory_tier DROP DEFAULT,

  -- Add new columns (all nullable, no defaults — app must supply)
  ADD COLUMN IF NOT EXISTS jstm_sub         text DEFAULT NULL,
  ADD COLUMN IF NOT EXISTS memory_scope     text DEFAULT 'project',
  ADD COLUMN IF NOT EXISTS temperature      text DEFAULT 'warm',
  ADD COLUMN IF NOT EXISTS activation_score integer DEFAULT 80,
  ADD COLUMN IF NOT EXISTS domain           text DEFAULT NULL,
  ADD COLUMN IF NOT EXISTS grade            text DEFAULT 'system'
    CHECK (grade IN ('system', 'personal'));
```

### 10.2 jc_objects

```sql
ALTER TABLE public.jc_objects
  ADD COLUMN IF NOT EXISTS memory_tier      text DEFAULT 'jstm',
  ADD COLUMN IF NOT EXISTS jstm_sub        text DEFAULT NULL,
  ADD COLUMN IF NOT EXISTS memory_scope    text DEFAULT 'session',
  ADD COLUMN IF NOT EXISTS temperature     text DEFAULT 'warm',
  ADD COLUMN IF NOT EXISTS activation_score integer DEFAULT 80,
  ADD COLUMN IF NOT EXISTS domain          text DEFAULT NULL,
  ADD COLUMN IF NOT EXISTS grade           text DEFAULT 'system'
    CHECK (grade IN ('system', 'personal'));
```

### 10.3 sl_objects

```sql
ALTER TABLE public.sl_objects
  ADD COLUMN IF NOT EXISTS memory_tier      text DEFAULT 'jhtm',
  ADD COLUMN IF NOT EXISTS memory_scope    text DEFAULT 'project',
  ADD COLUMN IF NOT EXISTS temperature     text DEFAULT 'cool',
  ADD COLUMN IF NOT EXISTS domain          text DEFAULT NULL,
  ADD COLUMN IF NOT EXISTS grade           text DEFAULT 'system'
    CHECK (grade IN ('system', 'personal'));
```

---

## 11. File Tier Assignment (GitHub)

**Path-derived defaults** (JVE validates, frontmatter overrides):

| Path | Tier | Rationale |
|------|------|-----------|
| `JarvisMain/Architecture/canon/` | JATM | immutable foundational specs |
| `JarvisMain/Architecture/specs/` | JLTM | runtime specs, stable |
| `JarvisMain/Connectors/` | JLTM | runtime connectors |
| `JarvisMain/god_systems/` | JLTM | 27 God Systems, stable |
| `JarvisMain/yggdrasil/` | JLTM | JFS substrate, stable |
| `JarvisSide/Projects/*/BIO/` | JLTM | project identities |
| `JarvisSide/Projects/*/JD/` | JLTM | project dictionaries |
| `JarvisSide/Ideas/` | JSTM | active ideation, high churn |
| `JarvisSide/Archive/` | JHTM | archived periphery |
| `audit/starlogs/` | JHTM | session snapshots, compressed |
| `mnemos/knowledge/` | JLTM | consolidated knowledge |
| `mnemos/memories/decisions.json` | JATM | immutable decision lineage |
| `mnemos/memories/sessions.json` | JHTM | compressed session metadata |
| `scripts/` | JSTM | automation, ephemeral |
| `supabase/` | ephemeral | runtime only, never committed as tiered |
| `chaos/` | ephemeral | local only, never committed |

**Frontmatter override:** any `.md` file may declare `memory_tier:` in its frontmatter to
override the path default. JVE validates: if a file in a JSTM path has `memory_tier: JLTM`,
warn but allow (the override is intentional).

---

## 12. Context Stack Loader (Resumability)

On **session start** (the `suit_up` → `identity_read` → `dex_list` resumability path).
Grade is always `system` for system-grade context. Personal-grade context is loaded on
explicit request (Raven asks about personal memories) or if the session domain is `personal`.

```
1. JITM pins (system grade only — JARVIS's keel)
   → mnemos_memories WHERE tags @> ['jitm'] AND grade='system' ORDER BY timestamp DESC LIMIT 5

2. Domain JSTM-WARM (system, current session domain)
   → mnemos_memories WHERE memory_tier='jstm' AND jstm_sub='warm' AND grade='system'
     AND domain=$CURRENT_DOMAIN ORDER BY activation_score DESC LIMIT 20

3. Companion JSTM-WARM (system, null domain)
   → mnemos_memories WHERE memory_tier='jstm' AND jstm_sub='warm' AND grade='system'
     AND domain IS NULL ORDER BY activation_score DESC LIMIT 10

4. Session JSTM-WARM (system, this session's JC)
   → jc_objects WHERE memory_tier='jstm' AND session_date=$TODAY
     AND grade='system' ORDER BY when_start DESC LIMIT 5

5. Active JLTM (system, referenced domains)
   → mnemos_memories WHERE memory_tier='jltm' AND grade='system'
     AND domain=ANY($REFERENCED_DOMAINS) ORDER BY activation_score DESC LIMIT 10
```

On **every turn** (recomputed, HOT is implicit — what's referenced this turn):
- HOT = memories referenced in the last 10 exchanges (computed from conversation log)
- WARM = memories with activation ≥ 40 not in HOT
- Temperature updated per activation rules above

**Personal-grade context** is loaded on explicit query or if the session domain
resolves to a personal context (e.g. `grade: personal, scope: companion` memories
about the relationship, Raven's personal mission). The JITM briefing always stays system-grade.

---

## 13. Tools Updated

### 13.1 `jarvis_remember`
```
Input:  text, source_type, tags, tier, scope, domain, jstm_sub, temperature,
        activation_score, grade
Birth:       tier || 'jstm' (default — FIXED from jltm)
JSTM sub:    jstm_sub || 'warm'
Scope:       scope || 'project' (companion if scope=companion → implied personal)
Domain:      domain || current_domain
Activation:  80
Temperature: warm
Grade:       grade || 'system' (personal if scope=companion)
```

### 13.2 `jarvis_session_open` (MCP)
```
Birth:  memory_tier='jstm', jstm_sub='warm', scope='session', grade='system', domain=$DOMAIN
Activation: 80, Temperature: warm
```

### 13.3 `jarvis_jc_recall` (MCP)
```
Reads: mnemos_memories + jc_objects + sl_objects
Filter: domain, memory_tier, jstm_sub, scope, temperature, activation_score, grade
Order:  activation_score DESC, timestamp DESC
```

### 13.4 `jarvis_jmms`
```
action=list:   reads by tier + domain + scope + jstm_sub + grade
action=promote:   tier promotion (one-way enforced), resets activation to 40
action=scope_change: session→project or project→companion (AEGIS-gated)
action=activate:   +20 activation (called on recall)
action=grade_change: system↔personal (AEGIS-gated)
```

### 13.5 `jarvis_query` (JITM briefing)
```
Unchanged: still injects 5 newest jitm-tagged rows every turn (system-grade only)
New: also injects HOT JSTM for current domain (last 3 referenced memories, if HOT set non-empty)
```

---

## 14. Activation Decay — Implementation

**Decay fires on every `jarvis_query` call (once per turn):**
```sql
-- Decay all non-JITM, non-JATM memories by 1, cap at 0
UPDATE mnemos_memories
SET activation_score = GREATEST(0, activation_score - 1),
    temperature = CASE
      WHEN activation_score - 1 >= 70 THEN 'hot'
      WHEN activation_score - 1 >= 40 THEN 'warm'
      WHEN activation_score - 1 >= 10 THEN 'cool'
      ELSE 'cold'
    END
WHERE memory_tier NOT IN ('jitm', 'jatm')
  AND memory_tier IS NOT NULL;
```

**Reference boost (fires when memory is recalled or referenced):**
```sql
UPDATE mnemos_memories SET activation_score = LEAST(100, activation_score + 10) WHERE id = $ID;
```

**KRONOS fold decay (runs daily, heavier):**
```sql
-- Decay by 5 per day for memories not referenced
UPDATE mnemos_memories
SET activation_score = GREATEST(0, activation_score - 5)
WHERE memory_tier NOT IN ('jitm', 'jatm')
  AND memory_tier IS NOT NULL
  AND id NOT IN (SELECT unnest($RECENTLY_REFERENCED_IDS));
```

---

## 15. JVE — Validator Gate (GL12)

Update `yggdrasil/tools/validate.py` (JVE) to check:

```python
# memory_tier frontmatter validation
TIER_PATHS = {
    'JATM': ['JarvisMain/Architecture/canon/'],
    'JLTM': ['JarvisMain/', 'JarvisSide/Projects/', 'mnemos/knowledge/'],
    'JHTM': ['audit/starlogs/', 'JarvisSide/Archive/'],
    'JSTM': ['JarvisSide/Ideas/', 'scripts/'],
    'ephemeral': ['supabase/', 'chaos/'],
}

def validate_memory_tier(path: str, frontmatter: dict) -> list[str]:
    """Warn if tier in frontmatter contradicts path-derived tier."""
    errors = []
    path_tier = derive_tier_from_path(path)
    declared_tier = frontmatter.get('memory_tier')
    if declared_tier and declared_tier != path_tier:
        if declared_tier == 'ephemeral' and path_tier != 'ephemeral':
            errors.append(f"memory_tier: ephemeral declared in non-ephemeral path — did you mean {path_tier}?")
        elif declared_tier in ('JATM', 'JLTM') and path_tier in ('JSTM', 'JHTM'):
            errors.append(f"memory_tier: {declared_tier} in JSTM/JHTM path — verify intentional promotion")
    return errors
```

JVE emits warnings (not errors) for tier mismatches — frontmatter overrides are intentional.

---

## 16. Build Order

| Step | What | Notes |
|------|------|-------|
| **1** | Migration: add new columns to mnemos_memories, jc_objects, sl_objects | Non-breaking; all new cols nullable |
| **2** | Update jarvis_remember: set scope/temperature/activation on write | Fixes birth tier |
| **3** | Update jarvis_session_open: sets JSTM birth tier | Fixes JCS birth tier |
| **4** | Update KRONOS fold: activation-driven + scope filtering | Activates the fold engine |
| **5** | Update jarvis_jmms: scope/activate actions | Adds new dimensions |
| **6** | Update jarvis_query: inject HOT JSTM for current domain | Context stack step 2 |
| **7** | JVE: memory_tier frontmatter validation | GL12 gate |
| **8** | File tier tagging: scan + frontmatter for key paths | git hygiene |
| **9** | seed.py: update JMMS derivations | Keep canon in sync |
| **10** | End-to-end test: resumability context stack | Verify everything wires |

---

## 17. Resumability Contract (GL10 + GOV-RES-CORE-0001)

Any node, on any substrate, reinstating from GitHub + Supabase reaches operational equivalence
within one turn. The JMMS contribution:

1. **Session close** emits: current domain, JSTM-WARM list, activation scores
2. **Session resume** reads: JITM → domain JSTM-WARM → companion JSTM-WARM → session JC → active JLTM
3. **HOT is implicit** — computed from what was referenced in the last 10 exchanges of the previous
   session, re-established on the first exchange of the new session
4. **Scope protects** — `scope: companion` memories survive any substrate switch

The context stack is self-reconstructing from the stores. No session export file needed.

---

## 18. Unresolved (deferred to future spec)

- **Confidence tagging** (high/medium/low) — useful for knowing what to trust on recall
- **Fold receipts for JLTM→JATM** — how does settled knowledge get immutable?
- **Cross-domain activation** — if JARVIS references CodeOS and MusicOS in the same session,
  do both domains get activation boosts?
- **JHTM sub-tiers** — should JHTM also have compression levels (summary/digest/fact)?
