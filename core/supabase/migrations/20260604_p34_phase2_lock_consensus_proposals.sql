-- P34 phase 2 (cont): consensus_proposals is now written through the grid-write
-- service-role proxy (operations/scripts/jarvis-propose.py rerouted; browser GNPL already
-- proxied). Lock the anon key to READ-ONLY: drop the anon INSERT/UPDATE policies,
-- keep anon SELECT (the session brief + /propose list read it). GL5.
-- Applied + verified live 2026-06-04: grid-write insert -> 200 ok; direct anon
-- insert -> 401 "new row violates row-level security policy".
drop policy if exists "anon insert" on public.consensus_proposals;
drop policy if exists "anon update" on public.consensus_proposals;