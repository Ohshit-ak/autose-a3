# Design — Let count() work without a query

## Summary
Allow `Table.count()` to be called without arguments or with `None` as the query condition, in which case it returns the total number of documents in the table (delegating to `__len__()` / `len(self._read_table())`). When a valid query condition is provided, it behaves exactly as before. Since `TinyDB` forwards unknown attribute lookups to the default table via `__getattr__`, this automatically enables `db.count()` without arguments as well.

## Files to change
| Path | Change | Functions/classes |
|---|---|---|
| tinydb/table.py | modify | Table.count |
| tests/test_autose_issue_3.py | NEW | tests for AC-1..AC-4 (NEW) |

## Public interface
- `Table.count(cond: Optional[QueryLike] = None) -> int`:
  - When `cond` is `None` (omitted or explicitly passed as `None`), returns the total number of documents in the table (equivalent to `len(self)`).
  - When `cond` is a valid `QueryLike` instance, returns the number of documents matching the condition (equivalent to `len(self.search(cond))`).
- `TinyDB.count(cond: Optional[QueryLike] = None) -> int`:
  - Forwards to the default table's `count()` method via `__getattr__`, inheriting the exact same behavior.

## Change plan
1. Modify `Table.count` in `tinydb/table.py`:
   - Change signature from `def count(self, cond: QueryLike) -> int:` to `def count(self, cond: Optional[QueryLike] = None) -> int:`.
   - Update implementation to:
     ```python
     if cond is None:
         return len(self)
     return len(self.search(cond))
     ```
2. Create `tests/test_autose_issue_3.py`:
   - Add unit tests covering AC-1, AC-2, AC-3, and AC-4.

## AC mapping
- AC-1 → `tests/test_autose_issue_3.py`: tests `db.count()` without arguments on a `TinyDB` instance.
- AC-2 → `tests/test_autose_issue_3.py`: tests `db.count(query)` on a `TinyDB` instance.
- AC-3 → `tests/test_autose_issue_3.py`: tests `table.count()` without arguments on a custom `Table` instance.
- AC-4 → `tests/test_autose_issue_3.py`: tests `table.count(query)` on a custom `Table` instance.

## Architecture constraints check
- C1..C5 kept: No new storages, no direct storage writes bypassing `_update_table`, no cache changes, layering rules respected (`table.py` continues to use `QueryLike`), standard configuration used.

## Risks
- Low risk. Making `cond` optional with a default value of `None` is fully backwards compatible.


---
## Appendix — stage 2 check (Controller)
Result: PASS
- 2 file(s) named; all functions resolved; all ACs mapped
