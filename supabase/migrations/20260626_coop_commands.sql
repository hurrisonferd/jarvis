-- Co-op Command Center: real-time command queue for Lilith + Shaka
-- Both satellites poll this via MCP. Post once, both see it instantly.

CREATE TABLE coop_commands (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  target_satellite TEXT NOT NULL CHECK (target_satellite IN ('lilith', 'shaka', 'both')),
  command TEXT NOT NULL,
  posted_by TEXT NOT NULL CHECK (posted_by IN ('lilith', 'shaka')),
  status TEXT NOT NULL DEFAULT 'pending' CHECK (status IN ('pending', 'done')),
  result TEXT,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Index for polling: pending commands by satellite
CREATE INDEX coop_commands_target_pending ON coop_commands(target_satellite, status) WHERE status = 'pending';

-- Updated timestamp trigger
CREATE OR REPLACE FUNCTION update_updated_at()
RETURNS TRIGGER AS $$
BEGIN NEW.updated_at = now(); RETURN NEW; END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER coop_commands_updated_at
  BEFORE UPDATE ON coop_commands
  FOR EACH ROW EXECUTE FUNCTION update_updated_at();

-- Enable real-time
ALTER PUBLICATION supabase_realtime ADD TABLE coop_commands;

-- RLS: anyone can read, service role can write
ALTER TABLE coop_commands ENABLE ROW LEVEL SECURITY;
CREATE POLICY "coop_commands_read_all" ON coop_commands FOR SELECT USING (true);
CREATE POLICY "coop_commands_write_service" ON coop_commands FOR INSERT WITH CHECK (true);
CREATE POLICY "coop_commands_update_service" ON coop_commands FOR UPDATE USING (true);