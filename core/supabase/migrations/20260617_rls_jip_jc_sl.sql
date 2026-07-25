-- 20260617_rls_jip_jc_sl.sql — close the anon exposure flagged CRITICAL by the Supabase advisor,
-- and secure the freshly-materialized jip_entries. Applied live via the connector (Supabase MCP)
-- 2026-06-17 and recorded here git-first so git == live. Idempotent.
--
-- Effect: RLS ON for all three; the service_role (the connector's key) keeps full access; the anon
-- and authenticated roles are denied by default (no policy granted to them). The connector reads/
-- writes via the service key, so jc_recall + JIP tools are unaffected; only anon-key access closes.

alter table public.jip_entries enable row level security;
alter table public.jc_objects  enable row level security;
alter table public.sl_objects  enable row level security;

drop policy if exists service_all on public.jip_entries;
create policy service_all on public.jip_entries for all to service_role using (true) with check (true);

drop policy if exists service_all on public.jc_objects;
create policy service_all on public.jc_objects  for all to service_role using (true) with check (true);

drop policy if exists service_all on public.sl_objects;
create policy service_all on public.sl_objects  for all to service_role using (true) with check (true);
