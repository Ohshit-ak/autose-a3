# PR #16: https://github.com/Ohshit-ak/tinydb/pull/16

Resolves #3

> 🤖 AutoSE opened this PR automatically (round 1, variant `single-pass`). A person decides whether to merge it.

## Acceptance criteria (from spec.md)

- **AC-1** — Calling `db.count()` without arguments returns total document count (verifies FR-001)
- **AC-2** — Calling `db.count(query)` with a query condition works as before (verifies FR-002)
- **AC-3** — Calling `table.count()` without arguments returns total table document count (verifies FR-001)
- **AC-4** — Existing query-based counting behaviour for tables remains unchanged (verifies FR-002)

## Design summary

Allow `Table.count()` to be called without arguments or with `None` as the query condition, in which case it returns the total number of documents in the table (delegating to `__len__()` / `len(self._read_table())`). When a valid query condition is provided, it behaves exactly as before. Since `TinyDB` forwards unknown attribute lookups to the default table via `__getattr__`, this automatically enables `db.count()` without arguments as well.

## Files changed

- `docs/usage.rst`
- `tests/test_autose_issue_3.py`
- `tinydb/table.py`

## Test report

| AC | Tests | Red on base? |
|---|---|---|
| AC-1 | test_ac1_count_without_condition | test_ac1_count_without_condition: FAILED |
| AC-2 | test_ac2_count_with_query | test_ac2_count_with_query: PASSED |
| AC-3 | test_ac3_table_count_without_condition | test_ac3_table_count_without_condition: FAILED |
| AC-4 | test_ac4_table_count_with_query | test_ac4_table_count_with_query: PASSED |

- New tests: `4 passed in 0.01s`
- Full suite: `231 passed, 1 skipped in 0.54s`
- *Red on base* = the new test FAILED against the unmodified code (the expected result for new behaviour; tests of unchanged behaviour pass on base by design).

## Trace

- Actions run (artifacts: spec.md, design.md, diff.patch, test_report.md, state.json): https://github.com/Ohshit-ak/tinydb/actions/runs/44912891421
- Base `f3540f5` → head `c49e1a5`; worker model `gemini-3.5-flash-lite`; tokens this run: 290,540
- State transitions: SPEC → DESIGN → BUILD → TEST → DONE
