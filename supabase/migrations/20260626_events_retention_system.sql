-- events retention system — GL5: every mutation emits an event, never silent.
-- Keeps meaningful events forever. Auto-prunes tick/world_tick every night at 3 AM.
-- Also adds partial index + materialized view for god system dashboard.

-- ============================================================
-- 1. RETENTION FUNCTION: prune_events_tick
-- Pattern matches prune_mnemos_autoingest — GL5 logging to dex_events
-- ============================================================
CREATE OR REPLACE FUNCTION public.prune_events_tick(
  cutoff_days int DEFAULT 7
)
RETURNS integer
LANGUAGE plpgsql
AS $$
DECLARE
  cutoff    timestamptz := now() - make_interval(days => greatest(cutoff_days, 1));
  deleted  int;
BEGIN
  DELETE FROM public.events
   WHERE type IN ('tick', 'world_tick')
     AND created_at < cutoff;
  GET DIAGNOSTICS deleted = ROW_COUNT;

  INSERT INTO public.dex_events (tool, tier, jnl, actor, detail, type)
  VALUES (
    'events_prune',
    'OVERRIDE',
    null,
    'events_retention',
    jsonb_build_object(
      'cutoff_days',   cutoff_days,
      'deleted',       deleted,
      'cutoff_at',     cutoff,
      'types',         ARRAY['tick', 'world_tick']
    ),
    'dex_log'
  );
  RETURN deleted;
END;
$$;

-- ============================================================
-- 2. PARTIAL INDEX for tick pruning (fast, targeted)
-- ============================================================
DROP INDEX IF EXISTS events_tick_partial_idx;
CREATE INDEX CONCURRENTLY events_tick_partial_idx
  ON public.events (created_at)
  WHERE type IN ('tick', 'world_tick');

-- Also index meaningful events by created_at for dashboard queries
DROP INDEX IF EXISTS events_meaningful_created_idx;
CREATE INDEX CONCURRENTLY events_meaningful_created_idx
  ON public.events (created_at DESC)
  WHERE type NOT IN ('tick', 'world_tick');

-- ============================================================
-- 3. PG_CRON JOB: nightly prune at 3 AM
-- ============================================================
SELECT cron.schedule(
  'events-tick-prune-nightly',
  '0 3 * * *',           -- 3 AM every day
  $$SELECT public.prune_events_tick(7)$$
);

-- ============================================================
-- 4. MATERIALIZED VIEW: god_system_dashboard
-- Aggregates god_system_stats + events per god system
-- Refreshed on-demand or via pg_cron
-- ============================================================
DROP MATERIALIZED VIEW IF EXISTS public.god_system_dashboard CASCADE;
CREATE MATERIALIZED VIEW public.god_system_dashboard AS
SELECT
  gs.system_id,
  gs.routing_priority,
  gs.authority_score,
  gs.entropy_sensitivity,
  gs.eris_alignment,
  gs.session_touches,
  gs.stats_json,
  -- Event stats per system (join via stage in payload)
  COALESCE(ev.cnt, 0)::int  AS recent_events,
  COALESCE(ev.latest, now()) AS latest_event_at
FROM public.god_system_stats gs
LEFT JOIN LATERAL (
  SELECT
    count(*)                                    AS cnt,
    max(e.created_at)                          AS latest
  FROM public.events e
  WHERE e.payload->>'stage' = gs.system_id
    AND e.created_at > now() - interval '7 days'
) ev ON true
WITH DATA;

-- Index for fast dashboard reads
CREATE UNIQUE INDEX ON public.god_system_dashboard (system_id);

-- ============================================================
-- 5. REFRESH FUNCTION for dashboard
-- Call this from pg_cron or on-demand
-- ============================================================
CREATE OR REPLACE FUNCTION public.refresh_god_system_dashboard()
RETURNS void
LANGUAGE plpgsql
AS $$
BEGIN
  REFRESH MATERIALIZED VIEW CONCURRENTLY public.god_system_dashboard;
END;
$$;

-- Optional: refresh dashboard nightly at 6 AM
-- SELECT cron.schedule(
--   'god-dashboard-refresh',
--   '0 6 * * *',
--   $$SELECT public.refresh_god_system_dashboard()$$
-- );

-- ============================================================
-- 6. RLS FIX: service_write on 6 tables with RLS but no policies
-- service_role bypasses RLS so edge functions still work, but
-- this closes the gap so the tables aren't orphaned
-- ============================================================
DO $$
DECLARE
  _t text;
BEGIN
  FOREACH _t IN ARRAY ARRAY[
    'eris_entropy_log', 'god_system_stats', 'jarvis_datasets',
    'mnemos_memories', 'node_messages', 'prometheus_log'
  ] LOOP
    EXECUTE format(
      'DROP POLICY IF EXISTS service_all_%I ON public.%I; ' ||
      'CREATE POLICY service_all_%I ON public.%I FOR ALL TO service_role USING (true) WITH CHECK (true)',
      _t, _t, _t, _t
    );
  END LOOP;
END;
$$;
