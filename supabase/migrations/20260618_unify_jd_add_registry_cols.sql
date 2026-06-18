-- 20260618_unify_jd_add_registry_cols.sql — Unification step 1 of 4 (Raven-approved 2026-06-18:
-- "jd_entries and jnl_registry are one system, one JSE wrapper"; approach = incremental + compat view).
--
-- jd_entries and jnl_registry are already one logical object split across two tables (jd_entries.jnl
-- is a FK into jnl_registry, and every connector write hits BOTH in lockstep). This migration begins
-- collapsing them into ONE physical table (jd_entries, the JSE object) by absorbing the three columns
-- that only jnl_registry carried: location, anchors, state.
--
-- This step is purely ADDITIVE — new nullable columns + a backfill from the current registry. Nothing
-- reads them yet, so it cannot break the live connector or the mirror. Later steps: JSE absorbs the
-- keys (seed/validate/sync own them), the dex drops its redundant jnl_registry writes, and jnl_registry
-- becomes a VIEW over jd_entries. Applied live via the connector (Supabase MCP) 2026-06-18, git-first.
-- Idempotent.

alter table public.jd_entries add column if not exists location text;
alter table public.jd_entries add column if not exists anchors  text[] not null default '{}';
alter table public.jd_entries add column if not exists state    text   not null default 'active';

-- Backfill from the registry so the one table holds the whole object before the view swap.
update public.jd_entries e
set location = r.location,
    anchors  = coalesce(r.anchors, '{}'),
    state    = coalesce(r.state, 'active')
from public.jnl_registry r
where e.jnl = r.jnl;
