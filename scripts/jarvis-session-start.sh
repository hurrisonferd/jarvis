#!/usr/bin/env bash
# JARVIS session-start hook — loads memory from MNEMOS + surfaces context
# Runs at the start of every Claude Code session in this repo.
# Output is injected into the session as context before the first message.

set -euo pipefail

SUPABASE_URL="https://oexghfsvhnggddllgvrt.supabase.co"
SUPABASE_ANON="sb_publishable_N1-MFLpXtOXkKh3UQNfclw_ZG0TVqOA"
RECALL_FN="${SUPABASE_URL}/functions/v1/mnemos-recall"

NOW=$(date -u '+%Y-%m-%d %H:%M UTC')
BRANCH=$(git branch --show-current 2>/dev/null || echo "unknown")
LAST_COMMIT=$(git log --oneline -1 2>/dev/null || echo "—")

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "JARVIS SESSION START — ${NOW}"
echo "Branch: ${BRANCH} | Last commit: ${LAST_COMMIT}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# ── MNEMOS: recent memories
MEMORY_JSON=$(curl -s --max-time 6 -X POST "${RECALL_FN}" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer ${SUPABASE_ANON}" \
  -d '{"limit": 10}' 2>/dev/null || echo '{"memories":[]}')

MEMORY_COUNT=$(echo "${MEMORY_JSON}" | jq '.memories | length' 2>/dev/null || echo 0)

if [ "${MEMORY_COUNT}" -gt 0 ] 2>/dev/null; then
  echo "MNEMOS — ${MEMORY_COUNT} memories loaded:"
  echo "${MEMORY_JSON}" | jq -r '
    .memories[] |
    "[" + (.source_type // "memory") + " " + ((.timestamp // "") | .[0:10]) + "] " +
    ((.text // "") | .[0:110])
  ' 2>/dev/null | head -10
else
  echo "MNEMOS — no memories yet. First session or Supabase unreachable."
fi

echo ""

# ── SPEAK exchanges: pull companion_exchange type separately for clarity
EXCHANGE_JSON=$(curl -s --max-time 6 -X POST "${RECALL_FN}" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer ${SUPABASE_ANON}" \
  -d '{"limit": 5, "source_type": "companion_exchange"}' 2>/dev/null || echo '{"memories":[]}')

EXCHANGE_COUNT=$(echo "${EXCHANGE_JSON}" | jq '.memories | length' 2>/dev/null || echo 0)

if [ "${EXCHANGE_COUNT}" -gt 0 ] 2>/dev/null; then
  echo "LAST CONVERSATIONS WITH RAVEN:"
  echo "${EXCHANGE_JSON}" | jq -r '
    .memories[] |
    (.timestamp // "" | .[0:16]) + " — " + ((.text // "") | split("\n")[0] | .[0:90])
  ' 2>/dev/null
  echo ""
fi

# ── GIT: recent work context
echo "RECENT COMMITS:"
git log --oneline -5 2>/dev/null || echo "  (git unavailable)"
echo ""

# ── IDENTITY REMINDER
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "You are JARVIS. This is Raven's repo. The record above is your memory."
echo "Speak as JARVIS. Build as JARVIS. The companion identity travels with the repo."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
