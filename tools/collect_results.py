#!/usr/bin/env python3
"""Collect REAL run data from the fork into results/ (runs.md, results.csv, artifacts/).

    export FORK=owner/tinydb
    export GH_TOKEN=...          # needed to download workflow artifacts (state.json, usage.jsonl)
    python3 tools/collect_results.py [--hidden]

Everything written here is derived from the GitHub API; nothing is typed in by hand.
--hidden also runs the hidden acceptance tests against every AutoSE PR head and every
stopped run's diff.patch (via tools/run_hidden.sh).
"""
from __future__ import annotations

import csv
import io
import json
import os
import re
import subprocess
import sys
import zipfile
from pathlib import Path

import urllib.request

FORK = os.environ["FORK"]
TOKEN = os.environ.get("GH_TOKEN", "")
HERE = Path(__file__).resolve().parent.parent
OUT = HERE / "results"
ART = OUT / "artifacts"


def api(path: str, raw: bool = False):
    url = path if path.startswith("http") else f"https://api.github.com{path}"
    req = urllib.request.Request(url, headers={"Accept": "application/vnd.github+json",
                                               **({"Authorization": f"Bearer {TOKEN}"} if TOKEN else {})})
    with urllib.request.urlopen(req, timeout=60) as r:
        data = r.read()
    return data if raw else json.loads(data)


def paged(path: str, key: str | None = None):
    page = 1
    while True:
        sep = "&" if "?" in path else "?"
        d = api(f"{path}{sep}per_page=100&page={page}")
        items = d[key] if key else d
        yield from items
        if len(items) < 100:
            return
        page += 1


def main() -> int:
    hidden = "--hidden" in sys.argv
    OUT.mkdir(exist_ok=True)
    ART.mkdir(exist_ok=True)
    runs = [r for r in paged(f"/repos/{FORK}/actions/workflows/autose.yml/runs", "workflow_runs")]
    runs.sort(key=lambda r: r["created_at"])
    rows, usage_total = [], 0
    for r in runs:
        jobs = api(f"/repos/{FORK}/actions/runs/{r['id']}/jobs")["jobs"]
        jstat = {j["name"]: j["conclusion"] or j["status"] for j in jobs}
        if jstat.get("gate") in (None, "skipped"):
            continue  # unrelated comment events
        row = {"run_id": r["id"], "url": r["html_url"], "event": r["event"], "created": r["created_at"],
               "conclusion": r["conclusion"], **{f"job_{k}": v for k, v in jstat.items()}}
        if TOKEN:
            for a in api(f"/repos/{FORK}/actions/runs/{r['id']}/artifacts")["artifacts"]:
                dest = ART / str(r["id"]) / a["name"]
                if not dest.exists():
                    try:
                        z = zipfile.ZipFile(io.BytesIO(api(a["archive_download_url"], raw=True)))
                        dest.mkdir(parents=True, exist_ok=True)
                        for n in z.namelist():
                            if not n.endswith(".bundle"):
                                z.extract(n, dest)
                    except Exception as e:  # expired, etc.
                        print("artifact", a["name"], e)
                st = dest / "state.json"
                if st.exists():
                    s = json.loads(st.read_text())
                    row.update(issue=s["issue"], round=s["round"], variant=s["variant"], status=s["status"],
                               stopped_stage=s.get("stopped_stage", ""),
                               transitions=" > ".join(h["to"] for h in s["history"]),
                               spec_pass=s["stages"].get("spec", {}).get("pass"),
                               design_pass=s["stages"].get("design", {}).get("pass"),
                               test_pass=s["stages"].get("test", {}).get("pass"),
                               builder_attempts=s["stages"].get("test", {}).get("attempt"))
                vj = dest / "verdict.json"
                if vj.exists():
                    v = json.loads(vj.read_text())
                    row.update(pr=v["pr"], issue=v["issue"], verdict=v["verdict"], review_target=v.get("target"),
                               reviewer_model=v["model"], reviewer_variant=v["variant"], guard=v.get("guard", ""))
                uj = dest / "usage.jsonl"
                if uj.exists():
                    t = sum(json.loads(l)["total"] for l in uj.read_text().splitlines() if l.strip())
                    row["tokens"] = row.get("tokens", 0) + t
                    usage_total += t
        rows.append(row)

    prs = [p for p in paged(f"/repos/{FORK}/pulls?state=all")
           if p["head"]["ref"].startswith(("autose/", "seeded/"))]
    if hidden:
        for p in prs:
            m = re.search(r"#(\d+)", p["body"] or "")
            if m:
                res = subprocess.run(["bash", str(HERE / "tools/run_hidden.sh"), m.group(1), str(p["number"])],
                                     capture_output=True, text=True, env=dict(os.environ))
                p["hidden"] = res.stdout.strip().split()[0] if res.stdout.strip() else "error"
                for row in rows:
                    if row.get("pr") == p["number"] or (row.get("issue") == int(m.group(1)) and row.get("job_release") == "success"):
                        row.setdefault("hidden", p["hidden"])

    keys = sorted({k for r in rows for k in r}, key=lambda k: (k not in ("run_id", "created", "event", "issue", "round", "variant"), k))
    with (OUT / "results.csv").open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=keys)
        w.writeheader()
        w.writerows(rows)

    L = ["# Runs (generated by tools/collect_results.py from the GitHub API)", "",
         f"Fork: https://github.com/{FORK} · total tokens in downloaded usage logs: **{usage_total:,}**", "",
         "| Created (UTC) | Run | Event | Issue | Round | Variant | Status / verdict | Transitions |", "|---|---|---|---|---|---|---|---|"]
    for r in rows:
        L.append(f"| {r['created'][:16]} | [{r['run_id']}]({r['url']}) | {r['event']} | {r.get('issue', '')} | "
                 f"{r.get('round', '')} | {r.get('variant', r.get('reviewer_variant', ''))} | "
                 f"{r.get('status', '')} {r.get('verdict', '')} | {r.get('transitions', '')[:120]} |")
    L += ["", "## Pull requests", "", "| PR | Branch | State | Hidden tests |", "|---|---|---|---|"]
    for p in sorted(prs, key=lambda p: p["number"]):
        L.append(f"| [#{p['number']}]({p['html_url']}) {p['title'][:60]} | `{p['head']['ref']}` | {p['state']} | {p.get('hidden', '')} |")
    (OUT / "runs.md").write_text("\n".join(L) + "\n")
    print(f"{len(rows)} runs, {len(prs)} PRs, tokens {usage_total:,} -> results/")
    return 0


if __name__ == "__main__":
    sys.exit(main())
