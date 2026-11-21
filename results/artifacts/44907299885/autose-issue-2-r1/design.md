# Design — Document IDs skip numbers after a failed insert_multiple

## Summary
When `insert_multiple` fails midway through processing a batch (e.g. due to an invalid mapping or an existing explicit ID conflict), an exception is raised and `_update_table` aborts without writing changes. However, `self._next_id` on the `Table` instance has already been mutated during the partial iteration. To prevent ID gaps, `Table.insert_multiple` should either compute/allocate IDs without mutating `self._next_id` prematurely or restore `self._next_id` (and clear/reset any transient id state) if an exception occurs, or more simply, perform validation or ID calculation on a local copy or backup `self._next_id` state and only commit the new `self._next_id` upon successful completion of `insert_multiple`.

Wait, let's examine how `insert` and `insert_multiple` use `self._next_id`.
In `insert`, `_get_next_id()` is called, which mutates `self._next_id`. But `insert` is a single insertion, so either it succeeds completely or raises before any mutation of `self._next_id` (or if it raises, it's a single item).
In `insert_multiple`, multiple documents are processed. If any document is invalid, we want `self._next_id` not to have advanced.
If we backup `old_next_id = self._next_id` before running the updater, and in a `try...except` block restore `self._next_id = old_next_id` on exception, would that work?
Wait, if `insert_multiple` succeeds, we *do* want `self._next_id` to advance to the new value computed during insertion so subsequent inserts know where to start!
So if we save `old_next_id = self._next_id`, run the updater (which may update `self._next_id`), and if an exception occurs, we restore `self._next_id = old_next_id`. If it succeeds, we keep the new `self._next_id`.

## Files to change
| Path | Change | Functions/classes |
|---|---|---|
| tinydb/table.py | modify | Table.insert_multiple |
| tests/test_autose_issue_2.py | NEW | tests for AC-1, AC-2, AC-3 (NEW) |

## Public interface
- `Table.insert_multiple(documents: Iterable[Mapping]) -> list[int]`: If an exception (like `ValueError`) is raised midway, `self._next_id` remains unchanged (restored to its state before `insert_multiple` was called), and no changes are written to the database.

## Change plan
1. In `tinydb/table.py`:
   - In `Table.insert_multiple`, store `old_next_id = self._next_id` before calling `self._update_table(updater)`.
   - Wrap the call to `self._update_table(updater)` in a `try...except` block (or `try...finally` where we check if an exception was raised, or simply `try: ... except Exception: self._next_id = old_next_id; raise`).
   - This ensures that if any validation or iteration error occurs, `self._next_id` is restored.

## AC mapping
- AC-1 → `tests/test_autose_issue_2.py`: test that a failed `insert_multiple` due to invalid mapping preserves `_next_id` so subsequent `insert` gets ID `2`.
- AC-2 → `tests/test_autose_issue_2.py`: test that a failed `insert_multiple` due to duplicate ID preserves `_next_id` so subsequent `insert` gets ID `2`.
- AC-3 → `tests/test_autose_issue_2.py`: test that a successful `insert_multiple` assigns sequential IDs correctly and advances `_next_id`.

## Architecture constraints check
- C1-C5: Kept. No new storage classes, `_update_table` is still used for all table mutations, no layering violations.

## Risks
- None. Restoring `self._next_id` on exception in `insert_multiple` is clean, local, and completely prevents ID skipping on failure.


---
## Appendix — stage 2 check (Controller)
Result: PASS
- 2 file(s) named; all functions resolved; all ACs mapped
