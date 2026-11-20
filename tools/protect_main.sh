#!/usr/bin/env bash
# Protect main (no direct pushes; PR required, admins included). Run after the smoke run.
# Afterwards, workflow fixes must go through a PR that you merge yourself.
set -euo pipefail
: "${GH_TOKEN:?}" "${FORK:?}"
curl -fsS -X PUT -H "Authorization: Bearer $GH_TOKEN" -H "Accept: application/vnd.github+json" \
  "https://api.github.com/repos/$FORK/branches/main/protection" --data '{
  "required_status_checks": null,
  "enforce_admins": true,
  "required_pull_request_reviews": {"required_approving_review_count": 0},
  "restrictions": null, "allow_force_pushes": false, "allow_deletions": false}' >/dev/null
echo "main is protected on $FORK"
