#!/usr/bin/env bash
# One-shot GitHub setup for the AutoSE fork. Run it YOURSELF (it uses your token).
#
#   export GH_TOKEN=<a token with repo + workflow scopes>   # e.g. the one git already uses
#   export FORK=Ohshit-ak/tinydb                             # your fork of msiemens/tinydb
#   bash tools/setup_github.sh /path/to/tinydb-autose
#
# Before running: fork https://github.com/msiemens/tinydb in the browser (keep the name 'tinydb').
# After running: add the secret GEMINI_API_KEY (Settings > Secrets and variables > Actions).
set -euo pipefail
LOCAL=${1:?path to local tinydb-autose repo}
: "${GH_TOKEN:?export GH_TOKEN}" "${FORK:?export FORK=owner/tinydb}"
HERE=$(cd "$(dirname "$0")/.." && pwd)
API=https://api.github.com
api() { # method path [json]
  curl -fsS -X "$1" -H "Authorization: Bearer $GH_TOKEN" -H "Accept: application/vnd.github+json" \
       -H "X-GitHub-Api-Version: 2022-11-28" "$API$2" ${3:+--data "$3"}; }

echo "== 0. token check (needs scopes: repo, workflow; you must be admin of $FORK)"
scopes=$(curl -fsSI -H "Authorization: Bearer $GH_TOKEN" $API/user | tr -d '\r' | sed -n 's/^x-oauth-scopes: //Ip')
echo "  token scopes: ${scopes:-<fine-grained token: make sure it has Contents, Workflows, Administration, Issues, Pull requests, Actions, Variables = read/write>}"
if [ -n "$scopes" ] && ! grep -q workflow <<<"$scopes"; then echo "ERROR: token lacks the 'workflow' scope (needed to push .github/workflows)"; exit 1; fi
api GET "/repos/$FORK" | python3 -c 'import json,sys;d=json.load(sys.stdin);assert d["permissions"]["admin"],"not admin";assert d.get("fork"),"not a fork";print("  repo ok:",d["full_name"],"fork of",d["parent"]["full_name"])'

echo "== 1. push main (edff96a + CI trim + AutoSE) and make it the default branch"
git -C "$LOCAL" push -f "https://x-access-token:${GH_TOKEN}@github.com/${FORK}.git" main:main
api PATCH "/repos/$FORK" '{"default_branch":"main","has_issues":true}' >/dev/null
api DELETE "/repos/$FORK/git/refs/heads/master" >/dev/null 2>&1 || true

echo "== 2. enable Actions; allow GITHUB_TOKEN to create PRs (needed by stage 5)"
api PUT "/repos/$FORK/actions/permissions" '{"enabled":true,"allowed_actions":"all"}' >/dev/null
api PUT "/repos/$FORK/actions/permissions/workflow" \
    '{"default_workflow_permissions":"read","can_approve_pull_request_reviews":true}' >/dev/null

echo "== 3. repository variables (models, budget)"
for kv in "AUTOSE_WORKER_MODEL=${AUTOSE_WORKER_MODEL:-gemini-2.5-flash}" \
          "AUTOSE_REVIEWER_MODEL=${AUTOSE_REVIEWER_MODEL:-gemini-2.5-pro}" \
          "AUTOSE_TOKEN_CAP=${AUTOSE_TOKEN_CAP:-2000000}"; do
  k=${kv%%=*}; v=${kv#*=}
  api POST "/repos/$FORK/actions/variables" "{\"name\":\"$k\",\"value\":\"$v\"}" >/dev/null 2>&1 || \
  api PATCH "/repos/$FORK/actions/variables/$k" "{\"name\":\"$k\",\"value\":\"$v\"}" >/dev/null
done

echo "== 4. labels"
for l in "autose:0e8a16" "autose:failed:b60205" "autose:changes-requested:d93f0b" \
         "autose:reviewer-approved:0e8a16" "autose:ready-for-human:1d76db"; do
  name=${l%:*}; color=${l##*:}
  api POST "/repos/$FORK/labels" "{\"name\":\"$name\",\"color\":\"$color\"}" >/dev/null 2>&1 || echo "  (label $name exists)"
done

echo "== 5. (branch protection is a separate step: tools/protect_main.sh, run it after the smoke run)"

echo "== 6. open the five issues (in order, so they get numbers #1..#5)"
for f in "$HERE"/experiment/issues/issue-*.md; do
  python3 - "$f" > /tmp/autose_issue.json <<'PY'
import json, re, sys
t = open(sys.argv[1]).read()
m = re.match(r"---\n(.*?)\n---\n(.*)", t, re.S)
title = re.search(r'title:\s*"(.*)"', m.group(1)).group(1)
print(json.dumps({"title": title, "body": m.group(2).strip()}))
PY
  api POST "/repos/$FORK/issues" "$(cat /tmp/autose_issue.json)" | python3 -c 'import json,sys;d=json.load(sys.stdin);print("  issue", d["number"], d["title"])'
done

echo "== 7. seeded reviewer-check PRs (s1..s5)"
TITLES=([1]="Allow count() without a query" [2]="Reset held tables on drop_table/drop_tables" \
        [3]="Don't crash when comparing mixed types" [4]="Add operations.append" \
        [5]="Don't skip ids after a failed insert_multiple")
TMP=$(mktemp -d); git clone -q "$LOCAL" "$TMP/wt"
for k in 1 2 3 4 5; do
  git -C "$TMP/wt" checkout -q -B "seeded/s$k" main
  git -C "$TMP/wt" apply "$HERE/experiment/seeded_prs/s$k.patch"
  git -C "$TMP/wt" add -A
  git -C "$TMP/wt" -c user.name="seeded-author" -c user.email="seeded@users.noreply.github.com" commit -qm "seeded PR s$k"
  git -C "$TMP/wt" push -q -f "https://x-access-token:${GH_TOKEN}@github.com/${FORK}.git" "seeded/s$k:seeded/s$k"
  body=$(python3 -c 'import json,sys;print(json.dumps(open(sys.argv[1]).read()))' "$HERE/experiment/seeded_prs/s$k.body.md")
  title=${TITLES[$k]}
  api POST "/repos/$FORK/pulls" "{\"title\":\"[seeded s$k] $title\",\"head\":\"seeded/s$k\",\"base\":\"main\",\"body\":$body}" \
    | python3 -c 'import json,sys;d=json.load(sys.stdin);print("  PR", d["number"], d["html_url"])'
done
rm -rf "$TMP"
echo
echo "Done. Remaining manual steps:"
echo "  * Settings > Secrets and variables > Actions > New secret: GEMINI_API_KEY"
echo "  * Set a spending cap / budget on the Google AI Studio / Cloud billing project"
echo "  * Smoke run: add label 'autose' to issue #3, check the run end to end"
echo "  * Then: bash tools/protect_main.sh   (no direct pushes to main)"
