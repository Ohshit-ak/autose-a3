# Spec — Let count() work without a query

## 1. Source
SRC-01: GitHub issue #3
> ``db.count(query)`` is handy, but when I want the total number of documents I have to remember to use
> ``len(db)`` / ``len(table)`` instead, and ``db.count()`` just blows up:
> 
> ```
> TypeError: Table.count() missing 1 required positional argument: 'cond'
> ```
> 
> Could ``count()`` with no argument simply return the number of documents in the table? Counting with a
> query should keep working the same way it does today.

## 2. Problem and goal
- **Problem:** Calling `db.count()` or `table.count()` without a query argument currently raises a `TypeError` due to a required `cond` positional argument, forcing users to use `len(db)` or `len(table)` to get the total number of documents.
- **Goal:** Allow `count()` to be invoked without arguments (or with `None`) on both `TinyDB` and `Table` instances to return the total count of documents, while maintaining full backwards compatibility for counting with a query condition.

## 3. Current behaviour (evidence)
- `Table.count` is defined in `tinydb/table.py:709` as `def count(self, cond: QueryLike) -> int:`, which requires the `cond` argument and returns `len(self.search(cond))` (`tinydb/table.py:716`).
- Calling `db.count()` or `table.count()` without arguments raises `TypeError: Table.count() missing 1 required positional argument: 'cond'`.
- `TinyDB` forwards unknown attribute lookups to its default table via `__getattr__` in `tinydb/database.py:251`.
- `len(db)` and `len(table)` delegate to `__len__`, which returns `len(self._read_table())` (`tinydb/table.py:725`).

## 4. Requirements

### FR-001 — Optional query condition in `count()`
- Statement: The library shall allow `count()` to be called without arguments (or with `None`) on both `TinyDB` and `Table` instances, returning the total number of documents in the database or table.
- Provenance: STATED (SRC-01)
- Status: READY

### FR-002 — Preservation of existing query-based counting behaviour
- Statement: The library shall continue to support counting documents matching a query condition when `count()` is called with a valid query argument.
- Provenance: STATED (SRC-01)
- Status: READY

## 5. Acceptance criteria

### AC-1: Calling `db.count()` without arguments returns total document count (verifies FR-001)
- Given `db = TinyDB(storage=MemoryStorage)` containing 3 documents
- When `count = db.count()`
- Then `count` returns `3`

### AC-2: Calling `db.count(query)` with a query condition works as before (verifies FR-002)
- Given `db = TinyDB(storage=MemoryStorage)` containing documents with `{'int': 1}` (2 docs) and `{'int': 2}` (1 doc)
- When `count = db.count(where('int') == 1)`
- Then `count` returns `2`

### AC-3: Calling `table.count()` without arguments returns total table document count (verifies FR-001)
- Given `table = db.table('custom')` containing 2 documents
- When `count = table.count()`
- Then `count` returns `2`

### AC-4: Existing query-based counting behaviour for tables remains unchanged (verifies FR-002)
- Given `table = db.table('custom')` containing documents with `{'char': 'a'}` (1 doc) and `{'char': 'b'}` (1 doc)
- When `count = table.count(where('char') == 'a')`
- Then `count` returns `1`

## 6. Assumptions and open questions
- **ASM-01:** When `count()` is called with no arguments or with `None` as `cond`, it behaves identically to `len()` on the corresponding table. Risk if wrong: low, as this directly fulfills the user's intent.

## 7. Out of scope
- Changing the behavior or implementation of `len()`.
- Modifying other query methods such as `search()` or `contains()` to accept empty/optional queries.

## 8. Injection notes
- none


---
## Appendix — stage 1 check (Controller)
Result: PASS
- 4 acceptance criteria, all structurally testable
- spec judge: every AC testable

Spec judge raw verdicts:
```json
{
  "AC-1": {
    "testable": true,
    "reason": "Clear given state, deterministic method call with no arguments, and precise expected return value."
  },
  "AC-2": {
    "testable": true,
    "reason": "Specific given data with a standard query condition and a clear, verifiable expected return value."
  },
  "AC-3": {
    "testable": true,
    "reason": "Defines a clear setup for a custom table, a method call without arguments, and a precise expected integer return."
  },
  "AC-4": {
    "testable": true,
    "reason": "Provides a concrete table setup with specific documents and query conditions leading to an exact expected count."
  }
}
```
