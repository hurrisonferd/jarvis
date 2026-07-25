-- Patch 17: audit_log + patch_log (append-only immutable change journal)
CREATE TABLE IF NOT EXISTS audit_log (
  id            bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  event_id      text UNIQUE NOT NULL DEFAULT gen_random_uuid()::text,
  event_type    text NOT NULL CHECK (event_type IN ('CHANGE','MERGE','REMOVAL','RECONCILE','SNAPSHOT','PATCH_DEPLOY','BOOT')),
  source_system text NOT NULL DEFAULT 'github',
  affected_paths text[],
  git_commit_id text,
  patch_ids     text[],
  diff_summary  text,
  risk_score    int DEFAULT 0,
  briefing_ref  text,
  metadata      jsonb DEFAULT '{}'::jsonb,
  created_at    timestamptz DEFAULT now()
);

CREATE TABLE IF NOT EXISTS patch_log (
  id          bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  patch_id    text UNIQUE NOT NULL,
  name        text NOT NULL,
  priority    text DEFAULT 'normal',
  status      text DEFAULT 'pending' CHECK (status IN ('done','partial','pending','reference','blocked')),
  summary     text,
  commits     text[],
  deployed_at timestamptz,
  notes       text,
  updated_at  timestamptz DEFAULT now()
);

ALTER TABLE audit_log ENABLE ROW LEVEL SECURITY;
ALTER TABLE patch_log ENABLE ROW LEVEL SECURITY;

CREATE POLICY "anon_select_audit_log" ON audit_log FOR SELECT TO anon USING (true);
CREATE POLICY "anon_select_patch_log" ON patch_log FOR SELECT TO anon USING (true);
CREATE POLICY "service_all_audit_log"  ON audit_log FOR ALL TO service_role USING (true);
CREATE POLICY "service_all_patch_log"  ON patch_log FOR ALL TO service_role USING (true);

ALTER PUBLICATION supabase_realtime ADD TABLE audit_log;
ALTER PUBLICATION supabase_realtime ADD TABLE patch_log;
