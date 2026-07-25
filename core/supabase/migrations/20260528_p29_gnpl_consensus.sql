-- P29: GNPL Consensus Engine — multi-system proposal/vote table
-- Governance Node Protocol Layer: tracks proposals requiring quorum before execution

CREATE TABLE IF NOT EXISTS consensus_proposals (
  id             uuid        DEFAULT gen_random_uuid() PRIMARY KEY,
  created_at     timestamptz DEFAULT now(),
  proposal_type  text        NOT NULL,                                    -- 'tool_execution' | 'state_transition' | 'resource_access' | 'expansion'
  proposer       text        NOT NULL,                                    -- god system proposing (e.g. 'SKADI', 'ODIN')
  payload        jsonb       DEFAULT '{}',
  status         text        DEFAULT 'pending' CHECK (status IN ('pending','approved','rejected','expired')),
  votes          jsonb       DEFAULT '{}',                                -- { "AEGIS": "approve", "HALO": "approve" }
  required_quorum integer    DEFAULT 2,
  session_id     uuid        REFERENCES sessions(id) ON DELETE SET NULL,
  resolved_at    timestamptz,
  patch_id       text        DEFAULT 'P29',
  stage          text        DEFAULT 'AEGIS',
  correlation_id uuid        DEFAULT gen_random_uuid()
);

ALTER TABLE consensus_proposals ENABLE ROW LEVEL SECURITY;
CREATE POLICY "anon read"   ON consensus_proposals FOR SELECT USING (true);
CREATE POLICY "anon insert" ON consensus_proposals FOR INSERT WITH CHECK (true);
CREATE POLICY "anon update" ON consensus_proposals FOR UPDATE USING (true);

-- realtime
ALTER PUBLICATION supabase_realtime ADD TABLE consensus_proposals;

-- index for fast lookup by status + session
CREATE INDEX idx_consensus_pending ON consensus_proposals (status, session_id) WHERE status = 'pending';
