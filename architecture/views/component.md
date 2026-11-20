# Component view — AutoSE issue-to-PR workflow

Status: design-time view, committed before any agent code (see git history).

## Components

| Component | Kind | Runs in (Actions job) | Model | Tools it gets | GitHub token rights |
|---|---|---|---|---|---|
| **Gate** | deterministic Python | `gate` | none | GitHub REST (read issue, read sender permission) | `issues: read`, `pull-requests: read` |
| **Controller** | deterministic Python state machine | `agents` | none | starts the agents, runs every stage check, runs git locally, decides on back-edges | none (checkout with `persist-credentials: false`) |
| **Analyst** (stage 1) | LLM agent | `agents` | worker model | `read_file`, `list_files`, `search_code` (read-only, path-jailed), `submit` | none |
| **Spec judge** (stage 1 check) | LLM judge, single call | `agents` | worker model, temperature 0 | none | none |
| **Architect** (stage 2) | LLM agent | `agents` | worker model | read-only tools, `submit` | none |
| **Builder** (stage 3) | LLM agent | `agents` | worker model | read-only tools, `write_file`, `replace_in_file` (allowlist `tinydb/**`, `docs/**`), `check_build`, `run_tests` (fixed pytest command, sandbox user, no secrets) | none |
| **Tester** (stage 4) | LLM agent | `agents` | worker model | read-only tools **on the base commit**, `write_file` (only `tests/test_autose_issue_<n>.py`), `run_tests` | none |
| **Release** (stage 5) | deterministic Python | `release` | none | `git push`, GitHub REST (PRs, comments, labels) | `contents: write`, `pull-requests: write`, `issues: write` |
| **CI** (stage 5 check) | reusable workflow `ci.yml` | `ci` | none | pytest + compileall | `contents: read` |
| **Reviewer** (stage 6) | LLM agent, fresh runner | `review` | reviewer model (different from worker) | read-only tools on PR head, `run_tests`, `run_python` (sandbox), `submit_review` | `contents: read`, `issues: read`, `pull-requests: read` (cannot push or post) |
| **Review poster** | deterministic Python | `post-review` | none | GitHub REST (post PR review as COMMENT, labels, `workflow_dispatch` for the next round) | `pull-requests: write`, `issues: write`, `actions: write` |

The model key (`GEMINI_API_KEY`) exists only in the `agents` and `review` jobs. Neither of them has
a token that can write to GitHub. The jobs that can write to GitHub never see the model key and never
run model output as code.

## Who calls whom

```mermaid
flowchart TB
    subgraph GH[GitHub]
      Issue[(Issue + label 'autose'\nor '/autose' comment)]
      PR[(Pull request\nautose/issue-N)]
      Arts[(Workflow artifacts\nspec.md design.md diff.patch\ntest_report.md pr.md review.md\nstate.json usage.jsonl)]
      StateC[(State comment on issue\n<!-- autose-state {json} -->)]
    end

    Issue -- "issues.labeled / issue_comment" --> Gate
    Gate -- "mode, issue, pr, round" --> Controller

    subgraph AgentsJob["job: agents  (contents:read, GEMINI key, no push)"]
      Controller{{Controller\nstate machine}}
      Analyst[[Analyst\nA1 skill, unattended]]
      Judge[[Spec judge]]
      Architect[[Architect\nARCHITECTURE.md]]
      Builder[[Builder]]
      Tester[[Tester\nreads base commit]]
      Checks[/Deterministic checks\nlint, AST, compileall, pytest/]
      Controller --> Analyst --> Controller
      Controller --> Judge --> Controller
      Controller --> Architect --> Controller
      Controller --> Builder --> Controller
      Controller --> Tester --> Controller
      Controller --> Checks --> Controller
    end

    Controller -- "upload: artifacts + git bundle" --> Arts
    Arts -- "download bundle" --> Release

    subgraph ReleaseJob["job: release  (contents/PR/issues write, no model key)"]
      Release[Release\npath allowlist check, push, open PR]
    end
    Release -- push + open/update --> PR
    Release -- "upsert" --> StateC
    PR --> CI[job: ci\nreusable ci.yml on head sha]

    subgraph ReviewJob["job: review  (read-only token, GEMINI key, fresh runner)"]
      Reviewer[[Reviewer\nissue + diff + repo@head only]]
    end
    CI --> Reviewer
    Issue -. "issue text (API)" .-> Reviewer
    PR -. "diff base...head, checkout head" .-> Reviewer
    Reviewer -- "review.md + verdict.json" --> Poster

    subgraph PostJob["job: post-review  (PR/issues/actions write, no model key)"]
      Poster[Review poster]
    end
    Poster -- "PR review (COMMENT) + labels" --> PR
    Poster -- "request_changes and round < 2:\nworkflow_dispatch mode=rework,target=design/implementation/tests" --> Gate
    Poster -- "approve or rounds used up:\nlabel autose:ready-for-human" --> Human((Maintainer\nmerges or closes))
```

## What each agent can see (summary; details in ADR-003)

| Agent | Sees | Deliberately does not see |
|---|---|---|
| Analyst | issue title/body (fenced as untrusted data), condensed A1 skill, repo (read-only) | ARCHITECTURE.md, any code-change instructions |
| Architect | spec.md, ARCHITECTURE.md, repo (read-only) | raw issue body (the spec is the contract and it reduces injection surface) |
| Builder | spec.md, design.md, repo (read/write within allowlist), on retries: failing test output / review findings | the hidden tests, other issues' runs |
| Tester | spec.md (acceptance criteria), design.md "public interface" section, repo **at the base commit** | the Builder's diff and reasoning (tests come from the spec, not from the code) |
| Reviewer | issue text, `git diff base...head`, repo at PR head, can run code | spec.md, design.md, test_report.md, pr.md, PR body, any agent transcript |
