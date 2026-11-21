# PR #17: https://github.com/Ohshit-ak/tinydb/pull/17

Resolves #1

> 🤖 AutoSE opened this PR automatically (round 1, variant `default`). A person decides whether to merge it.

## Acceptance criteria (from spec.md)

- **AC-1** — Stale query cache cleared after drop_table
- **AC-2** — Document ID sequence resets after drop_table
- **AC-3** — Stale query cache and ID sequence cleared after drop_tables
- **AC-4** — Normal table operations without drop remain fully functional

## Design summary

When `TinyDB.drop_table()` or `TinyDB.drop_tables()` is called, existing Python references to `Table` instances retain stale state (`_query_cache` and `_next_id`). We add a mechanism to invalidate or clear the query cache and reset `_next_id` on these table instances (or provide a reset method/mechanism called during drop). Specifically, we can add a `clear()` or `reset()` method on `Table` (or `_reset()` (NEW)), and have `TinyDB.drop_table()` and `TinyDB.drop_tables()` call it on any table instances they hold or previously held/dropped, or clear the cache and `_next_id` on cached/dropped table objects.

## Files changed

- `tests/test_autose_issue_1.py`
- `tinydb/database.py`
- `tinydb/table.py`

## Test report

| AC | Tests | Red on base? |
|---|---|---|
| AC-1 | test_ac1_stale_query_cache_cleared_after_drop_table | test_ac1_stale_query_cache_cleared_after_drop_table: FAILED |
| AC-2 | test_ac2_document_id_sequence_resets_after_drop_table | test_ac2_document_id_sequence_resets_after_drop_table: FAILED |
| AC-3 | test_ac3_stale_query_cache_and_id_sequence_cleared_after_drop_tables | test_ac3_stale_query_cache_and_id_sequence_cleared_after_drop_tables: FAILED |
| AC-4 | test_ac4_normal_table_operations_without_drop_remain_fully_functional | test_ac4_normal_table_operations_without_drop_remain_fully_functional: PASSED |

- New tests: `4 passed in 0.01s`
- Full suite: `231 passed, 1 skipped in 0.57s`
- *Red on base* = the new test FAILED against the unmodified code (the expected result for new behaviour; tests of unchanged behaviour pass on base by design).

## Trace

- Actions run (artifacts: spec.md, design.md, diff.patch, test_report.md, state.json): https://github.com/Ohshit-ak/tinydb/actions/runs/44915194834
- Base `f3540f5` → head `e3c7f9b`; worker model `gemini-3.5-flash-lite`; tokens this run: 308,226
- State transitions: SPEC → SPEC → DESIGN → BUILD → TEST → DONE
