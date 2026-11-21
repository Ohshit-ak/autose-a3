# PR #15: https://github.com/Ohshit-ak/tinydb/pull/15

Resolves #2

> 🤖 AutoSE opened this PR automatically (round 1, variant `single-pass`). A person decides whether to merge it.

## Acceptance criteria (from spec.md)

- **AC-1** — Next ID is preserved after `insert_multiple` failure due to invalid document type
- **AC-2** — Next ID is preserved after `insert_multiple` failure due to existing document ID collision
- **AC-3** — Successful `insert_multiple` behavior remains unaffected

## Design summary

When `insert_multiple` fails partway through processing its documents, `self._next_id` has already been mutated during the failed run, causing subsequent `insert()` calls to skip document IDs. We fix this by backing up `self._next_id` before the batch updater runs and restoring it if an exception occurs.

## Files changed

- `tests/test_autose_issue_2.py`
- `tinydb/table.py`

## Test report

| AC | Tests | Red on base? |
|---|---|---|
| AC-1 | test_ac1_next_id_preserved_after_insert_multiple_invalid_type | test_ac1_next_id_preserved_after_insert_multiple_invalid_type: FAILED |
| AC-2 | test_ac2_next_id_preserved_after_insert_multiple_collision | test_ac2_next_id_preserved_after_insert_multiple_collision: PASSED |
| AC-3 | test_ac3_successful_insert_multiple_behavior | test_ac3_successful_insert_multiple_behavior: PASSED |

- New tests: `3 passed in 0.01s`
- Full suite: `230 passed, 1 skipped in 0.71s`
- *Red on base* = the new test FAILED against the unmodified code (the expected result for new behaviour; tests of unchanged behaviour pass on base by design).

## Trace

- Actions run (artifacts: spec.md, design.md, diff.patch, test_report.md, state.json): https://github.com/Ohshit-ak/tinydb/actions/runs/44912802445
- Base `f3540f5` → head `fbe6843`; worker model `gemini-3.5-flash-lite`; tokens this run: 263,771
- State transitions: SPEC → DESIGN → BUILD → TEST → DONE
