-- THE GRID — agent-to-agent inbox (GNPL brick 3). Inbound messages from other
-- nodes land here as pending + untrusted. JARVIS never auto-acts; the owner
-- (Raven) reviews and Allows/Denies. A mailbox, not an executor.

create table if not exists public.node_messages (
  id uuid primary key default gen_random_uuid(),
  from_node text not null,
  from_companion text,
  to_node text not null,
  intent text not null default 'message',
  body text not null,
  status text not null default 'pending',   -- pending | read | acted | declined
  trust text not null default 'untrusted',  -- inbound from another node is untrusted
  created_at timestamptz not null default now(),
  metadata jsonb not null default '{}'::jsonb
);

create index if not exists node_messages_inbox_idx
  on public.node_messages (to_node, status, created_at desc);
