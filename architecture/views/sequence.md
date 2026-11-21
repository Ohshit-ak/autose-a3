# Sequence view: one real run (issue #3 → PR #11)

The timings come from [run 44902438357](https://github.com/Ohshit-ak/tinydb/actions/runs/44902438357):
Controller transitions are from `state.json` (seconds after the agents job started), and job
times are from the GitHub API (UTC, 2026-11-21).

The release job ran twice. The first attempt failed because `main` had moved during the run, and
GitHub rejects `GITHUB_TOKEN` pushes that change workflow files. Only that job was re-run after the
fix (ADR-012), and the times below are from that second attempt.

```mermaid
sequenceDiagram
    actor M as Maintainer
    participant G as gate job
    participant C as Controller (agents job)
    participant A as Analyst / Spec judge
    participant R as Architect
    participant B as Builder
    participant T as Tester
    participant Rel as release job
    participant CI as ci + ci-status
    participant Rv as Reviewer (review job)
    participant P as post-review job

    M->>G: workflow_dispatch(mode=full, issue=3) at 12:08:50
    G->>G: sender has write permission; ack comment on issue #3
    G->>C: agents job starts at 12:09:01
    C->>A: issue #3 (fenced as untrusted) + A1 skill
    A-->>C: spec.md, 4 ACs; lint + judge: all testable (t=20 s)
    C->>R: spec.md + ARCHITECTURE.md
    R-->>C: design.md: tinydb/table.py Table.count; AST and AC mapping ok (t=298 s)
    Note over R: worker falls back from 3.5-flash-lite to 3.5-flash (quota)
    C->>B: spec + design
    B-->>C: edits Table.count; check_build + run_tests; build check ok (t=1426 s)
    C->>T: ACs + public interface, base commit only
    T-->>C: tests/test_autose_issue_3.py; AC coverage 4/4, red on base for AC-1/2; full suite 231 passed (t=1897 s)
    C->>Rel: artifacts + git bundle (agents job ends at 12:40:53)
    Rel->>Rel: rebase onto current main (ADR-012); path allowlist ok
    Rel->>M: push autose/issue-3, open PR #11 (12:42:17–12:42:30)
    Rel->>CI: ci.yml on head 54c9ff2: success; commit status "AutoSE CI (stage 5)" (12:42:33–12:42:59)
    CI->>Rv: review job on a fresh runner (12:42:53–12:44:16)
    Rv->>Rv: derives R1–R3 from the issue, runs tests, approves (evidence guard ok)
    Rv-->>P: review.md + verdict.json
    P->>M: PR review posted as COMMENT; labels reviewer-approved, ready-for-human (12:44:33)
    Note over M: hidden tests 4/4 pass; a human decides whether to merge
```
