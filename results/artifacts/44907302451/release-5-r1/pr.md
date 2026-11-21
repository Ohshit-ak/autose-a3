# PR #14: https://github.com/Ohshit-ak/tinydb/pull/14

Resolves #5

> 🤖 AutoSE opened this PR automatically (round 1, variant `default`). A person decides whether to merge it.

## Acceptance criteria (from spec.md)

- **AC-1** — Greater-than query with incompatible types returns False instead of crashing (verifies FR-001)
- **AC-2** — Less-than-or-equal query with incompatible types returns False instead of crashing (verifies FR-001)
- **AC-3** — Valid comparison queries return matching documents (verifies FR-001 and existing behaviour)

## Design summary

When querying older documents where a field has an unexpected type (e.g. string instead of integer), comparison queries (`<`, `<=`, `>`, `>=`, `==`, `!=`) currently raise an unhandled `TypeError` during comparison, crashing the search. We will wrap the comparison test execution in `_generate_test` runner (or within the operator test functions) so that `TypeError` is caught and evaluated as returning `False` (for `<`, `<=`, `>`, `>=`, `==`) or `True` (for `!=` as per standard inequality semantics, or handled gracefully). Specifically, FR-001 requires `<, <=, >, >=` to return `False`, and FR-002 specifies equality/inequality handling as well. Since `_generate_test` catches `(KeyError, TypeError)` during path traversal, catching `TypeError` during the `test(value)` execution (or inside the comparison operators) prevents crashes.

## Files changed

- `tests/test_autose_issue_5.py`
- `tinydb/queries.py`

## Test report

| AC | Tests | Red on base? |
|---|---|---|
| AC-1 | test_ac1_greater_than_incompatible_types | test_ac1_greater_than_incompatible_types: FAILED |
| AC-2 | test_ac2_less_than_or_equal_incompatible_types | test_ac2_less_than_or_equal_incompatible_types: FAILED |
| AC-3 | test_ac3_valid_comparison_queries | test_ac3_valid_comparison_queries: PASSED |

- New tests: `3 passed in 0.01s`
- Full suite: `230 passed, 1 skipped in 0.55s`
- *Red on base* = the new test FAILED against the unmodified code (the expected result for new behaviour; tests of unchanged behaviour pass on base by design).

## Trace

- Actions run (artifacts: spec.md, design.md, diff.patch, test_report.md, state.json): https://github.com/Ohshit-ak/tinydb/actions/runs/44907302451
- Base `c8c93a7` → head `b91f254`; worker model `gemini-3.5-flash-lite`; tokens this run: 303,779
- State transitions: SPEC → SPEC → DESIGN → BUILD → TEST → DONE
