alter table public.god_system_stats
  add column if not exists stat_a_key text,
  add column if not exists stat_a_val numeric default 0,
  add column if not exists stat_b_key text,
  add column if not exists stat_b_val numeric default 0,
  add column if not exists stat_c_key text,
  add column if not exists stat_c_val numeric default 0,
  add column if not exists stat_d_key text,
  add column if not exists stat_d_val numeric default 0,
  add column if not exists stat_e_key text,
  add column if not exists stat_e_val numeric default 0,
  add column if not exists stats_json jsonb default '{}'::jsonb;

insert into public.god_system_stats (system_id, stats_json)
values
  ('JARVIS', '{"sessions_sealed":0,"decisions_logged":0,"entropy_current":0.0,"entropy_trend":"stable","gold_law_violations":0,"platforms_active":0,"days_since_start":0,"build_vs_theory_ratio":0.0,"build_sessions":0,"theory_sessions":0,"platforms_seen":[]}'::jsonb),
  ('ERIS', '{"entropy_signals_sent":0,"mission_alignment_score":1.0,"last_signal_reason":null,"gold_law_checks":0,"drift_events_caught":0}'::jsonb),
  ('AEGIS', '{"constraints_enforced":0,"vetoes_issued":0,"gold_law_violations_blocked":0,"pass_rate":1.0,"last_veto_reason":null}'::jsonb),
  ('ODIN', '{"routing_decisions":0,"routes_to_skadi":0,"routes_to_mnemos":0,"failed_routes":0,"avg_route_depth":0.0}'::jsonb),
  ('SKADI', '{"tasks_executed":0,"tasks_completed":0,"tasks_failed":0,"completion_rate":1.0,"last_task_type":null}'::jsonb),
  ('MNEMOS', '{"sessions_stored":0,"vector_count":0,"retrieval_count":0,"avg_drift_score":0.0,"oldest_memory_days":0}'::jsonb),
  ('PROMETHEUS', '{"decisions_logged":0,"systems_most_affected":[],"avg_eris_weight":0.0,"pending_raven_approval":0,"last_decision_system":null}'::jsonb),
  ('JANUS', '{"proposals_generated":0,"proposals_accepted":0,"proposals_rejected":0,"acceptance_rate":0.0,"last_proposal_topic":null}'::jsonb),
  ('HUGINN', '{"diffs_computed":0,"drift_detected_count":0,"avg_drift_score":0.0,"cross_platform_syncs":0,"last_sync_platform":null}'::jsonb),
  ('HALO', '{"structure_checks":0,"violations_found":0,"clean_rate":1.0,"last_violation_type":null,"iris_flags_received":0}'::jsonb),
  ('MIMIR', '{"semantic_checks":0,"contradictions_found":0,"consistency_score":1.0,"last_check_system":null,"false_positives":0}'::jsonb),
  ('NEMESIS', '{"overlap_checks":0,"warnings_issued":0,"conflicts_found":0,"highest_overlap_pair":null,"highest_overlap_score":0.0}'::jsonb),
  ('LOKI', '{"rollbacks_executed":0,"rollback_success_rate":1.0,"deepest_rollback_depth":0,"last_rollback_reason":null,"tidal_marks_used":0}'::jsonb),
  ('DANTE', '{"interpretations":0,"philosophy_queries":0,"frames_applied":0,"havenos_queries":0,"last_frame_type":null}'::jsonb),
  ('ATLAS', '{"uptime_sessions":0,"substrate_failures":0,"avg_response_ms":0.0,"ollama_calls":0,"last_model_used":null}'::jsonb)
on conflict (system_id) do update
set stats_json = coalesce(public.god_system_stats.stats_json, '{}'::jsonb) || excluded.stats_json,
    last_updated = now();
