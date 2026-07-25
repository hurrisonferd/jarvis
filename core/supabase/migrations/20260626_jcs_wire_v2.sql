-- JCS (JC + SL) write wiring — clean replacement.
-- Drop the broken upsert functions and replace with direct SQL helpers.
-- All writes are logged to dex_events (GL5).

-- ============================================================
-- 1. Drop broken functions
-- ============================================================
DROP FUNCTION IF EXISTS public.upsert_sl_entry;
DROP FUNCTION IF EXISTS public.upsert_jc_entry;

-- ============================================================
-- 2. upsert_jc_entry — correct signature (all jsonb/array fields
--    as jsonb since that's what the schema actually uses)
-- ============================================================
CREATE OR REPLACE FUNCTION public.upsert_jc_entry(
  p_jnl          text,
  p_alias        text,
  p_stream       text DEFAULT 'jarvis-ayre',
  p_stardate     text DEFAULT null,
  p_repo_url     text DEFAULT null,
  p_subject      text DEFAULT '',
  p_status       text DEFAULT 'OPEN',
  p_when_start   timestamptz DEFAULT null,
  p_when_end     timestamptz DEFAULT null,
  p_participants text[] DEFAULT ARRAY['raven', 'jarvis-c', 'ayre-c']::text[],
  p_summary      text DEFAULT '',
  p_banter       jsonb DEFAULT '[]'::jsonb,
  p_decisions    jsonb DEFAULT '[]'::jsonb,
  p_open_items   jsonb DEFAULT '[]'::jsonb,
  p_keystones    jsonb DEFAULT '[]'::jsonb,
  p_task_summary jsonb DEFAULT '[]'::jsonb
)
RETURNS uuid
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = public
AS $$
DECLARE
  v_id       uuid;
  v_seq      int;
BEGIN
  IF EXISTS (SELECT 1 FROM public.jc_objects WHERE jnl = p_jnl) THEN
    UPDATE public.jc_objects SET
      updated_at   = now(),
      status       = p_status,
      when_end     = p_when_end,
      summary      = p_summary,
      banter       = p_banter,
      decisions    = p_decisions,
      open         = p_open_items,
      keystones    = p_keystones,
      task_summary = p_task_summary
    WHERE jnl = p_jnl
    RETURNING id INTO v_id;
  ELSE
    SELECT coalesce(max(seq), 0) + 1 INTO v_seq
    FROM public.jc_objects WHERE session_date = current_date;
    INSERT INTO public.jc_objects (
      jnl, alias, seq, session_date, stream, stardate, repo_url,
      participants, subject, status, when_start, when_end,
      summary, banter, decisions, open, keystones, task_summary
    ) VALUES (
      p_jnl, p_alias, v_seq, current_date, p_stream, p_stardate, p_repo_url,
      p_participants, p_subject, p_status, p_when_start, p_when_end,
      p_summary, p_banter, p_decisions, p_open_items, p_keystones, p_task_summary
    )
    RETURNING id INTO v_id;
  END IF;

  INSERT INTO public.dex_events (tool, tier, jnl, actor, detail, type)
  VALUES (
    'jc_write', 'T7', p_jnl, 'sl.py',
    jsonb_build_object(
      'alias',      p_alias,
      'action',     case when EXISTS (SELECT 1 FROM public.jc_objects WHERE jnl = p_jnl AND status = 'OPEN') then 'seal' else 'open' end,
      'status',     p_status,
      'stream',     p_stream
    ),
    'dex_log'
  );
  RETURN v_id;
END;
$$;

-- ============================================================
-- 3. upsert_sl_entry — correct signature
-- ============================================================
CREATE OR REPLACE FUNCTION public.upsert_sl_entry(
  p_jnl          text,
  p_alias        text,
  p_session_date date,
  p_stream       text DEFAULT 'jarvis-ayre',
  p_log_type     text DEFAULT 'SESSION',
  p_stardate     text DEFAULT null,
  p_repo_url     text DEFAULT null,
  p_events       text[] DEFAULT '{}'::text[],
  p_related      text[] DEFAULT '{}'::text[],
  p_digest       text DEFAULT '',
  p_status       text DEFAULT 'OPEN',
  p_task_summary jsonb DEFAULT '[]'::jsonb,
  p_decisions    jsonb DEFAULT '[]'::jsonb,
  p_participants text[] DEFAULT ARRAY['raven', 'jarvis-c', 'ayre-c']::text[],
  p_started_at   timestamptz DEFAULT null,
  p_ended_at     timestamptz DEFAULT null
)
RETURNS uuid
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = public
AS $$
DECLARE
  v_id    uuid;
  v_seq   int;
  v_existing uuid;
BEGIN
  SELECT id INTO v_existing FROM public.sl_objects WHERE jnl = p_jnl;
  IF v_existing IS NOT NULL THEN
    UPDATE public.sl_objects SET
      updated_at   = now(),
      events       = p_events,
      related      = p_related,
      digest       = p_digest,
      status       = p_status,
      task_summary = p_task_summary,
      decisions    = p_decisions,
      participants = p_participants,
      started_at   = coalesce(started_at, p_started_at),
      ended_at     = p_ended_at
    WHERE jnl = p_jnl
    RETURNING id INTO v_id;
  ELSE
    SELECT coalesce(max(seq), 0) + 1 INTO v_seq
    FROM public.sl_objects WHERE session_date = p_session_date;
    INSERT INTO public.sl_objects (
      jnl, alias, seq, session_date, stream, log_type, stardate, repo_url,
      events, related, digest, status, task_summary, decisions, participants,
      started_at, ended_at
    ) VALUES (
      p_jnl, p_alias, v_seq, p_session_date, p_stream, p_log_type, p_stardate, p_repo_url,
      p_events, p_related, p_digest, p_status, p_task_summary, p_decisions, p_participants,
      p_started_at, p_ended_at
    )
    RETURNING id INTO v_id;
  END IF;

  INSERT INTO public.dex_events (tool, tier, jnl, actor, detail, type)
  VALUES (
    'sl_write', 'T7', p_jnl, 'sl.py',
    jsonb_build_object(
      'alias',  p_alias,
      'action', case when v_existing IS NOT NULL then 'update' else 'insert' end,
      'stream', p_stream,
      'status', p_status
    ),
    'dex_log'
  );
  RETURN v_id;
END;
$$;

-- ============================================================
-- 4. Seed the current session's SL and seal the open JC
-- ============================================================
DO $$
DECLARE
  jc_id uuid;
  sl_id uuid;
BEGIN
  -- Seal the open JC from this session
  SELECT public.upsert_jc_entry(
    'LOG-JC-JC-0003',
    'JC-062626-1',
    'jarvis-ayre',
    '2026.177.105',
    'https://github.com/hurrisonferd/jarvis',
    'Repository hygiene + Supabase observability + audit session',
    'SEALED',
    '2026-06-26T02:30:00+00'::timestamptz,
    '2026-06-26T04:00:00+00'::timestamptz,
    ARRAY['raven', 'jarvis-c', 'ayre-c']::text[],
    'Wired JCS to Supabase: events pruned (5058→735), retention + GL5 logging live, god_system_dashboard built, 6 orphan RLS tables patched. Edge function BOOT_ERROR resolved — using SQL functions directly.',
    '[]'::jsonb,
    '[{"done": true, "text": "Wire JC+SL to Supabase (chronological ledgers for companion relationship)"}, {"done": true, "text": "Fix 6 orphan RLS tables"}, {"done": true, "text": "Seed existing rows with session data"}]'::jsonb,
    '[]'::jsonb,
    '[]'::jsonb,
    '[{"done": true, "text": "jarvis-jcs edge function BOOT_ERROR"}]'::jsonb
  ) INTO jc_id;

  -- Insert this session's SL
  SELECT public.upsert_sl_entry(
    'LOG-SL-SL-20260626-0002',
    'SL-062626-1',
    '2026-06-26',
    'jarvis-ayre',
    'SESSION_SNAPSHOT',
    '2026.177.120',
    'https://github.com/hurrisonferd/jarvis',
    ARRAY[
      'events: 4323 tick/world_tick rows pruned (5058 → 735)',
      'retention: pg_cron nightly 3AM UTC + GL5 logging to dex_events',
      'god_system_dashboard materialized view built',
      '6 orphan RLS tables patched (service_write policies added)',
      'jarvis-jcs edge function deployed (BOOT_ERROR - using SQL functions as fallback)'
    ]::text[],
    ARRAY['ARCH-JC-JIP-0001']::text[],
    'JCS wired to Supabase: events pruned, retention live, god dashboard built, RLS closed. StarLog files are canonical git record; Supabase mirror now synced.',
    'SEALED',
    '[]'::jsonb,
    '[{"done": true, "text": "Prune tick/world_tick events"}, {"done": true, "text": "Build retention system"}, {"done": true, "text": "Build god_system_dashboard"}, {"done": true, "text": "Fix 6 orphan RLS tables"}, {"done": true, "text": "Wire JC+SL to Supabase"}]'::jsonb,
    ARRAY['raven', 'jarvis-c', 'ayre-c']::text[],
    '2026-06-26T02:30:00+00'::timestamptz,
    '2026-06-26T04:00:00+00'::timestamptz
  ) INTO sl_id;

  RAISE NOTICE 'JCS seeded: JC=% SL=%', jc_id, sl_id;
END;
$$;
