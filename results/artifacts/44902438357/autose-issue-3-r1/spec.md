# Spec — Let count() work without a query

## 1. Source
SRC-01: GitHub issue #3 (quote the key sentences verbatim, as quotes)
> ```
> `db.count(query)` is handy, but when I want the total number of documents I have to remember to use
> `len(db)` / `len(table)` instead, and `db.count()` just blows up:
> 
> TypeError: Table.count() missing 1 required positional argument: 'cond'
> 
> Could `count()` with no argument simply return the number of documents in the table? Counting with a
> query should keep working the same way it does today.
> ```

## 2. Problem and goal
- **Problem:** Calling `Table.count()` or `TinyDB.count()` (via `__getattr__` forwarding) without arguments raises a `TypeError` due to a missing required positional argument (`cond`). Users must remember to use `len(db)` or `len(table)` to get the total number of documents.
- **Goal:** Allow `count()` to be invoked with no arguments to return the total number of documents in the table/database, while preserving existing query-based counting behaviour.

## 3. Current behaviour (evidence)
- `Table.count()` defines `cond` as a mandatory parameter (`tinydb/table.py:709`):
  ```python
  def count(self, cond: QueryLike) -> int:
      return len(self.search(cond))
  ```
- `TinyDB` forwards unknown attribute accesses to the default table via `__getattr__` (`tinydb/database.py:251-255`), meaning `db.count()` invokes `Table.count()`.

## 4. Requirements
### FR-001 — Optional query parameter in count
- Statement: The library shall allow `count()` to be called without any arguments on both `Table` and `TinyDB` instances, returning the total number of documents in the table or default table respectively.
- Provenance: STATED (SRC-01)
- Status: READY

### FR-002 — Preserve query-based counting
- Statement: The library shall continue to support counting documents matching a given query when `count(cond)` is called with a condition argument.
- Provenance: STATED (SRC-01)
- Status: READY

## 5. Acceptance criteria
### AC-1: Table count without argument verifies FR-001
- Given a `db = TinyDB(storage=MemoryStorage)` and table `table = db.table('notes')` containing 3 documents inserted via `table.insert({'a': 1})`
- When `table.count()` is called with no arguments
- Then it returns `3` and does not raise a `TypeError`

### AC-2: TinyDB count without argument verifies FR-001
- Given a `db = TinyDB(storage=MemoryStorage)` containing 2 documents in the default table inserted via `db.insert({'b': 2})`
- When `db.count()` is called with no arguments
- Then it returns `2` and does not raise a `TypeError`

### AC-3: Table count with query preserves existing behaviour verifies FR-002
- Given a `db = TinyDB(storage=MemoryStorage)` and table `table = db.table('notes')` containing documents `{'type': 'a'}` (twice) and `{'type': 'b'}` (once), with `Query = Query()`
- When `table.count(Query.type == 'a')` is called
- Then it returns `2`

### AC-4: Unchanged len behaviour remains the same
- Given a `db = TinyDB(storage=MemoryStorage)` and table `table = db.table('notes')` containing 4 documents
- When `len(table)` and `len(db)` are called
- Then both return `4` exactly as before

## 6. Assumptions and open questions
- ASM-01: The return type for `count()` without arguments is an `int`, matching `__len__` and query-based `count()`.

## 7. Out of scope
- Changing the behaviour of `len()` on tables or `TinyDB` instances.
- Adding new query operators or filtering logic.

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
    "reason": "The Given, When, and Then provide explicit state setup, a clear API call with no arguments, and a precise expected return value without ambiguity."
  },
  "AC-2": {
    "testable": true,
    "reason": "The Given, When, and Then clearly specify the database initialization, the default table usage, calling `db.count()` with no arguments, and the exact return value."
  },
  "AC-3": {
    "testable": true,
    "reason": "The Given, When, and Then define exact document insertions, use of the TinyDB Query object, and a deterministic expected count result."
  },
  "AC-4": {
    "testable": true,
    "reason": "The Given, When, and Then clearly define the number of documents and check Python's built-in `len()` function on both the table and database, yielding a deterministic output."
  }
}
```
