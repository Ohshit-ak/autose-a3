# PR #11: https://github.com/Ohshit-ak/tinydb/pull/11

Resolves #3

> 🤖 AutoSE opened this PR automatically (round 1, variant `default`). A person decides whether to merge it.

## Acceptance criteria (from spec.md)

- **AC-1** — Table count without argument verifies FR-001
- **AC-2** — TinyDB count without argument verifies FR-001
- **AC-3** — Table count with query preserves existing behaviour verifies FR-002
- **AC-4** — Unchanged len behaviour remains the same

## Design summary

Make `cond` in `Table.count(cond=...)` optional by defaulting `cond` to `None` (or `Optional[QueryLike]`). When `cond` is `None` (or omitted), `Table.count()` delegates to `len(self)`, returning the total number of documents in the table. When `cond` is provided, `Table.count(cond)` preserves the existing search-based counting logic. `TinyDB` forwards `count()` to the default table via `__getattr__` without requiring any changes in `database.py`.

## Files changed

- `tests/test_autose_issue_3.py`
- `tinydb/table.py`

## Test report

| AC | Tests | Red on base? |
|---|---|---|
| AC-1 | test_ac1_table_count_without_argument | test_ac1_table_count_without_argument: FAILED |
| AC-2 | test_ac2_tinydb_count_without_argument | test_ac2_tinydb_count_without_argument: FAILED |
| AC-3 | test_ac3_table_count_with_query_preserves_existing_behaviour | test_ac3_table_count_with_query_preserves_existing_behaviour: PASSED |
| AC-4 | test_ac4_unchanged_len_behaviour_remains_the_same | test_ac4_unchanged_len_behaviour_remains_the_same: PASSED |

- New tests: `4 passed in 0.01s`
- Full suite: `231 passed, 1 skipped in 0.66s`
- *Red on base* = the new test FAILED against the unmodified code (the expected result for new behaviour; tests of unchanged behaviour pass on base by design).

## Trace

- Actions run (artifacts: spec.md, design.md, diff.patch, test_report.md, state.json): https://github.com/Ohshit-ak/tinydb/actions/runs/44902438357
- Base `8d284c4` → head `353a2e1`; worker model `gemini-3.5-flash-lite`; tokens this run: 178,201
- State transitions: SPEC → DESIGN → BUILD → TEST → DONE
