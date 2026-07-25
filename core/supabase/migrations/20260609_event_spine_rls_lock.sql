-- HADES spine: immutable truth must not be world-writable (GL5).
-- Public read; writes only via service role (bypasses RLS). No anon mutation path.
alter table public.event_spine enable row level security;
drop policy if exists "public read event_spine" on public.event_spine;
create policy "public read event_spine" on public.event_spine for select using (true);
