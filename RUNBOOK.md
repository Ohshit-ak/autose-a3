# Runbook: what is left, in order

Everything in both local repos is committed **locally only**. Nothing has been pushed, and no real
run exists yet. Every result in the report must come from the steps below.

## 0. Today
- [ ] **Decide on an extension.** It must be requested *before* 21 Nov 23:59 IST. A1 already used 1 of
      the 3 days. Each real run takes about 10–20 minutes, and the full set is about 20 runs.
- [ ] Gemini: in AI Studio / Cloud billing, **set a spending cap** for the project. Note it in README.md
      ("Safety and cost").
- [ ] Check which models your key can use (the reviewer must be different from the worker):
      `curl -s "https://generativelanguage.googleapis.com/v1beta/models?key=$GEMINI_API_KEY" | grep '"name"'`.
      Defaults are now `gemini-3.5-flash` (workers) and `gemini-3.6-flash` (reviewer), see ADR-011. If one stops answering, set `AUTOSE_REVIEWER_MODEL`
      to the strongest model you have, and write that down.
- [ ] Rough request budget: one full run ≈ 100–200 model calls. The plan is 10 pipeline runs, 10
      seeded reviews and some rework rounds. The free tier will probably hit daily limits, so use a paid
      tier with the cap.

## 1. Local dry run (catches SDK or prompt errors before any Actions run)
```bash
export GEMINI_API_KEY=...            # in YOUR shell
cd ~/Desktop/ASE/assignment-3/2024111004_AutoSE_A3
bash tools/dry_run.sh ../tinydb-autose 3
```
This is not a result, it only proves the agents run. Paste any traceback back to Claude.

## 2. GitHub setup (fork)
1. In the browser, fork https://github.com/msiemens/tinydb as `Ohshit-ak/tinydb`.
2. Run:
```bash
export GH_TOKEN=...                  # classic token with repo + workflow scopes
export FORK=Ohshit-ak/tinydb
bash tools/setup_github.sh ../tinydb-autose
```
   The script pushes `main`, makes it the default branch, enables Actions and Issues, lets
   GITHUB_TOKEN open PRs, sets the variables and labels, opens issues #1–#5 and seeded PRs #6–#10.
   **Check that the issue numbers match the files** (the hidden tests depend on them) and that
   each seeded PR's `Fixes #k` points to the right issue.
3. Settings → Secrets and variables → Actions → **New secret `GEMINI_API_KEY`**.

## 3. Smoke run, then protect main
- [ ] Add the label `autose` to **issue #3** (the simplest one). Watch the run all the way through:
      ack comment → agents → release (PR opened) → ci + "AutoSE CI (stage 5)" status on the PR →
      review posted → maybe a rework dispatch.
- [ ] If something breaks, fix it locally in `tinydb-autose` and push to `main` (still unprotected).
- [ ] `bash tools/protect_main.sh` (no direct pushes from now on).

## 4. Result runs (all real, all linkable)
- [ ] E2 variant A: label `autose` on issues #1, #2, #4, #5 (#3 is already done).
- [ ] E2 variant B: comment `/autose single-pass` on issues #1–#5.
- [ ] E1: on each seeded PR (#6–#10) comment `/autose review`, then `/autose review coupled`.
- [ ] Record the demo run (step 6) during one of these.

## 5. Collect results and finish the report
```bash
export GH_TOKEN=... FORK=Ohshit-ak/tinydb
python3 tools/collect_results.py --hidden     # writes results/runs.md, results.csv, artifacts/
```
Then ask Claude to fill in every `PENDING` box in `report_src/report.tex` from `results/`, and to
replace `architecture/views/sequence.md` with the demo run. Superseded ADRs are kept, and new ADRs are
added only where a run showed an ADR was wrong. Rebuild `report.pdf`.

**Owner tasks:**
- rework the ADR wording into your own reasoning (course rule);
- fill in the AI-use TODO in README.md.

## 6. Demo video (≤ 5 min) — shot list
1. (0:00) Issue #k on GitHub. Explain in one sentence why this issue is a good example.
2. (0:20) Add the label `autose` → the ack comment appears with the run link.
3. (0:40) Actions run graph: gate → agents → release → ci → review → post-review. Say which jobs hold
   the model key and which hold the write token.
4. (1:30) Agents job log: the `==>` state transitions (spec check, design check, build, test, any back-edge).
5. (2:15) Artifacts: open spec.md (ACs), design.md (files to change), test_report.md (red on base).
6. (3:00) The PR: pr.md body, the "AutoSE CI (stage 5)" status, the diff.
7. (3:40) The posted review: requirements R1..Rn with evidence, the tool evidence log, the verdict, the
   labels. A rework dispatch if there was one.
8. (4:30) Close: "the bot never merges — the human decides", and point at the merge button.

## 7. Push the submission repo
```bash
# create an empty public repo Ohshit-ak/autose-a3 in the browser, then:
cd ~/Desktop/ASE/assignment-3/2024111004_AutoSE_A3
bash tools/sync_workflow.sh ../tinydb-autose   # keep workflow/ identical to the fork
git add -A && git commit -m "results and report"
git remote add origin https://github.com/Ohshit-ak/autose-a3.git && git push -u origin main
```
Submit `../2024111004_a3_AutoSE.txt` (it contains only the repo link). Keep both repos public until
grades are out.
