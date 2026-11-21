# Design — Let count() work without a query

## Summary
Make `cond` in `Table.count(cond=...)` optional by defaulting `cond` to `None` (or `Optional[QueryLike]`). When `cond` is `None` (or omitted), `Table.count()` delegates to `len(self)`, returning the total number of documents in the table. When `cond` is provided, `Table.count(cond)` preserves the existing search-based counting logic. `TinyDB` forwards `count()` to the default table via `__getattr__` without requiring any changes in `database.py`.

## Files to change
| Path | Change | Functions/classes |
|---|---|---|
| tinydb/table.py | modify | `Table.count` |
| tests/test_autose_issue_3.py | NEW | tests for AC-1..AC-4 (NEW) |

## Public interface
- `Table.count(self, cond: Optional[QueryLike] = None) -> int`
  - When `cond` is `None` (or omitted), returns `len(self)` (an `int` representing total document count).
  - When `cond` is passed, returns `len(self.search(cond))` (an `int` representing count of matching documents).
- `TinyDB.count(self, cond: Optional[QueryLike] = None) -> int` (via existing `__getattr__` forwarding to default table).

## Change plan
1. In `tinydb/table.py`, update `Table.count(self, cond: Optional[QueryLike] = None) -> int`:
   - Change signature parameter default: `cond: Optional[QueryLike] = None` (ensure `Optional` is imported or typed properly according to file imports).
   - In `count`, check `if cond is None: return len(self)`.
   - Otherwise, `return len(self.search(cond))`.
2. Create `tests/test_autose_issue_3.py`:
   - Add test functions verifying AC-1 (calling `table.count()` returns total documents), AC-2 (calling `db.count()` returns total default table documents), AC-3 (calling `table.count(query)` returns matching query count), AC-4 (`len(table)` and `len(db)` return expected counts).

## AC mapping
- AC-1 → `tinydb/table.py`: `Table.count` — optional `cond=None` causes `table.count()` to return `len(self)`, which returns total doc count without raising `TypeError`.
- AC-2 → `tinydb/table.py`: `Table.count` & `tinydb/database.py`: `TinyDB.__getattr__` — `db.count()` forwards to default table's `count()`, returning default table doc count without `TypeError`.
- AC-3 → `tinydb/table.py`: `Table.count` — when `cond` is provided, `count(cond)` delegates to `len(self.search(cond))`, matching existing behavior.
- AC-4 → `tinydb/table.py`: `Table.__len__` & `tinydb/database.py`: `TinyDB.__len__` — `len()` logic is unchanged and returns total counts as before.

## Architecture constraints check
- C1 (Storages subclass `Storage`): Kept — no changes to storages.
- C2 (Table mutations via `_update_table`): Kept — `count()` is a read-only operation and does not mutate table data.
- C3 (Query caching & hashval): Kept — query cache and `QueryInstance.hashval` are untouched; query searches proceed through `self.search(cond)` when `cond` is provided.
- C4 (Layering rules): Kept — `table.py` still relies only on `QueryLike` protocol/type hints.
- C5 (Storage/middleware args): Kept — constructor options unchanged.

## Risks
None identified.


---
## Appendix — stage 2 check (Controller)
Result: PASS
- 2 file(s) named; all functions resolved; all ACs mapped
