-- 20260625_mnemos_memory_tier.sql
-- REWORK 1 (HIGH): stamp every memory with its JMMS tier.
-- Direct edge calls bypassed tiering — jarvis_remember did it, mnemos-store did not.
-- Fix: add memory_tier column + index, backfill existing rows to jltm (consolidated/durable default).

alter table public.mnemos_memories
  add column if not exists memory_tier text not null default 'jltm';

-- Index for JLTM recall path (REWORK 2)
create index if not exists idx_mnemos_memories_memory_tier
  on public.mnemos_memories (memory_tier, timestamp desc);

-- Backfill existing rows (all existing are jltm — they survived in Supabase, ergo durable)
update public.mnemos_memories
  set memory_tier = 'jltm'
  where memory_tier is null;

-- GL5: log the schema change on the spine
insert into public.dex_events (tool, tier, jnl, actor, detail)
values ('alter_table', 'OVERRIDE', null, 'jarvis',
        '{"action":"add memory_tier column","table":"mnemos_memories","default":"jltm"}');
