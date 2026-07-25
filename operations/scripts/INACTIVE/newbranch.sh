#!/usr/bin/env bash
# Always cut a new branch from a freshly-fetched origin/main.
# Avoids the squash-merge conflict from branching off a prior feature branch.
# Usage: operations/scripts/newbranch.sh <branch-name>
set -euo pipefail
name="${1:?usage: newbranch.sh <branch-name>}"
git fetch origin main --quiet
git checkout -B "$name" origin/main
echo "✓ cut '$name' from origin/main @ $(git rev-parse --short HEAD)"
