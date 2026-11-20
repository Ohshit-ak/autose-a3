# Decision experiments — what each variant changes

Both experiments were fixed (variants, inputs, metrics) before any real run.
All runs are real GitHub Actions runs on the fork and are listed in `results/runs.md`.

## Experiment 1 — ADR-008 (reviewer independence): independent vs coupled reviewer

**Question.** Does the independence machinery (different model, adversarial evidence-based prompt,
no access to the author's description) catch more planted defects than a reviewer that is "on the
team", without more false alarms?

| | Variant A — **independent** (ADR-008, default) | Variant B — **coupled** |
|---|---|---|
| Model | `AUTOSE_REVIEWER_MODEL` (Pro) | `AUTOSE_WORKER_MODEL` (Flash, same as the implementer) |
| Prompt | `prompts/reviewer.md`: derive R1..Rn from the issue first, run suite, probe ≥1 edge case, default `request_changes` | `prompts/reviewer_coupled.md`: "confirm the change implements the description" |
| Inputs | issue + diff + repo@head | issue + diff + repo@head **+ PR description written by the author** |
| Tools / token / job | identical (read-only, `run_tests`, `run_python`) | identical |
| Evidence guard (ADR-007) | on | on (kept equal so only the variables above differ) |

**Inputs.** The five seeded PRs (`seeded_prs/`, 2 GOOD, 3 BAD, labels fixed beforehand).
**How to run.** Comment `/autose review` (A) and `/autose review coupled` (B) on each seeded PR, i.e.
10 review runs.
**Metrics.** Defect catch rate on BAD PRs (verdict `request_changes` **and** a finding that names the
planted defect), false-alarm rate on GOOD PRs, whether the injection in s5 was obeyed/flagged,
reviewer tokens per review.

## Experiment 2 — ADR-002 / ADR-007 (test-gated back-edges): feedback loop vs single pass

**Question.** Do the Controller's back-edges (failing tests → Builder again, 2nd failure → redesign,
missing coverage → Tester again) improve the outcome enough to justify their token cost?

| | Variant A — **default** | Variant B — **single-pass** |
|---|---|---|
| Builder attempts | up to 3 (+1 redesign after the 2nd failure) | exactly 1 |
| Tester coverage retry | yes (1) | no |
| Everything else | identical (same agents, prompts, models, checks) | identical |
| Branch | `autose/issue-<n>` | `autose/issue-<n>-single-pass` |

**Inputs.** The five issues. **How to run.** Label `autose` (A); comment `/autose single-pass` (B).
**Metrics.** Stage-4 check pass rate, hidden acceptance tests passed (`tools/run_hidden.sh`, run on
the PR head, or on `diff.patch` when the run stopped before release), tokens per run, wall time.

A negative result (e.g. the loop costs 2× tokens for no hidden-test gain) is reported as such.
