# JARVIS Stats Triggers

These stats are meaningful only when updated by real events. The MCP server updates the first automatic layer from tools that already fire.

## Automatic Today

```text
jarvis_end
  JARVIS.sessions_sealed++
  JARVIS.entropy_current = current entropy
  JARVIS.entropy_trend = stable | watch
  JARVIS.platforms_active tracks unique platforms
  JARVIS.build_vs_theory_ratio updates from narrative/decision keywords
  MNEMOS.sessions_stored++
  MNEMOS.vector_count++ when vector storage succeeds
  ERIS.gold_law_checks++
  ERIS.mission_alignment_score = 1 - entropy
  ERIS.entropy_signals_sent++ when ERIS action fires

jarvis_log
  JARVIS.decisions_logged++
  PROMETHEUS.decisions_logged++
  PROMETHEUS.avg_eris_weight updates
  PROMETHEUS.pending_raven_approval++
  PROMETHEUS.last_decision_system = system_affected
  system_affected.session_touches++

jarvis_overlap
  NEMESIS.overlap_checks++
  NEMESIS.warnings_issued++ when score > 0.45
  NEMESIS.conflicts_found++ on canonical conflict
  NEMESIS.highest_overlap_pair/score update on new high score

jarvis_recall
  MNEMOS.retrieval_count++ when recall returns results
```

## Future Real Triggers

```text
Gold Law violation
  ERIS.drift_events_caught++
  AEGIS.vetoes_issued++
  AEGIS.gold_law_violations_blocked++

Godot or build session
  SKADI.tasks_executed++
  SKADI.tasks_completed or tasks_failed

Philosophy query
  DANTE.philosophy_queries++
  DANTE.interpretations++

Routing decision
  ODIN.routing_decisions++
  ODIN.routes_to_skadi or routes_to_mnemos

Rollback
  LOKI.rollbacks_executed++
  LOKI.rollback_success_rate updates
```

## Storage

Stats live in `public.god_system_stats`.

- `stats_json` stores the full flexible stat object.
- `stat_a_*` through `stat_e_*` expose dashboard-friendly numeric summaries.
- `session_touches` remains a general activity counter per system.
