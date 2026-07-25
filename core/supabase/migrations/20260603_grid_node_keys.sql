-- THE GRID — node signing keys (GNPL v0.2.0). PUBLIC material only. The node
-- stores its public key + the owner's identity certificate (a signature over the
-- identity assertion). The private key NEVER touches this system — only Raven
-- holds it, off-system. The node verifies; it never signs. (Sovereign-key model.)

create table if not exists public.node_keys (
  node_id text primary key,
  algo text not null default 'ed25519',
  public_key text not null,       -- raw 32-byte Ed25519 public key, base64
  identity_cert text not null,    -- signature over the identity assertion, base64
  owner text not null,
  assertion text not null,        -- the exact bytes that were signed (auditable)
  registered_at timestamptz not null default now()
);
