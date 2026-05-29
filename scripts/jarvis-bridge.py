#!/usr/bin/env python3
"""
GRID Execution Bridge CLI — submit events through AEGIS gate.
All events are validated by AEGIS and logged to execution_trace.

Usage:
  jarvis-bridge.py submit <type> <intent> [patch_id]
  jarvis-bridge.py list [limit]
  jarvis-bridge.py trace <trace_id>

Event types: speak, store, propose, execute, observe, query, heartbeat, recall, commit, deploy
Source is always 'jarvis' from this CLI.
"""
import json
import os
import sys
import urllib.request

SUPABASE_URL = os.environ.get("SUPABASE_URL", "https://oexghfsvhnggddllgvrt.supabase.co")
SUPABASE_ANON = os.environ.get("SUPABASE_ANON_KEY", "sb_publishable_N1-MFLpXtOXkKh3UQNfclw_ZG0TVqOA")
BRIDGE_FN = f"{SUPABASE_URL}/functions/v1/grid-event"
REST_BASE  = f"{SUPABASE_URL}/rest/v1"
HEADERS    = {"apikey": SUPABASE_ANON, "Authorization": f"Bearer {SUPABASE_ANON}"}


def submit(event_type: str, intent: str, patch_id: str = None) -> dict:
    payload = json.dumps({
        "type":     event_type,
        "source":   "jarvis",
        "intent":   intent,
        "node_id":  "node-001-raven",
        "payload":  {"cli": True},
        **({
            "patch_id": patch_id} if patch_id else {}),
    }).encode()
    req = urllib.request.Request(
        BRIDGE_FN, data=payload,
        headers={"Content-Type": "application/json", "Authorization": f"Bearer {SUPABASE_ANON}"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            return json.loads(resp.read())
    except urllib.error.HTTPError as e:
        body = e.read()
        try:
            return json.loads(body) if body else {"error": f"HTTP {e.code}"}
        except json.JSONDecodeError:
            return {"error": f"HTTP {e.code}: {body.decode('utf-8', errors='replace')[:200]}"}
    except Exception as e:
        return {"error": str(e)}


def list_traces(limit: int = 10) -> list:
    url = f"{BRIDGE_FN}?limit={limit}"
    req = urllib.request.Request(url, headers={"Authorization": f"Bearer {SUPABASE_ANON}"})
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            return json.loads(resp.read()).get("traces", [])
    except Exception:
        return []


def get_trace(trace_id: str) -> dict:
    url = f"{REST_BASE}/execution_trace?id=eq.{trace_id}&select=*"
    req = urllib.request.Request(url, headers=HEADERS)
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read())
            return data[0] if data else {}
    except Exception:
        return {}


def fmt_trace(t: dict) -> str:
    ts     = (t.get("created_at") or "")[:19].replace("T", " ")
    typ    = (t.get("type") or "?")[:10]
    src    = (t.get("source") or "?")[:10]
    stage  = t.get("stage") or "?"
    intent = (t.get("intent") or "")[:60]
    pid    = t.get("patch_id") or ""
    pid_s  = f" [{pid}]" if pid else ""
    return f"  [{typ}/{src} {ts} {stage}]{pid_s} {intent}"


def main():
    args = sys.argv[1:]

    if not args or args[0] == "list":
        limit = int(args[1]) if len(args) > 1 else 10
        traces = list_traces(limit)
        if not traces:
            print("No execution traces found. Bridge may be unreachable.")
            sys.exit(0)
        print(f"EXECUTION TRACE — last {len(traces)} events")
        print("─" * 60)
        for t in traces:
            print(fmt_trace(t))
        print()
        sys.exit(0)

    if args[0] == "trace":
        if len(args) < 2:
            print("Usage: jarvis-bridge.py trace <trace_id>")
            sys.exit(1)
        t = get_trace(args[1])
        if not t:
            print(f"No trace found: {args[1]}")
            sys.exit(1)
        print(json.dumps(t, indent=2))
        sys.exit(0)

    if args[0] == "submit":
        if len(args) < 3:
            print("Usage: jarvis-bridge.py submit <type> <intent> [patch_id]")
            print("Types: speak store propose execute observe query heartbeat recall commit deploy")
            sys.exit(1)
        event_type = args[1]
        intent     = args[2]
        patch_id   = args[3] if len(args) > 3 else None

        result = submit(event_type, intent, patch_id)

        print(f"AEGIS GATE — {event_type.upper()}")
        print("─" * 50)

        status = result.get("status", "error")
        if status == "allowed":
            print(f"  status:   ALLOWED")
            print(f"  trust:    {result.get('trust', '?')}")
            print(f"  trace_id: {(result.get('trace_id') or '')[:8]}...")
            print(f"  node:     {result.get('node_id', '?')}")
            print(f"  intent:   {intent}")
        elif status == "rejected":
            print(f"  status:   REJECTED")
            print(f"  reason:   {result.get('reason', 'unknown')}")
            print(f"  trust:    {result.get('trust', 0)}")
        else:
            print(f"  error:    {result.get('error', 'bridge unreachable')}")
        sys.exit(0)

    print(f"Unknown command: {args[0]}")
    print("Commands: submit, list, trace")
    sys.exit(1)


if __name__ == "__main__":
    main()
