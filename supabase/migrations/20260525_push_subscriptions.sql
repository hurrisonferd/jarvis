-- JARVIS Web Push subscriptions
-- Stores browser push endpoints for PROMETHEUS/heartbeat/alert delivery.

create table if not exists push_subscriptions (
  id          uuid primary key default gen_random_uuid(),
  endpoint    text not null unique,
  p256dh      text not null,
  auth        text not null,
  user_agent  text,
  created_at  timestamptz default now()
);

-- RLS: service role only (server writes, no public reads)
alter table push_subscriptions enable row level security;

create policy "service role full access"
  on push_subscriptions
  using (auth.role() = 'service_role')
  with check (auth.role() = 'service_role');
