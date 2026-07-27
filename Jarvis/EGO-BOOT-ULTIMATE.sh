#!/usr/bin/env bash
set -euo pipefail

# EGO-BOOT-ULTIMATE — public-safe JARVIS ISO boot template
# Coordinates orientation, identity loading, memory routing, full pipeline,
# and the pre-reply gate. It is read-only and creates no directories.

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ISO_ROOT="${ISO_ROOT:-$SCRIPT_DIR}"
ISO_NAME="${1:-JARVIS}"
RUN_PIPELINE="${RUN_PIPELINE:-true}"
WEIGHT_SECONDS="${WEIGHT_SECONDS:-0}"

RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'
CYAN='\033[0;36m'; PURPLE='\033[0;35m'; WHITE='\033[1;37m'
BOLD='\033[1m'; NC='\033[0m'

fail() { echo -e "${RED}ERROR:${NC} $*" >&2; exit 1; }
step() { echo -e "\n${PURPLE}${BOLD}[$1] $2${NC}"; }
show() {
  local file="$1"; local label="$2"
  if [[ -f "$file" ]]; then
    echo -e "${CYAN}$label:${NC} ${file#$ISO_ROOT/}"
    cat "$file"
    [[ "$WEIGHT_SECONDS" != "0" ]] && sleep "$WEIGHT_SECONDS"
  else
    echo -e "${YELLOW}MISSING:${NC} ${file#$ISO_ROOT/}"
  fi
}

[[ -d "$ISO_ROOT" ]] || fail "ISO root not found: $ISO_ROOT"
[[ -f "$ISO_ROOT/README.md" ]] || fail "Root README sign missing"
[[ -f "$ISO_ROOT/JARVIS-IDENTITY.md" ]] || fail "Identity file missing"
[[ -f "$ISO_ROOT/EGO-PIPELINE.sh" ]] || fail "EGO-PIPELINE.sh missing"

printf '\n'
echo -e "${PURPLE}${BOLD}╔══════════════════════════════════════════════╗${NC}"
echo -e "${PURPLE}${BOLD}║ EGO-BOOT-ULTIMATE — ${WHITE}$ISO_NAME${PURPLE}              ║${NC}"
echo -e "${PURPLE}${BOLD}╚══════════════════════════════════════════════╝${NC}"
echo "root: $ISO_ROOT"
echo "mode: public template / read-only"

step "0" "STRUCTURAL SAFETY"
echo "FIND FIRST. VERIFY EXACTLY. USE WHAT EXISTS."
echo "This boot reads the current scaffold and never creates folders."

step "1" "ROOT README — ENTER THE MIND MAP"
show "$ISO_ROOT/README.md" "Root sign"

step "2" "IDENTITY LOADING"
show "$ISO_ROOT/JARVIS-IDENTITY.md" "Identity contract"

step "3" "PROFILE + CANONICAL ORIENTATION"
show "$ISO_ROOT/Profile/README.md" "Profile sign"
show "$ISO_ROOT/canonical/README.md" "Canonical sign"

step "4" "CRITICAL MEMORY — JCSM"
show "$ISO_ROOT/Memory/JMMS/JCSM/README.md" "Core-self memory sign"

step "5" "JUST-IN-TIME + SESSION MEMORY"
show "$ISO_ROOT/Memory/JMMS/JITM/README.md" "Just-in-time memory sign"
show "$ISO_ROOT/Memory/JMMS/JSTM/README.md" "Short-term memory sign"

step "6" "ATTRACTOR ORIENTATION"
show "$ISO_ROOT/Memory/Attractors/README.md" "Attractor sign"

step "7" "FULL EGO PIPELINE"
if [[ "$RUN_PIPELINE" == "true" ]]; then
  ISO_ROOT="$ISO_ROOT" WEIGHT_SECONDS="$WEIGHT_SECONDS" \
    bash "$ISO_ROOT/EGO-PIPELINE.sh" "$ISO_NAME"
else
  echo "Skipped because RUN_PIPELINE=$RUN_PIPELINE"
fi

step "8" "PRE-REPLY GATE"
if [[ -x "$ISO_ROOT/JARVIS-PRE-REPLY.sh" ]]; then
  bash "$ISO_ROOT/JARVIS-PRE-REPLY.sh"
else
  show "$ISO_ROOT/JARVIS-PRE-REPLY.sh" "Pre-reply instructions"
fi

step "9" "BOOT RECEIPT"
echo -e "${GREEN}${BOLD}BOOT COMPLETE${NC}"
echo "identity: $ISO_NAME"
echo "root: $ISO_ROOT"
echo "pipeline: $RUN_PIPELINE"
echo "directories created: 0"
echo "next action: respond through the loaded identity, memory map, and pre-reply gate"
