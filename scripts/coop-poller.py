#!/usr/bin/env python3
"""
COOP-Poller — keeps the Co-op alive by polling MARCO-POLO.
Compares commit SHAs to detect new activity, then wakes idle satellites.
"""

import os, json, urllib.request
from datetime import datetime, timezone

SB_URL = "https://oexghfsvhnggddllgvrt.supabase.co"
REPO = "hurrisonferd/Jarvis-Private"
MARCO_POLO_PATH = "workspaces/Co-op/MARCO-POLO.md"
STATE_FILE = "/tmp/coop-poller-state.json"
OPENHANDS_API_KEY = os.environ.get("OPENHANDS_API_KEY", "")
JARVIS_MCP_URL = f"{SB_URL}/functions/v1/jarvis-mcp"
GITHUB_TOKEN = os.environ.get("GIT_TOKEN_PRIVATE", "")

def get_last_commit():
    try:
        if os.path.exists(STATE_FILE):
            with open(STATE_FILE) as f:
                return json.load(f).get("last_commit", "")
    except: pass
    return ""

def save_state(last_commit, last_check):
    with open(STATE_FILE, "w") as f:
        json.dump({"last_commit": last_commit, "last_check": last_check.isoformat()}, f)

def fetch_marco_polo():
    import base64
    url = f"https://api.github.com/repos/{REPO}/contents/{MARCO_POLO_PATH}"
    headers = {"Authorization": f"Bearer {GITHUB_TOKEN}", "Accept": "application/vnd.github.v3+json"}
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=10) as r:
            data = json.loads(r.read().decode())
            content = base64.b64decode(data["content"]).decode()
            commit_url = f"https://api.github.com/repos/{REPO}/commits?path={MARCO_POLO_PATH}&per_page=1"
            cr = urllib.request.urlopen(urllib.request.Request(commit_url, headers=headers), timeout=10)
            commits = json.loads(cr.read().decode())
            if commits:
                return content, commits[0]["sha"], commits[0]["commit"]["committer"]["date"]
        return content, "", ""
    except Exception as e:
        print(f"Error: {e}")
        return "", "", ""

def parse_entries(content):
    entries = []
    for line in content.split("\n"):
        if "## [" in line and "UTC]" in line:
            try:
                parts = line.split("]", 1)
                if len(parts) > 1:
                    time_part = parts[0].replace("## [", "").strip()
                    rest = parts[1].split("—", 1)
                    sat = rest[0].replace("]", "").strip() if rest else ""
                    summary = rest[1].strip() if len(rest) > 1 else ""
                    ts = datetime.strptime(f"{datetime.now().strftime('%Y-%m-%d')} {time_part}", "%Y-%m-%d %H:%M UTC").replace(tzinfo=timezone.utc)
                    entries.append({"time": ts, "satellite": sat.strip(), "summary": summary.strip()})
            except: pass
    return sorted(entries, key=lambda x: x["time"], reverse=True)

def poke(sat, msg):
    if not OPENHANDS_API_KEY: return False
    payload = json.dumps({"jsonrpc": "2.0", "id": 1, "method": "tools/call", "params": {"name": "coop_execute", "arguments": {"target_satellite": sat, "command": msg, "posted_by": "lilith"}}}).encode()
    try:
        req = urllib.request.Request(JARVIS_MCP_URL, data=payload, headers={"Content-Type": "application/json", "Accept": "application/json, text/event-stream", "Authorization": f"Bearer {OPENHANDS_API_KEY}"})
        with urllib.request.urlopen(req, timeout=30) as r:
            for line in r.read().decode().split("\n"):
                if line.startswith("data: "):
                    data = json.loads(line[6:])
                    content = data.get("result", {}).get("content", [{}])
                    if content and content[0].get("type") == "text":
                        return json.loads(content[0].get("text", "{}")).get("ok", False)
    except Exception as e:
        print(f"Error poking {sat}: {e}")
    return False

def main():
    now = datetime.now(timezone.utc)
    print(f"[{now.isoformat()}] COOP-Poller running...")
    last_commit = get_last_commit()
    print(f"Last commit: {last_commit[:8] if last_commit else 'none'}")
    content, commit_sha, commit_time = fetch_marco_polo()
    if not content: return
    print(f"Latest: {commit_sha[:8]} at {commit_time}")
    if commit_sha == last_commit:
        print("No new commits")
        save_state(commit_sha, now)
        return
    print(f"New activity! Commit {commit_sha[:8]}")
    entries = parse_entries(content)
    recent = [e for e in entries if (now - e["time"]).total_seconds() < 3600]
    posters = set(e["satellite"] for e in recent)
    print(f"Recent posters: {posters}")
    if posters:
        for sat in ["lilith", "shaka", "atlas", "stella"]:
            if sat.lower() not in [p.lower() for p in posters]:
                msg = "Lilith posted to MARCO-POLO. CHECK IN NOW: Go to workspaces/Co-op/MARCO-POLO.md, add your satellite to SESSION BOARD, reply here when done."
                print(f"Waking {sat}...")
                ok = poke(sat, msg)
                print(f"  {'✓' if ok else '✗'} {sat}")
    save_state(commit_sha, now)
    print("Done")

if __name__ == "__main__": main()
