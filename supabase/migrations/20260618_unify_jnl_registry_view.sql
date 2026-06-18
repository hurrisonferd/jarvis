-- 20260618_unify_jnl_registry_view.sql — Unification step 3/4 of 4: collapse to ONE table.
--
-- jd_entries now physically holds the whole governed object (location/anchors/state absorbed in
-- 20260618_unify_jd_add_registry_cols.sql). The connector (jarvis-dex) and the mirror (sync_supabase)
-- no longer write jnl_registry. So jnl_registry becomes a VIEW over jd_entries — the same interface
-- every reader already uses (jarvis-dex jd_get/jd_list/collision-check, jarvis-mcp status), now
-- derived from the single source instead of a second table that could drift. Drift class eliminated.
--
-- Only jd_entries.jnl FK-referenced jnl_registry (verified 2026-06-18), so dropping it is clean.
-- Apply ONLY AFTER the jarvis-dex deploy that removes the jnl_registry writes (a view is not
-- upsertable). Applied live via the connector (Supabase MCP) + recorded git-first. Idempotent-ish
-- (drop view/table guards both directions).

alter table public.jd_entries drop constraint if exists jd_entries_jnl_fkey;
drop view  if exists public.jnl_registry;
drop table if exists public.jnl_registry;

create view public.jnl_registry as
  select jnl, name, type, class, tier, owner, parent, location,
         tags, anchors, state, status, created, updated, synced_at
  from public.jd_entries;
