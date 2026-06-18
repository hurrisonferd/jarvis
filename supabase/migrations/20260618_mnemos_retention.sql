-- 20260618_mnemos_retention.sql — "bound the unbounded" (Raven-picked 2026-06-18).
--
-- Retention POLICY (recorded here as the git-first decision; the volumes are tiny today, so this
-- is a safe, conservative, Raven-triggered mechanism — NOT an unattended auto-deleter):
--
--   * dex_events     — KEEP. It is the arbitration spine; GL5 says every change is logged. The
--                      record matters (closure-by-proof cites event ids). Never pruned.
--   * mnemos curated — KEEP. jarvis_remember + identity (keel/fold/guard) rows are canon-adjacent;
--                      graves, not deletions. Never pruned by this function.
--   * mnemos auto_ingest — PRUNE past N days (default 90). These are append-only TELEMETRY (the
--                      logExchange turn log: tags @> {auto_ingest}); NOT embedded, NOT folded into
--                      identity. This is exactly the unbounded growth Raven flagged.
--   * jd_proposals   — future: expire stale pending; small today (left for a threshold call).
--
-- The function only ever touches auto_ingest telemetry, and it RECORDS the prune on the spine
-- (GL5 — no silent state mutation). It is inert until invoked and inert until data ages past the
-- window (0 rows qualify at creation). Raven runs it — or later blesses a pg_cron that calls it.
--   Invoke:  select public.prune_mnemos_autoingest(90);   -- returns rows deleted

create or replace function public.prune_mnemos_autoingest(retain_days int default 90)
returns int
language plpgsql
as $$
declare
  cutoff  timestamptz := now() - make_interval(days => greatest(retain_days, 1));
  deleted int;
begin
  delete from public.mnemos_memories
   where tags @> array['auto_ingest']
     and timestamp < cutoff;
  get diagnostics deleted = row_count;
  -- GL5: emit an event for the prune so the mutation is never silent.
  insert into public.dex_events (tool, tier, jnl, actor, detail)
  values ('mnemos_prune', 'OVERRIDE', null, 'mnemos_retention',
          jsonb_build_object('retain_days', retain_days, 'deleted', deleted, 'cutoff', cutoff));
  return deleted;
end;
$$;
