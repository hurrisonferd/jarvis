-- P37 Grid Trust Layer: lock the federation tables. node_keys + node_messages were
-- RLS-disabled in public (Supabase advisor ERROR rls_disabled_in_public) — world-
-- writable via the anon key. Anyone could forge signing-key registrations or flood
-- any node's inbox. Enable RLS. Public keys are publishable (anon read); inbox
-- messages are owner-only via the service-role connector (no anon access). All
-- writes are service-role only (the connector uses the service key, which bypasses
-- RLS). Applied live 2026-06-04.
alter table public.node_keys enable row level security;
alter table public.node_messages enable row level security;

drop policy if exists "anon read node_keys" on public.node_keys;
create policy "anon read node_keys" on public.node_keys for select to anon using (true);

-- node_messages: intentionally NO anon policy → deny-all to anon. The connector
-- reads and writes with the service role. Inbound is held for the owner only and
-- never exposed to the public key.
