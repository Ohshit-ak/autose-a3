# Design — Table still returns old documents after drop_table()
## Summary
When `TinyDB.drop_table()` or `TinyDB.drop_tables()` is called, existing Python references to `Table` instances retain stale state (`_query_cache` and `_next_id`). We add a mechanism to invalidate or clear the query cache and reset `_next_id` on these table instances (or provide a reset method/mechanism called during drop). Specifically, we can add a `clear()` or `reset()` method on `Table` (or `_reset()` (NEW)), and have `TinyDB.drop_table()` and `TinyDB.drop_tables()` call it on any table instances they hold or previously held/dropped, or clear the cache and `_next_id` on cached/dropped table objects.

## Files to change
| Path | Change | Functions/classes |
|---|---|---|
| tinydb/table.py | modify | Table.clear_cache, Table.truncate, Table._reset (NEW) |
| tinydb/database.py | modify | TinyDB.drop_table, TinyDB.drop_tables |
| tests/test_autose_issue_1.py | NEW | tests for AC-1..AC-4 (NEW) |

## Public interface
- `Table._reset() (NEW)`: Clears the query cache (`self.clear_cache()`) and resets `self._next_id = None`.

## Change plan
1. `tinydb/table.py`: Add `_reset(self) -> None (NEW)` method to `Table` that calls `self.clear_cache()` and sets `self._next_id = None`.
2. `tinydb/database.py`: In `TinyDB.drop_tables()`, call `table._reset()` on any table instances in `self._tables.values()` before clearing `self._tables`, or keep track of them. Wait, `drop_tables()` clears `self._tables`. If someone holds a reference to a table instance that was in `self._tables`, `drop_tables()` should ideally reset it. We can iterate over `list(self._tables.values())` and call `table._reset()`, then `self._tables.clear()`.
3. `tinydb/database.py`: In `TinyDB.drop_table(name)`, if `name in self._tables`, call `self._tables[name]._reset()` before deleting it from `self._tables` (or after, by keeping a reference to it).
4. `tests/test_autose_issue_1.py`: Add test file covering AC-1, AC-2, AC-3, and AC-4.

## AC mapping
- AC-1 → tinydb/database.py, tinydb/table.py: `drop_table` calls `Table._reset()` clearing query cache, so `search()` and `count()` return empty results.
- AC-2 → tinydb/database.py, tinydb/table.py: `drop_table` resets `_next_id`, so next insert gets ID `1`.
- AC-3 → tinydb/database.py, tinydb/table.py: `drop_tables` calls `Table._reset()` on all open tables, resetting query cache, results, and ID sequence.
- AC-4 → tinydb/database.py, tinydb/table.py: Normal operations without drop remain unaffected.

## Architecture constraints check
- C1-C5: Kept. No new storage requirements, all table mutations / resets use standard internal methods.
- ADR-1..3: Kept.

## Risks
- Users holding references to tables dropped via `drop_tables()` or `drop_table()` might still have table objects pointing to the same storage; resetting `_next_id` and clearing `_query_cache` via `_reset()` ensures they correctly reflect the empty state.


---
## Appendix — stage 2 check (Controller)
Result: PASS
- 3 file(s) named; all functions resolved; all ACs mapped
