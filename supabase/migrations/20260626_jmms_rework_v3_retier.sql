-- JMMS Rework v3 — Re-tier all existing Supabase memories
-- Based on IMPL-JMMS-0001 §8 (Birth Tier Rules, retrospective).
-- Every row is classified by its source_type and assigned the tier it *should*
-- have been born into. This is a one-time correction, not a fold — the rows'
-- existing text and identity are preserved; only their JMMS metadata changes.
--
-- Logic:
--   JSTM (session-born ephemeral): speak_input, speak_output, council_trace,
--     guard_check, companion_exchange, node_message_in, raven_insight, navigation
--   JHTM (compressed historical): session_summary, continuity_digest, history
--   JLTM (durable knowledge): identity_summary, raven_profile, mcp_memory, decision,
--     jarvis_identity, identity_growth_*, governance, mission, milestone, memory,
--     identity_seed, identity_keel, identity_growth_ayre, deployment, raven_insight
--   JATM (immutable keel): jitm_pin (the 4 foundational pins)
--
--   jstm_sub: hot (speak_input/output/council_trace), warm (all other JSTM)
--   memory_scope: session (JSTM), project (JHTM/JLTM), companion (JATM)
--   temperature: hot (JSTM HOT), warm (JSTM WARM/JLTM/JATM), cool (JHTM)
--   activation_score: 60 (JSTM HOT), 80 (all others — KRONOS fold will decay)

BEGIN;

-- ========================================================================
-- PHASE 1: Set memory_tier by source_type
-- ========================================================================

UPDATE public.mnemos_memories
SET memory_tier = CASE
    WHEN source_type IN (
      'speak_input','speak_output','council_trace','guard_check',
      'companion_exchange','node_message_in','raven_insight',
      'navigation','diagnosis'
    ) THEN 'jstm'

    WHEN source_type IN (
      'session_summary','continuity_digest','history','session_log'
    ) THEN 'jhtm'

    WHEN source_type IN (
      'identity_summary','raven_profile','mcp_memory','decision',
      'jarvis_identity','identity_growth_jarvis','identity_growth_ayre',
      'governance','mission','milestone','memory',
      'identity_seed','identity_keel','deployment',
      'conversation','e2e_test'
    ) THEN 'jltm'

    WHEN source_type = 'jitm_pin'
    THEN 'jatm'

    ELSE 'jltm'  -- catch-all: anything not listed goes to JLTM
  END
WHERE memory_tier = 'jltm';  -- only touch rows seeded as jltm by v1 migration

-- ========================================================================
-- PHASE 2: Set jstm_sub for JSTM rows
-- ========================================================================

UPDATE public.mnemos_memories
SET jstm_sub = CASE
    WHEN source_type IN ('speak_input','speak_output','council_trace')
    THEN 'hot'
    ELSE 'warm'
  END
WHERE memory_tier = 'jstm'
  AND jstm_sub IS NULL;

-- ========================================================================
-- PHASE 3: Set memory_scope by tier
-- ========================================================================

UPDATE public.mnemos_memories
SET memory_scope = CASE
    WHEN memory_tier = 'jstm'  THEN 'session'
    WHEN memory_tier = 'jhtm'  THEN 'project'
    WHEN memory_tier = 'jltm'  THEN 'project'
    WHEN memory_tier = 'jatm'  THEN 'companion'
    ELSE 'project'
  END
WHERE memory_scope = 'project';  -- only touch v1-seeded rows

-- ========================================================================
-- PHASE 4: Set temperature by tier + jstm_sub
-- ========================================================================

UPDATE public.mnemos_memories
SET temperature = CASE
    WHEN jstm_sub = 'hot' THEN 'hot'
    WHEN memory_tier = 'jhtm' THEN 'cool'
    ELSE 'warm'
  END
WHERE temperature = 'warm';  -- only touch v1-seeded rows

-- ========================================================================
-- PHASE 5: Set activation_score by tier
-- ========================================================================

UPDATE public.mnemos_memories
SET activation_score = CASE
    WHEN jstm_sub = 'hot'    THEN 60  -- session-hot: warm but not keel-hot
    WHEN memory_tier = 'jhtm' THEN 40  -- already compressed once
    ELSE 80
  END
WHERE activation_score = 80;  -- only touch v1-seeded rows (all were 80)

-- ========================================================================
-- PHASE 6: Set domain (null = companion-scope; populate from tags if useful)
-- ========================================================================

-- domain remains null for JATM (companion-scope keels have no domain)
-- domain remains null for most existing rows (they carry no domain metadata)
-- Future writes will populate domain from the session context

COMMIT;

-- ========================================================================
-- Verification query (run after migration)
-- ========================================================================

SELECT
  memory_tier,
  jstm_sub,
  memory_scope,
  temperature,
  activation_score,
  count(*) as rows
FROM public.mnemos_memories
GROUP BY 1, 2, 3, 4, 5
ORDER BY
  CASE memory_tier
    WHEN 'jitm' THEN 1
    WHEN 'jstm' THEN 2
    WHEN 'jhtm' THEN 3
    WHEN 'jltm' THEN 4
    WHEN 'jatm' THEN 5
    ELSE 6
  END,
  jstm_sub NULLS LAST,
  memory_scope,
  temperature,
  activation_score;
