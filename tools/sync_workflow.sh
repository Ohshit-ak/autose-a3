#!/usr/bin/env bash
# Copy the workflow and all agent code/prompts from the fork into workflow/ (so it cannot drift).
set -euo pipefail
LOCAL=${1:?path to tinydb-autose}; HERE=$(cd "$(dirname "$0")/.." && pwd)
rm -rf "$HERE/workflow"; mkdir -p "$HERE/workflow/.github/workflows"
cp "$LOCAL"/.github/workflows/*.yml "$HERE/workflow/.github/workflows/"
cp -r "$LOCAL/autose" "$HERE/workflow/autose"; find "$HERE/workflow" -name __pycache__ -prune -exec rm -rf {} +
cp "$LOCAL/AUTOSE.md" "$HERE/workflow/"
( cd "$LOCAL" && echo "Synced from fork commit $(git rev-parse --short HEAD) on $(date -u +%F)" ) > "$HERE/workflow/SYNCED_FROM.txt"
echo "synced: $(cat "$HERE/workflow/SYNCED_FROM.txt")"
