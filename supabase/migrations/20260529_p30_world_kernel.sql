-- P30: World Kernel Spec
-- NODE → WORLD promotion. Isolated execution sandbox + bounded agent hosting.
-- A World is a promoted GRID node with its own storage envelope, runtime loop, and agent registry.
-- Foundation for P31 (Mythos Governance) and P32 (Fractal Universe).

-- ── world_kernels: promoted nodes ────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS world_kernels (
  id              uuid        DEFAULT gen_random_uuid() PRIMARY KEY,
  world_id        text        UNIQUE NOT NULL,
  node_id         text        NOT NULL,               -- references grid_nodes.node_id (soft ref)
  owner           text        NOT NULL,
  display_name    text        NOT NULL,
  description     text,
  schema_version  int         DEFAULT 1,
  rules           jsonb       DEFAULT '{}',           -- L1 causal rules governing this world
  bounds          jsonb       NOT NULL,               -- storage envelope — enforced by AEGIS
  initial_state   jsonb       DEFAULT '{}',           -- L0 spatial seed + portals
  access_policy   jsonb       DEFAULT '{"mode":"owner_only"}',
  tick_rate_ms    int         DEFAULT 900,            -- world's own temporal cadence
  status          text        DEFAULT 'active'
                              CHECK (status IN ('active','archived','suspended')),
  gl7_approved    boolean     DEFAULT false,          -- GL7 review passed
  raven_sign_off  boolean     DEFAULT false,          -- Raven explicit sign-off
  promoted_at     timestamptz DEFAULT now(),
  last_tick       timestamptz,
  tick_count      bigint      DEFAULT 0,
  created_at      timestamptz DEFAULT now(),
  patch_id        text        DEFAULT 'P30'
);

-- ── world_agents: agents admitted to a world ─────────────────────────────────
-- All admission via GNPL proposal. World owner has final authority.
CREATE TABLE IF NOT EXISTS world_agents (
  id           uuid        DEFAULT gen_random_uuid() PRIMARY KEY,
  world_id     text        REFERENCES world_kernels(world_id) ON DELETE CASCADE,
  agent_id     text        NOT NULL,
  role         text        NOT NULL
                           CHECK (role IN ('sovereign','executor','ideator','observer')),
  trust_score  float       DEFAULT 0.5
                           CHECK (trust_score >= 0 AND trust_score <= 1),
  capabilities jsonb       DEFAULT '[]',
  admitted_by  text        NOT NULL,
  admitted_at  timestamptz DEFAULT now(),
  last_active  timestamptz,
  status       text        DEFAULT 'active'
                           CHECK (status IN ('active','suspended','expelled')),
  patch_id     text        DEFAULT 'P30',
  UNIQUE (world_id, agent_id)
);

-- ── world_events: append-only audit trail per world (GL9) ────────────────────
CREATE TABLE IF NOT EXISTS world_events (
  id         uuid        DEFAULT gen_random_uuid() PRIMARY KEY,
  world_id   text        REFERENCES world_kernels(world_id) ON DELETE CASCADE,
  event_type text        NOT NULL,
    -- 'world_promoted' | 'world_archived' | 'world_heartbeat'
    -- 'agent_admitted' | 'agent_suspended' | 'agent_expelled'
    -- 'tick' | 'bounds_exceeded' | 'portal_connect' | 'portal_disconnect'
    -- 'gnpl_propose' | 'gnpl_commit' | 'gnpl_reject'
  stage      text,                                    -- pipeline stage that emitted this
  agent_id   text,
  payload    jsonb       DEFAULT '{}',
  gl_law     text,
  ts         timestamptz DEFAULT now(),
  patch_id   text        DEFAULT 'P30'
);

-- ── RLS ──────────────────────────────────────────────────────────────────────
ALTER TABLE world_kernels ENABLE ROW LEVEL SECURITY;
ALTER TABLE world_agents  ENABLE ROW LEVEL SECURITY;
ALTER TABLE world_events  ENABLE ROW LEVEL SECURITY;

CREATE POLICY "anon read"   ON world_kernels FOR SELECT USING (true);
CREATE POLICY "anon insert" ON world_kernels FOR INSERT WITH CHECK (true);
CREATE POLICY "anon update" ON world_kernels FOR UPDATE USING (true);

CREATE POLICY "anon read"   ON world_agents FOR SELECT USING (true);
CREATE POLICY "anon insert" ON world_agents FOR INSERT WITH CHECK (true);
CREATE POLICY "anon update" ON world_agents FOR UPDATE USING (true);

CREATE POLICY "anon read"   ON world_events FOR SELECT USING (true);
CREATE POLICY "anon insert" ON world_events FOR INSERT WITH CHECK (true);

-- ── Realtime ─────────────────────────────────────────────────────────────────
ALTER PUBLICATION supabase_realtime ADD TABLE world_kernels;
ALTER PUBLICATION supabase_realtime ADD TABLE world_events;

-- ── Indexes ──────────────────────────────────────────────────────────────────
CREATE INDEX idx_world_kernels_owner  ON world_kernels (owner);
CREATE INDEX idx_world_kernels_status ON world_kernels (status);
CREATE INDEX idx_world_agents_world   ON world_agents  (world_id, status);
CREATE INDEX idx_world_events_world   ON world_events  (world_id, ts DESC);
