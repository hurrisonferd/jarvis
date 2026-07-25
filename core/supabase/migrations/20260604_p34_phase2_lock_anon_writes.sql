-- P34 Phase 2: lock the public anon key to READ-ONLY on tables the browser now
-- writes exclusively through the grid-write service-role proxy (GL5 — no silent
-- state mutation from the public key). Browser writes go via grid-write (service
-- role bypasses RLS); these anon INSERT/UPDATE policies are now dead surface.
-- SELECT policies are KEPT so reads + realtime subscriptions survive.
-- Verified writers: sessions/events/save_states/rom_library/push_subscriptions via
-- grid-write; node_fields/memory_state/emulator_state have NO anon writer in the
-- codebase (only realtime read subscriptions).
-- Applied + verified live 2026-06-04: grid-write insert -> 200 ok; direct anon
-- insert -> 401 "new row violates row-level security policy".

-- sessions (browser: grid-write insert+update)
drop policy if exists "anon insert sessions" on public.sessions;
drop policy if exists "anon update sessions" on public.sessions;

-- events (browser: grid-write insert)
drop policy if exists "anon insert events" on public.events;

-- save_states (browser: grid-write insert; no browser update)
drop policy if exists "anon insert save_states" on public.save_states;
drop policy if exists "anon_insert_save_states" on public.save_states;
drop policy if exists "anon update save_states" on public.save_states;

-- rom_library (browser: grid-write insert)
drop policy if exists "anon insert rom_library" on public.rom_library;

-- push_subscriptions (browser: grid-write upsert+delete)
drop policy if exists "anon insert" on public.push_subscriptions;

-- node_fields (no anon writer; realtime read only)
drop policy if exists "anon insert node_fields" on public.node_fields;
drop policy if exists "anon update node_fields" on public.node_fields;

-- memory_state (no anon writer)
drop policy if exists "anon upsert memory" on public.memory_state;
drop policy if exists "anon update memory" on public.memory_state;

-- emulator_state (no anon writer)
drop policy if exists "anon insert emulator_state" on public.emulator_state;
drop policy if exists "anon_insert_emulator_state" on public.emulator_state;
drop policy if exists "anon update emulator_state" on public.emulator_state;

-- DEFERRED (writer still on anon — lock only after reroute):
--   consensus_proposals  — operations/scripts/jarvis-propose.py writes via anon; route through
--                          grid-write (add to whitelist) or service key first.
--   world_kernels/world_agents/world_events — jarvis-world-init.py + CI heartbeat;
--                          blocked on SUPABASE_SERVICE_KEY in CI (P17 secret).
