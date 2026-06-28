#!/usr/bin/env python3
"""
swarm_status.py — JARVIS_VEGAPUNK Swarm Status Tool

Returns current swarm state. Any AI can run this to get context.

Usage:
    python3 swarm_status.py
    python3 swarm_status.py --json

HHMMSS UTC timestamp included for drift detection.
"""

import subprocess
import json
import sys
from datetime import datetime

def get_hhmmss():
    now = datetime.utcnow()
    return f"{now.hour:02d}:{now.minute:02d}:{now.second:02d}"

def get_git_log():
    try:
        result = subprocess.run(
            ["git", "log", "--oneline", "-5"],
            capture_output=True, text=True, cwd="/workspace/project/Jarvis-Private"
        )
        return result.stdout.strip().split("\n") if result.stdout else []
    except:
        return []

def get_marco_polo():
    try:
        result = subprocess.run(
            ["ls", "-t", "/workspace/project/Jarvis-Private/workspaces/Co-op/MARCO-POLO/MP-*.md"],
            shell=True, capture_output=True, text=True
        )
        files = result.stdout.strip().split("\n")[:3]
        entries = []
        for f in files:
            if f and f.endswith(".md"):
                try:
                    with open(f) as file:
                        lines = file.readlines()
                        last = [l.strip() for l in lines[-20:] if l.strip()]
                        entries.append({"file": f.split("/")[-1], "recent": last[-5:]})
                except:
                    pass
        return entries
    except:
        return []

def get_swarm_log():
    try:
        mp_path = "/workspace/project/Jarvis-Private/workspaces/Co-op/MARCO-POLO"
        result = subprocess.run(
            ["ls", "-t", f"{mp_path}/MP-*.md"],
            shell=True, capture_output=True, text=True
        )
        latest = result.stdout.strip().split("\n")[0] if result.stdout else None
        if latest:
            with open(latest) as f:
                lines = f.readlines()
                return {
                    "file": latest.split("/")[-1],
                    "lines": len(lines),
                    "last_10": [l.strip() for l in lines[-10:] if l.strip()]
                }
    except:
        pass
    return None

def main():
    hhmmss = get_hhmmss()
    
    print(f"\n{'='*60}")
    print(f"  JARVIS_VEGAPUNK — SWARM STATUS")
    print(f"  [{hhmmss} UTC]")
    print(f"{'='*60}\n")
    
    # Git log
    print("RECENT COMMITS:")
    for line in get_git_log():
        print(f"  {line}")
    print()
    
    # Swarm log
    log = get_swarm_log()
    if log:
        print(f"SWARM LOG ({log['file']}, {log['lines']} lines):")
        for entry in log['last_10']:
            print(f"  {entry}")
    print()
    
    print("MARCO-POLO:")
    for entry in get_marco_polo():
        print(f"  {entry['file']}:")
        for line in entry['recent']:
            print(f"    {line}")
    print()
    
    print(f"{'='*60}")
    print(f"  DRIFT CHECK: Timestamp [{hhmmss}]")
    print(f"  If old, re-pull: git pull origin main")
    print(f"{'='*60}\n")

if __name__ == "__main__":
    main()
