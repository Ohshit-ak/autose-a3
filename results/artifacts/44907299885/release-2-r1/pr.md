# PR #13: https://github.com/Ohshit-ak/tinydb/pull/13

Resolves #2

> 🤖 AutoSE opened this PR automatically (round 1, variant `default`). A person decides whether to merge it.

## Acceptance criteria (from spec.md)

- **AC-1** — Subsequent insert ID follows immediately after successful insert after failed `insert_multiple` due to invalid mapping type
- **AC-2** — Subsequent insert ID follows immediately after successful insert after failed `insert_multiple` due to duplicate document ID
- **AC-3** — Successful `insert_multiple` assigns sequential IDs

## Design summary

When `insert_multiple` fails midway through processing a batch (e.g. due to an invalid mapping or an existing explicit ID conflict), an exception is raised and `_update_table` aborts without writing changes. However, `self._next_id` on the `Table` instance has already been mutated during the partial iteration. To prevent ID gaps, `Table.insert_multiple` should either compute/allocate IDs without mutating `self._next_id` prematurely or restore `self._next_id` (and clear/reset any transient id state) if an exception occurs, or more simply, perform validation or ID calculation on a local copy or backup `self._next_id` state and only commit the new `self._next_id` upon successful completion of `insert_multiple`.

Wait, let's examine how `insert` and `insert_multiple` use `self._next_id`.
In `insert`, `_get_next_id()` is called, which mutates `self._next_id`. But `insert` is a single insertion, so either it succeeds completely or raises before any mutation of `self._next_id` (or if it raises, it's a single item).
In `insert_multiple`, multiple documents are processed. If any document is invalid, we want `self._next_id` not to have advanced.
If we backup `old_next_id = self._next_id` before running the updater, and in a `try...except` block restore `self._next_id = old_next_id` on exception, would that work?
Wait, if `insert_multiple` succeeds, we *do* want `self._next_id` to advance to the new value computed during insertion so subsequent inserts know where to start!
So if we save

## Files changed

- `tests/test_autose_issue_2.py`
- `tinydb/table.py`

## Test report

| AC | Tests | Red on base? |
|---|---|---|
| AC-1 | test_ac1_insert_multiple_invalid_mapping_type | test_ac1_insert_multiple_invalid_mapping_type: FAILED |
| AC-2 | test_ac2_insert_multiple_duplicate_document_id | test_ac2_insert_multiple_duplicate_document_id: PASSED |
| AC-3 | test_ac3_successful_insert_multiple_sequential_ids | test_ac3_successful_insert_multiple_sequential_ids: PASSED |

- New tests: `3 passed in 0.01s`
- Full suite: `230 passed, 1 skipped in 0.55s`
- *Red on base* = the new test FAILED against the unmodified code (the expected result for new behaviour; tests of unchanged behaviour pass on base by design).

## Trace

- Actions run (artifacts: spec.md, design.md, diff.patch, test_report.md, state.json): https://github.com/Ohshit-ak/tinydb/actions/runs/44907299885
- Base `c8c93a7` → head `7b1dfeb`; worker model `gemini-3.5-flash-lite`; tokens this run: 217,406
- State transitions: SPEC → SPEC → DESIGN → BUILD → TEST → DONE
