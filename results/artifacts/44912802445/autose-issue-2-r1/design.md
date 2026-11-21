# Design — Document IDs skip numbers after a failed insert_multiple
## Summary
When `insert_multiple` fails partway through processing its documents, `self._next_id` has already been mutated during the failed run, causing subsequent `insert()` calls to skip document IDs. We fix this by backing up `self._next_id` before the batch updater runs and restoring it if an exception occurs.

## Files to change
| Path | Change | Functions/classes |
|---|---|---|
| tinydb/table.py | modify | Table.insert_multiple |
| tests/test_autose_issue_2.py | NEW | tests for AC-1, AC-2, AC-3 (NEW) |

## Public interface
No changes to public signatures or methods. `insert_multiple` now preserves `self._next_id` if validation or collision fails.

## Change plan
1. In `tinydb/table.py:Table.insert_multiple`:
   - Save the current value of `self._next_id` into a local variable (e.g., `previous_next_id = self._next_id`) before calling `self._update_table(updater)`.
   - Wrap `self._update_table(updater)` in a `try...except` block (or `try...finally`), restoring `self._next_id = previous_next_id` if any exception is raised.

## AC mapping
- AC-1 → `tests/test_autose_issue_2.py`: tests `insert_multiple` failure with invalid document type and subsequent `insert` ID.
- AC-2 → `tests/test_autose_issue_2.py`: tests `insert_multiple` failure with ID collision and subsequent `insert` ID.
- AC-3 → `tests/test_autose_issue_2.py`: tests successful `insert_multiple` and subsequent `insert` ID.

## Architecture constraints check
- C1–C5 kept. `Table._update_table` is still used for table mutations; no direct storage writes.

## Risks
- None. Restoring `self._next_id` on failure is purely local to the table's in-memory ID state and rollback aligns with the atomic failure guarantee of `insert_multiple`.


---
## Appendix — stage 2 check (Controller)
Result: PASS
- 2 file(s) named; all functions resolved; all ACs mapped
