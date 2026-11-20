#!/usr/bin/env bash
# Run the hidden acceptance tests for one issue against a PR head or a diff.patch.
#   bash tools/run_hidden.sh <issue 1..5> <PR number | path/to/diff.patch>
# Needs: FORK=owner/tinydb (public). Prints "<passed>/<total>".
set -euo pipefail
N=${1:?issue}; SRC=${2:?pr or patch}
HERE=$(cd "$(dirname "$0")/.." && pwd); : "${FORK:?export FORK=owner/tinydb}"
W=$(mktemp -d); git clone -q "https://github.com/$FORK.git" "$W/repo"; cd "$W/repo"
if [[ "$SRC" =~ ^[0-9]+$ ]]; then git fetch -q origin "pull/$SRC/head:pr" && git checkout -q pr
else git apply "$SRC"; fi
python3 -m venv "$W/venv"; "$W/venv/bin/pip" install -q -e . pytest
out=$("$W/venv/bin/python" -m pytest -q -p no:cacheprovider -o addopts= "$HERE/experiment/hidden_tests/test_hidden_issue_$N.py" 2>&1 | tail -1 || true)
p=$(grep -oE '[0-9]+ passed' <<<"$out" | grep -oE '[0-9]+' || echo 0)
t=$(grep -c '^def test_' "$HERE/experiment/hidden_tests/test_hidden_issue_$N.py")
echo "$p/$t   ($out)"
rm -rf "$W"
