#!/usr/bin/env python3
"""
Swarm Dashboard — Real-time view of all swarm tasks

Usage:
    python swarm_dashboard.py              # Watch mode (continuous)
    python swarm_dashboard.py --once       # One-shot view
    python swarm_dashboard.py --tail 20    # Last N lines of log
"""

import os
import sys
import time
import argparse
import requests
from pathlib import Path
from datetime import datetime, timezone

OPENHANDS_API_URL = "https://app.all-hands.dev/api/v1"

def get_api_key():
    return os.environ.get("OPENHANDS_CLOUD_API_KEY", "")

def get_conversations(headers):
    """Get all active conversations."""
    try:
        resp = requests.get(
            f"{OPENHANDS_API_URL}/app-conversations/search",
            headers=headers,
            params={"limit": 50}
        )
        resp.raise_for_status()
        return resp.json().get("items", [])
    except:
        return []

def get_current_swarm_log():
    """Find the current swarm log file."""
    mp_dir = Path(__file__).parent / "MARCO-POLO"
    logs = sorted(mp_dir.glob("MP-*.md"), key=lambda x: x.name)
    return logs[-1] if logs else None

def format_time():
    return datetime.now(timezone.utc).strftime("%H:%M:%S")

def print_dashboard():
    api_key = get_api_key()
    headers = {"Authorization": f"Bearer {api_key}"} if api_key else {}
    
    print(f"\n{'='*60}")
    print(f"🐝 SWARM DASHBOARD [{format_time()} UTC]")
    print(f"{'='*60}")
    
    # Active conversations
    print(f"\n📋 Active Conversations:")
    convs = get_conversations(headers)
    active = [c for c in convs if c.get("sandbox_status", c.get("status")) in ["RUNNING", "WORKING"]]
    for c in active:
        title = c.get("title", "untitled")[:45]
        status = c.get("sandbox_status", c.get("status", "?"))
        created = (c.get("created_at", "")[11:19] if c.get("created_at") else "?")
        print(f"  [{status:8}] {title:45} | {created}")
    
    print(f"\n  Total active: {len(active)}/8")
    
    # Current swarm log
    log_file = get_current_swarm_log()
    if log_file:
        print(f"\n📝 Current Swarm Log: {log_file.name}")
        print(f"  Path: {log_file}")
        lines = log_file.read_text().strip().split("\n")
        print(f"  Lines: {len(lines)}")
        
        # Show last 15 entries
        print(f"\n  Last entries:")
        entry_lines = []
        for line in reversed(lines):
            if line.startswith("## "):
                if entry_lines:
                    break
                entry_lines = [line]
            elif entry_lines and line.strip():
                entry_lines.append(line)
        
        for line in reversed(entry_lines[:10]):
            print(f"    {line[:75]}")
    
    print(f"\n{'='*60}")

def main():
    parser = argparse.ArgumentParser(description="Swarm Dashboard")
    parser.add_argument("--once", action="store_true", help="One-shot view")
    parser.add_argument("--interval", type=int, default=10, help="Refresh interval (seconds)")
    parser.add_argument("--tail", type=int, default=0, help="Show last N lines of log")
    args = parser.parse_args()
    
    if args.tail:
        log_file = get_current_swarm_log()
        if log_file:
            lines = log_file.read_text().strip().split("\n")
            for line in lines[-args.tail:]:
                print(line)
        return
    
    if args.once:
        print_dashboard()
        return
    
    # Watch mode
    print("🐝 Swarm Dashboard — Press Ctrl+C to exit")
    try:
        while True:
            os.system('clear' if os.name == 'posix' else 'cls')
            print_dashboard()
            time.sleep(args.interval)
    except KeyboardInterrupt:
        print("\n👋 Dashboard closed")

if __name__ == "__main__":
    main()