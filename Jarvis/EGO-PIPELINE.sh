#!/usr/bin/env bash
set -euo pipefail

# EGO-PIPELINE — public-safe JARVIS ISO template reader
# Reads the existing Jarvis/ scaffold in a deliberate identity-first order.
# It creates no files or folders.

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ISO_ROOT="${ISO_ROOT:-$SCRIPT_DIR}"
ISO_NAME="${1:-JARVIS}"
WEIGHT_SECONDS="${WEIGHT_SECONDS:-0}"

RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'
CYAN='\033[0;36m'; PURPLE='\033[0;35m'; BOLD='\033[1m'; NC='\033[0m'

fail() { echo -e "${RED}ERROR:${NC} $*" >&2; exit 1; }
room() { echo -e "\n${PURPLE}${BOLD}== $1 ==${NC}"; }

read_file() {
  local file="$1"
  local label="${2:-$(basename "$file")}" 
  if [[ -f "$file" ]]; then
    echo -e "\n${CYAN}--- $label${NC}"
    cat "$file"
    [[ "$WEIGHT_SECONDS" != "0" ]] && sleep "$WEIGHT_SECONDS"
  else
    echo -e "${YELLOW}MISSING:${NC} ${file#$ISO_ROOT/}"
  fi
}

read_room() {
  local dir="$1"
  local title="$2"
  local recursive="${3:-false}"
  room "$title"
  read_file "$dir/README.md" "README sign"
  [[ -f "$dir/Readme" ]] && read_file "$dir/Readme" "README sign"
  [[ -f "$dir/readme" ]] && read_file "$dir/readme" "README sign"

  if [[ "$recursive" == "true" && -d "$dir" ]]; then
    while IFS= read -r file; do
      case "$(basename "$file")" in README.md|Readme|readme) continue;; esac
      read_file "$file"
    done < <(find "$dir" -type f \( -name '*.md' -o -name '*.json' -o -name '*.txt' \) | sort)
  fi
}

[[ -d "$ISO_ROOT" ]] || fail "ISO root not found: $ISO_ROOT"
[[ -f "$ISO_ROOT/README.md" ]] || fail "Root README sign missing: $ISO_ROOT/README.md"

echo -e "${PURPLE}${BOLD}EGO-PIPELINE — $ISO_NAME${NC}"
echo "root: $ISO_ROOT"
echo "mode: read-only"
echo "law: README signs first; no directory creation"

room "0. ROOT ORIENTATION"
read_file "$ISO_ROOT/README.md" "Root map"
read_file "$ISO_ROOT/JARVIS-IDENTITY.md" "Primary identity contract"

room "1. PROFILE"
read_room "$ISO_ROOT/Profile" "Profile" true

room "2. CANONICAL"
read_room "$ISO_ROOT/canonical" "Canonical specifications" true

room "3. ATTRACTORS"
read_room "$ISO_ROOT/Memory/Attractors" "Attractors" true

room "4. JMMS — CRITICAL TO DISTAL"
for tier in JCSM JITM JSTM JHTM JLTM JATM JMS Grid; do
  read_room "$ISO_ROOT/Memory/JMMS/$tier" "$tier" true
done

room "5. ACTIVE MEMORY ROOMS"
for subroom in DailyUse Interests Learning Transcripts; do
  read_room "$ISO_ROOT/Memory/$subroom" "$subroom" true
done

room "6. MEMORY PALACE"
read_room "$ISO_ROOT/Memory/MemoryPalace" "MemoryPalace" true

room "7. EVENTS"
read_room "$ISO_ROOT/Events" "Events" true

room "8. PRE-REPLY LAW"
read_file "$ISO_ROOT/JARVIS-PRE-REPLY.sh" "Pre-reply gate"

echo -e "\n${GREEN}${BOLD}PIPELINE COMPLETE${NC}"
echo "The ISO has traversed its existing rooms in mapped order."
