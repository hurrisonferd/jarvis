-- 20260617_drop_jd_entries_seq_unique.sql — unfreeze the git→Supabase mirror.
--
-- Root cause (found 2026-06-17): jd_entries carried a partial UNIQUE index on seq
--   CREATE UNIQUE INDEX jd_entries_seq_key ON public.jd_entries (seq) WHERE seq IS NOT NULL
-- seq is the JID mint serial. Any reseed/renumber in git reassigns a seq value to a
-- different jnl; the mirror upserts ON CONFLICT (jnl), which does NOT cover a seq
-- collision against a stale row. So since 2026-06-11 every jd_entries batch upsert died
-- with "23505 duplicate key … jd_entries_seq_key", SystemExit reddened the (unwatched)
-- CI mirror job, and jd_entries froze at 125 rows while jnl_registry (no seq column) kept
-- flowing. GPT read the stale mirror and confabulated missing layers.
--
-- Fix: drop the unique index. seq uniqueness is already guaranteed upstream — git is the
-- mint ledger and validate.py (JVE) enforces it. Enforcing it again on a READ mirror only
-- makes upserts brittle during renumbering. jnl stays the PK; seq stays a plain column.
-- Applied live via the connector (Supabase MCP) 2026-06-17 and recorded here git-first so
-- git == live (Git-First Canon, AUD-SYNC-REVW-0001). Idempotent.

drop index if exists public.jd_entries_seq_key;
