# Sequence view

**Status:** planned sequence (design-time). This file is replaced by the sequence of one *real* run
(issue → PR → review, with run/PR links and timings taken from `state.json`) once that run exists.

```mermaid
sequenceDiagram
    actor M as Maintainer
    participant GH as GitHub (issue/PR)
    participant G as gate job
    participant C as Controller (agents job)
    participant A as Analyst
    participant J as Spec judge
    participant R as Architect
    participant B as Builder
    participant T as Tester
    participant Rel as release job
    participant CI as ci job
    participant Rv as Reviewer (review job)
    participant P as post-review job

    M->>GH: add label "autose" to issue #n
    GH->>G: issues.labeled
    G->>GH: check sender permission (write+), ack comment
    G->>C: mode=full, issue=n, round=1
    C->>A: issue (fenced) + A1 skill
    A-->>C: spec.md
    C->>C: spec_lint
    C->>J: ACs
    J-->>C: {AC-k: testable}
    C->>R: spec.md + ARCHITECTURE.md
    R-->>C: design.md
    C->>C: design_check (paths, AST, AC mapping)
    loop up to 3 attempts (redesign after the 2nd)
        C->>B: spec + design (+ failing output)
        B-->>C: edits in tinydb/
        C->>C: build check (allowlist, compileall, import)
        C->>T: ACs + public interface, base commit only
        T-->>C: tests/test_autose_issue_n.py
        C->>C: AC coverage, new tests, full suite, red-on-base
    end
    C->>Rel: artifacts + git bundle
    Rel->>GH: push autose/issue-n, open PR, state comment
    Rel->>CI: ci.yml on head sha
    CI-->>Rv: success
    Rv->>GH: read issue + diff, checkout head (read-only token)
    Rv-->>P: review.md + verdict.json
    P->>GH: PR review (COMMENT) + labels
    alt request_changes and round < 3
        P->>GH: workflow_dispatch mode=rework target=stage
    else approve or rounds used up
        P->>GH: label autose:ready-for-human
        M->>GH: merge or close (human decision)
    end
```
