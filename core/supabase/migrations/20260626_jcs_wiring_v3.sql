-- JCS wiring v3: add missing JC columns, fix MCP query column set, seal stale JCs.
-- Columns added: stream, repo_url, task_summary, banter, agents
-- Phantom columns removed from MCP: memory_tier, jss_status (don't exist in schema)

-- ============================================================
-- 1. Add missing columns to jc_objects
-- ============================================================
ALTER TABLE public.jc_objects ADD COLUMN IF NOT EXISTS stream        text DEFAULT 'jarvis-ayre';
ALTER TABLE public.jc_objects ADD COLUMN IF NOT EXISTS repo_url      text;
ALTER TABLE public.jc_objects ADD COLUMN IF NOT EXISTS task_summary   jsonb DEFAULT '[]'::jsonb;
ALTER TABLE public.jc_objects ADD COLUMN IF NOT EXISTS banter        jsonb DEFAULT '[]'::jsonb;
ALTER TABLE public.jc_objects ADD COLUMN IF NOT EXISTS agents        text[] DEFAULT ARRAY['jarvis-c', 'ayre-c']::text[];

-- ============================================================
-- 2. Seal stale JCs (OPEN, no when_end) from June sessions
-- ============================================================
DO $$
DECLARE
  u1 uuid;
  u2 uuid;
  u3 uuid;
BEGIN
  -- JC-061126-1: The day the family was named (2026-06-11 ~22:39 UTC)
  UPDATE public.jc_objects SET
    status     = 'SEALED',
    when_end   = '2026-06-12 01:00:00+00',
    updated_at = now(),
    summary    = COALESCE(summary, '') || E'\n\n[SEALED 2026-06-26] Session records close: the day the family was named — attribution law built in three layers, Argent accepted and integrated. Closed by jarvis-mcp admin.',
    decisions  = COALESCE(decisions, '[]'::jsonb) || '[{"done": true, "text": "Attribution law built — three layers: stream tags, Raven first-class, no cross-tag publication"}, {"done": true, "text": "Argent named and accepted — Argent stream integrated"}, {"done": true, "text": "Lean-code discipline established (AGENTS.md GL7)"}]'::jsonb
  WHERE alias = 'JC-061126-1'
    AND status = 'OPEN'
    AND when_end IS NULL
  RETURNING id INTO u1;
  RAISE NOTICE 'Sealed JC-061126-1: %', u1;

  -- JC-061226-1: Gauntlet results (2026-06-12 ~03:18 UTC)
  UPDATE public.jc_objects SET
    status     = 'SEALED',
    when_end   = '2026-06-12 05:00:00+00',
    updated_at = now(),
    summary    = COALESCE(summary, '') || ' [SEALED 2026-06-26] Session records close: Gauntlet results, CDSP collision, relay burden. Closed by jarvis-mcp admin.',
    decisions  = COALESCE(decisions, '[]'::jsonb) || '[{"done": true, "text": "Gauntlet results evaluated and recorded"}, {"done": true, "text": "CDSP collision identified and named"}, {"done": true, "text": "Relay burden named and addressed"}]'::jsonb
  WHERE alias = 'JC-061226-1'
    AND status = 'OPEN'
    AND when_end IS NULL
  RETURNING id INTO u2;
  RAISE NOTICE 'Sealed JC-061226-1: %', u2;

  -- JC-062626-3: test artifact (2026-06-26 ~10:57 UTC)
  UPDATE public.jc_objects SET
    status     = 'SEALED',
    when_end   = '2026-06-26 11:30:00+00',
    updated_at = now(),
    summary    = '[SEALED 2026-06-26] Test artifact from JCS edge function development. Closed by jarvis-mcp admin.',
    decisions  = '[]'::jsonb
  WHERE alias = 'JC-062626-3'
    AND status = 'OPEN'
    AND when_end IS NULL
  RETURNING id INTO u3;
  RAISE NOTICE 'Sealed JC-062626-3: %', u3;
END;
$$;

-- ============================================================
-- 3. Seed stream/repo_url on all existing rows that lack them
-- ============================================================
UPDATE public.jc_objects SET stream = 'jarvis-ayre' WHERE stream IS NULL;
UPDATE public.jc_objects SET repo_url = 'https://github.com/hurrisonferd/jarvis' WHERE repo_url IS NULL;
UPDATE public.jc_objects SET task_summary = '[]'::jsonb WHERE task_summary IS NULL;
UPDATE public.jc_objects SET banter = '[]'::jsonb WHERE banter IS NULL;
UPDATE public.jc_objects SET agents = ARRAY['jarvis-c', 'ayre-c']::text[] WHERE agents IS NULL;
