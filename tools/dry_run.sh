#!/usr/bin/env bash
# Local dry run of stages 1-4 with the real Gemini API, no GitHub access.
# Useful to smoke-test prompts before spending Actions runs. NOT counted as a result.
#   export GEMINI_API_KEY=...   (in your own shell)
#   bash tools/dry_run.sh /path/to/tinydb-autose 3
set -euo pipefail
LOCAL=${1:?path to tinydb-autose}; N=${2:?issue number 1..5}
HERE=$(cd "$(dirname "$0")/.." && pwd)
: "${GEMINI_API_KEY:?export GEMINI_API_KEY in your shell}"
W=$(mktemp -d); git clone -q "$LOCAL" "$W/repo"; cd "$W/repo"
python3 -m venv "$W/venv"; "$W/venv/bin/pip" install -q -r autose/requirements.txt -e .
f=$(ls "$HERE"/experiment/issues/issue-"$N"-*.md)
python3 - "$f" "$N" > "$W/issue.json" <<'PY'
import json, re, sys
t = open(sys.argv[1]).read(); m = re.match(r"---\n(.*?)\n---\n(.*)", t, re.S)
print(json.dumps({"number": int(sys.argv[2]), "title": re.search(r'title:\s*"(.*)"', m.group(1)).group(1),
                  "body": m.group(2).strip()}))
PY
"$W/venv/bin/python" -m autose.controller --issue "$N" --issue-file "$W/issue.json" ${VARIANT:+--variant $VARIANT}
echo "artifacts: $W/repo/.autose-run"
