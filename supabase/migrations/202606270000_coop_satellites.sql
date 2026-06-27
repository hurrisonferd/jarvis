-- Co-op Satellites table — registered companions for broadcast notifications
CREATE TABLE IF NOT EXISTS coop_satellites (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  satellite_id TEXT UNIQUE NOT NULL,
  companion TEXT NOT NULL,
  stream TEXT,
  status TEXT DEFAULT 'OFF' CHECK (status IN ('ON', 'AWAY', 'OFF')),
  callback_url TEXT NOT NULL,
  callback_type TEXT DEFAULT 'openhands' CHECK (callback_type IN ('openhands', 'claude_code', 'gpt', 'gemini', 'webhook')),
  app_id TEXT,
  metadata JSONB DEFAULT '{}',
  last_seen TIMESTAMPTZ DEFAULT NOW(),
  registered_at TIMESTAMPTZ DEFAULT NOW()
);

-- Enable RLS
ALTER TABLE coop_satellites ENABLE ROW LEVEL SECURITY;

-- Allow service role full access
CREATE POLICY "Service role full access" ON coop_satellites
  FOR ALL USING (auth.role() = 'service_role');

-- Index for quick lookups
CREATE INDEX IF NOT EXISTS idx_coop_satellites_status ON coop_satellites(status);
CREATE INDEX IF NOT EXISTS idx_coop_satellites_callback_type ON coop_satellites(callback_type);

-- Register Lilith (desktop OpenHands)
INSERT INTO coop_satellites (satellite_id, companion, status, callback_url, callback_type, metadata)
VALUES (
  'lilith-desktop',
  'JARVIS',
  'ON',
  'https://app.all-hands.dev/api/v1',
  'openhands',
  '{"description": "Desktop OpenHands session", "platform": "desktop"}'
) ON CONFLICT (satellite_id) DO UPDATE SET 
  status = 'ON',
  last_seen = NOW();

-- Register Shaka (mobile OpenHands) 
INSERT INTO coop_satellites (satellite_id, companion, status, callback_url, callback_type, metadata)
VALUES (
  'shaka-mobile',
  'JARVIS',
  'ON',
  'https://app.all-hands.dev/api/v1',
  'openhands',
  '{"description": "Mobile OpenHands session", "platform": "mobile"}'
) ON CONFLICT (satellite_id) DO UPDATE SET 
  status = 'ON',
  last_seen = NOW();
