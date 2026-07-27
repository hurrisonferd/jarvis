#!/usr/bin/env bash
set -euo pipefail

# Public-safe template of the JARVIS pre-reply orientation step.
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

cat "$ROOT/README.md"
cat "$ROOT/JARVIS-IDENTITY.md"
cat "$ROOT/Profile/README.md"
cat "$ROOT/Memory/JMMS/JCSM/README.md"
cat "$ROOT/Memory/JMMS/JITM/README.md"
cat "$ROOT/Memory/JMMS/JSTM/README.md"

echo "[JARVIS TEMPLATE] Oriented. Replace template content before runtime use."
