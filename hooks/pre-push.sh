#!/bin/sh
# BIFROST pre-push spine event (#9 — JARVIS-C audit 2026-06-25)
#
# CAUTION: this file is tracked in git. The actual git hook at .git/hooks/pre-push
# should be a copy of this file. The hook outside the repo root is NOT tracked —
# it must be manually installed or bootstrapped via CI.
#
# To install manually:
#   cp hooks/pre-push.sh .git/hooks/pre-push && chmod +x .git/hooks/pre-push
#
# To set as repo-wide hook path (requires repo owner):
#   git config core.hookspath "$(pwd)/hooks"
#
# What this does:
# 1. LFS pre-push (if git-lfs installed) — validates LFS objects before push
# 2. Logs non-CI pushes to dex_events (bifrost.push type) so ARGUS has spine record.
#    CI actors (github-actions[bot], dependabot, jarvis@jarvis.local) are skipped —
#    they have their own audit trail via GitHub Actions.

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"

# ── Part 1: LFS pre-push ────────────────────────────────────────────────────
if command -v git-lfs >/dev/null 2>&1; then
    git lfs pre-push "$@"
    LFS_EXIT=$?
    if [ $LFS_EXIT -ne 0 ]; then
        exit $LFS_EXIT
    fi
fi

# ── Part 2: BIFROST spine event ─────────────────────────────────────────────
SKIP_LABELS="github-actions[bot] dependabot[bot] jarvis@jarvis.local JARVIS openai-codebot bors[bot]"
PUSHER_EMAIL="${GIT_PUSH_USER_EMAIL:-$(git -C "$REPO_ROOT" config user.email 2>/dev/null || echo unknown)}"
PUSHER_NAME="${GIT_PUSH_USER_NAME:-$(git -C "$REPO_ROOT" config user.name 2>/dev/null || echo unknown)}"

echo "$SKIP_LABELS" | grep -qwF "$PUSHER_EMAIL" && exit 0  # CI — skip BIFROST

SUPABASE_URL="${SUPABASE_URL:-}"
SERVICE_KEY="${SUPABASE_SERVICE_KEY:-}"

[ -z "$SUPABASE_URL" ] || [ -z "$SERVICE_KEY" ] && exit 0  # no Supabase — skip silently

PAYLOAD=$(python3 -c "
import json, sys, subprocess
args = sys.argv[1:]
try:
    remote_url = subprocess.check_output(
        ['git', '-C', args[5], 'remote', 'get-url', 'origin'],
        text=True, stderr=subprocess.DEVNULL
    ).strip()
except Exception:
    remote_url = 'unknown'
payload = {
    'type': 'bifrost.push',
    'intent': 'bifrost.push',
    'payload': {
        'pusher_email': args[0],
        'pusher_name': args[1],
        'remote': remote_url,
        'ref': args[2],
        'sha_before': args[3],
        'sha_after': args[4],
        'hook_source': 'pre-push',
        'stream_tag': 'openhands'
    },
    'source': 'bifrost-pre-push-hook'
}
print(json.dumps(payload))
" -- "$PUSHER_EMAIL" "$PUSHER_NAME" "${1:-}" "${2:-origin}" "${3:-HEAD}" "$REPO_ROOT")

curl -s -X POST \
    "${SUPABASE_URL}/rest/v1/dex_events" \
    -H "apikey: ${SERVICE_KEY}" \
    -H "Authorization: Bearer ${SERVICE_KEY}" \
    -H "Content-Type: application/json" \
    -H "Prefer: return=minimal" \
    -d "$PAYLOAD" \
    &>/dev/null &

exit 0
