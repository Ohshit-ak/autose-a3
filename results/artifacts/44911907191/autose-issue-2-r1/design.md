# Design — Document IDs skip numbers after a failed insert_multiple

## Summary
When `insert_multiple` fails partway through iterating over documents (e.g., due to an invalid non-mapping item or a duplicate document ID), changes made to `self._next_id` during the partial iteration must not persist. We will make `insert_multiple` compute and manage the next ID state in a local variable or temporary attribute during the transaction, updating `self._next_id` only at the very end of `updater` once all validation and insertion steps have successfully completed.

## Files to change
| Path | Change | Functions/classes |
|---|---|---|
| tinydb/table.py | modify | Table.insert_multiple |
| tests/test_autose_issue_2.py | NEW | tests for AC-1, AC-2, AC-3 (NEW) |

## Public interface
- `Table.insert_multiple(self, documents: Iterable[Mapping]) -> list[int]`: Inserts multiple documents into the table. If any item is invalid or causes a conflict, raises `ValueError` and leaves `self._next_id` and table storage entirely unchanged.

## Change plan
1. **`tinydb/table.py` (`Table.insert_multiple`)**:
   - Instead of mutating `self._next_id` directly inside the loop (`self._next_id = ...`), track the next ID state in a local variable (e.g., `next_id = self._next_id`) throughout the iteration over `documents`.
   - When auto-assigning an ID, derive and advance the local `next_id` appropriately (mirroring `_get_next_id` logic on the in-memory `table` dict).
   - When encountering a `Document` with an explicit ID, set the local `next_id` to `None`.
   - Only assign the finalized local `next_id` back to `self._next_id` at the end of the `updater` function (right before it successfully completes). If an exception is raised, `self._update_table(updater)` aborts and `self._next_id` remains untouched.

## AC mapping
- AC-1 → `tests/test_autose_issue_2.py`: tests `insert_multiple` failure on non-mapping item leaves `self._next_id` unchanged for subsequent `insert()`.
- AC-2 → `tests/test_autose_issue_2.py`: tests `insert_multiple` failure on duplicate ID leaves `self._next_id` unchanged for subsequent `insert()`.
- AC-3 → `tests/test_autose_issue_2.py`: tests successful `insert_multiple` behaviour and subsequent `insert()` IDs.

## Architecture constraints check
- C1-C5 kept. All table mutations still go through `Table._update_table`.

## Risks
- None.


---
## Appendix — stage 2 check (Controller)
Result: PASS
- 2 file(s) named; all functions resolved; all ACs mapped
