# PR #12: https://github.com/Ohshit-ak/tinydb/pull/12

Resolves #4

> 🤖 AutoSE opened this PR automatically (round 1, variant `default`). A person decides whether to merge it.

## Acceptance criteria (from spec.md)

- **AC-1** — Append to existing list field (verifies FR-001)
- **AC-2** — Append to missing field creates new list (verifies FR-001)
- **AC-3** — Existing operations remain unaffected (verifies FR-002)

## Design summary

Add an `append(field, val)` operation to `tinydb.operations`. It returns a transformation function that appends `val` to an existing list stored at `field` in a document, or initializes `field` with a new single-element list `[val]` if `field` is not present in the document.

## Files changed

- `tests/test_autose_issue_4.py`
- `tinydb/operations.py`

## Test report

| AC | Tests | Red on base? |
|---|---|---|
| AC-1 | test_ac1_append_to_existing_list_field | test_ac1_append_to_existing_list_field: ? |
| AC-2 | test_ac2_append_to_missing_field_creates_new_list | test_ac2_append_to_missing_field_creates_new_list: ? |
| AC-3 | test_ac3_existing_operations_remain_unaffected | test_ac3_existing_operations_remain_unaffected: ? |

- New tests: `3 passed in 0.01s`
- Full suite: `230 passed, 1 skipped in 0.59s`
- *Red on base* = the new test FAILED against the unmodified code (the expected result for new behaviour; tests of unchanged behaviour pass on base by design).

## Trace

- Actions run (artifacts: spec.md, design.md, diff.patch, test_report.md, state.json): https://github.com/Ohshit-ak/tinydb/actions/runs/44904983818
- Base `f0a6f1f` → head `dd99e05`; worker model `gemini-3.5-flash-lite`; tokens this run: 184,201
- State transitions: SPEC → DESIGN → BUILD → TEST → DONE
