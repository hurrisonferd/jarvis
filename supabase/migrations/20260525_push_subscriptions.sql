create table if not exists push_subscriptions (
  id uuid default gen_random_uuid() primary key,
  endpoint text not null unique,
  subscription_info jsonb not null,
  created_at timestamptz default now()
);

alter table push_subscriptions enable row level security;

-- Anon can insert only — server-side reads use service role key
create policy "anon insert"
  on push_subscriptions
  for insert
  to anon
  with check (true);
