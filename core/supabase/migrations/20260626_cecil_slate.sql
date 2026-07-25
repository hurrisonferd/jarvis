-- Cecil: companion carry slate (CONN-CEP-0001)
-- One session writes carry data; the next session reads and clears it.
-- Companion-scoped, 24h TTL, one-time lift.

CREATE TABLE IF NOT EXISTS cecil_slate (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  carry_key TEXT NOT NULL,
  companion_key TEXT NOT NULL,
  stream TEXT NOT NULL,
  carry_data TEXT NOT NULL,
  expires_at TIMESTAMPTZ NOT NULL DEFAULT (now() + '24 hours'::interval),
  written_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  written_by_session TEXT,
  lifted BOOLEAN NOT NULL DEFAULT FALSE,
  lifted_at TIMESTAMPTZ
);

CREATE UNIQUE INDEX IF NOT EXISTS cecil_slate_key_active
  ON cecil_slate (carry_key)
  WHERE lifted = FALSE;

CREATE INDEX IF NOT EXISTS cecil_slate_expires
  ON cecil_slate (expires_at)
  WHERE lifted = FALSE;
