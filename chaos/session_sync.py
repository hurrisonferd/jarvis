"""
JARVIS Session Sync v1.0
Backend functions for session start/end and HUGINN diff.
Used by Base44 hub and local session management.
"""

import json
import hashlib
import uuid
from datetime import datetime, timezone
from datetime import timedelta


def now():
    return datetime.now(timezone.utc).isoformat()


def _parse_utc(value: str | None = None) -> datetime:
    raw = (value or now()).replace("Z", "+00:00")
    dt = datetime.fromisoformat(raw)
    return dt.astimezone(timezone.utc)


def timeline_pointers(value: str | None = None) -> dict:
    dt = _parse_utc(value)
    iso = dt.isocalendar()
    monday = dt.date() - timedelta(days=dt.weekday())
    return {
        "day": dt.strftime("%Y-%m-%d"),
        "week": f"{iso.year}-W{iso.week:02d}",
        "week_start": monday.isoformat(),
        "month": dt.strftime("%Y-%m"),
    }


def huginn_diff(seed_state: dict, incoming_delta: dict) -> dict:
    systems_before = set(seed_state.get("god_systems", {}).keys())
    systems_after  = set(incoming_delta.get("god_systems", {}).keys()) if "god_systems" in incoming_delta else systems_before
    added   = systems_after - systems_before
    removed = systems_before - systems_after
    shared  = set(seed_state.keys()) & set(incoming_delta.keys())
    total   = set(seed_state.keys()) | set(incoming_delta.keys())
    drift   = len(shared) / max(len(total), 1)
    unauthorized = []
    if added:
        unauthorized.extend([f"system_added:{s}" for s in added])
    if removed:
        unauthorized.extend([f"system_removed:{s}" for s in removed])
    return {
        "drift_score":           round(drift, 3),
        "systems_added":         list(added),
        "systems_removed":       list(removed),
        "unauthorized_changes":  unauthorized,
        "merge_recommended":     drift >= 0.85 and not unauthorized,
        "timestamp":             now()
    }


def session_start(platform: str, chaos_seed: dict) -> dict:
    roles = {
        "claude": {"archetype": "Shiroe", "role": "vetting, audit, consistency enforcement"},
        "gpt":    {"archetype": "Kang",   "role": "production, execution, organized JARVIS spec"},
        "gemini": {"archetype": "Aizen",  "role": "ideation, interpretation, instance demonstration"},
    }
    arch    = roles.get(platform, roles["claude"])
    entropy = _compute_entropy(chaos_seed)
    session_id = str(uuid.uuid4())[:8]
    return {
        "session_id":      session_id,
        "platform":        platform,
        "archetype":       arch["archetype"],
        "role":            arch["role"],
        "chaos_version":   chaos_seed.get("chaos_version"),
        "jarvis_version":  chaos_seed.get("jarvis_version"),
        "mission":         chaos_seed.get("mission_statement", {}).get("primary"),
        "guardian":        chaos_seed.get("mission_statement", {}).get("guardian"),
        "gold_law_rules":  chaos_seed.get("gold_law", {}).get("rules", []),
        "pipeline_order":  chaos_seed.get("pipeline", {}).get("order", []),
        "system_count":    len(chaos_seed.get("god_systems", {})),
        "entropy_score":   entropy,
        "eris_active":     True,
        "started_at":      now(),
        "continuity_layers": [
            "event_log",
            "summaries",
            "working_memory",
            "ancestral_spine",
        ],
        "jc_object": {
            "kind": "session_start",
            "alias": f"JC-{session_id}",
            "platform": platform,
            "archetype": arch["archetype"],
            "continuity_role": "entry point for the session event log",
        },
        "timeline_pointers": timeline_pointers(),
    }


def session_end(platform, session_id, state_delta, narrative, current_chaos):
    diff = huginn_diff(current_chaos, state_delta)
    fp   = hashlib.sha256(json.dumps(current_chaos, sort_keys=True).encode()).hexdigest()[:16]
    git_commit = state_delta.get("git_commit") or state_delta.get("commit") or state_delta.get("head")
    jc_alias = state_delta.get("jc_alias") or f"JC-{session_id}"
    result = {
        "session_id":    session_id,
        "platform":      platform,
        "sealed_at":     now(),
        "drift_score":   diff["drift_score"],
        "huginn_diff":   diff,
        "narrative":     narrative,
        "chaos_updated": False,
        "fingerprint":   fp
    }
    result["event_log"] = {
        "kind": "session_end",
        "jc_alias": jc_alias,
        "git_commit": git_commit,
        "continuity_record": True,
        "summary": narrative,
        "state_delta_present": bool(state_delta),
        "saved_in_git": bool(git_commit),
        "timeline_pointers": timeline_pointers(),
        "layers": [
            "event_log",
            "summaries",
            "working_memory",
            "ancestral_spine",
        ],
    }
    if diff["merge_recommended"]:
        result["chaos_updated"] = True
        result["event_log"]["merge_recommended"] = True
    else:
        result["blocked_reason"] = f"Drift {diff['drift_score']} below 0.85 or unauthorized changes: {diff['unauthorized_changes']}"
        result["event_log"]["merge_recommended"] = False
    return result


def compute_entropy(chaos_seed: dict) -> dict:
    score = _compute_entropy(chaos_seed)
    systems = chaos_seed.get("god_systems", {})
    gold_law = chaos_seed.get("gold_law", {}).get("rules", [])
    mission  = chaos_seed.get("mission_statement", {}).get("primary", "")
    forbidden = chaos_seed.get("interaction_graph", {}).get("forbidden_edges", [])
    count = len(systems)
    return {
        "score":  score,
        "status": "ALIGNED" if score < 0.3 else "WATCH" if score < 0.6 else "SIGNAL" if score < 0.8 else "CRITICAL",
        "components": {
            "system_count":      round(max(0, (count - 27) / 27), 3),
            "rule_coherence":    round(max(0, 1.0 - len(gold_law) / 20.0), 3),
            "mission_alignment": 0.0 if "JARVIS" in mission else 0.5,
            "edge_integrity":    round(max(0, 1.0 - len(forbidden) / 10.0), 3),
        },
        "eris_action": None if score < 0.6 else "signals governance systems" if score < 0.8 else "signals directly to Raven"
    }


def _compute_entropy(chaos_seed: dict) -> float:
    systems  = chaos_seed.get("god_systems", {})
    gold_law = chaos_seed.get("gold_law", {}).get("rules", [])
    mission  = chaos_seed.get("mission_statement", {}).get("primary", "")
    forbidden = chaos_seed.get("interaction_graph", {}).get("forbidden_edges", [])
    count    = len(systems)
    target   = 27
    count_score     = max(0, (count - target) / max(target, 1))
    coherence_score = max(0, 1.0 - len(gold_law) / 20.0)
    alignment_score = 0.0 if "JARVIS" in mission else 0.5
    edge_score      = max(0, 1.0 - len(forbidden) / 10.0)
    entropy = (count_score * 0.3 + coherence_score * 0.2 + alignment_score * 0.3 + edge_score * 0.2)
    return min(1.0, max(0.0, round(entropy, 3)))
