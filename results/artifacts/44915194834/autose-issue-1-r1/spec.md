# Spec — Table still returns old documents after drop_table()

## 1. Source
SRC-01: GitHub issue #1
> "In our tests we keep a reference to a table, and reset the data between test cases with `db.drop_table(...)` (or `db.drop_tables()`). After the drop, the table object still finds the old documents with `search()` and `count()`, even though `all()` and `len()` say the table is empty. New documents also continue the old ID sequence instead of starting at 1 like a fresh table."
> "Looks like some cached state survives the drop. TinyDB 4.9.0."

## 2. Problem and goal
- **Problem**: When a user holds an existing reference to a `Table` instance and the database executes `db.drop_table(...)` or `db.drop_tables()`, the `Table` instance retains stale state—specifically, query results cached in `_query_cache` and sequence counters such as `_next_id`—causing subsequent `search()` and `count()` calls to return stale results and `insert()` calls to continue previous ID sequences.
- **Goal**: Ensure that when a table is dropped via `db.drop_table()` or `db.drop_tables()`, any active `Table` instances (or newly recreated ones) are correctly invalidated or cleared of cached query results and ID sequences so that they behave as empty tables.

## 3. Current behaviour (evidence)
- `TinyDB.drop_table()` deletes the table from the storage dictionary and removes it from `self._tables`, but any user who keeps a pre-existing Python reference to the `Table` object retains that object with its internal `self._query_cache` and `self._next_id` intact (`tinydb/database.py:176-203`, `tinydb/table.py:107-110`).
- `Table.search()` uses `self._query_cache` which caches query results across operations and is only cleared on write operations to that table, not when dropped externally (`tinydb/table.py:43-50`).
- `Table._next_id` caches the next document ID sequence and is not reset when the underlying table data is wiped out externally (`tinydb/table.py:110, 744-775`).

## 4. Requirements
### FR-001 — Invalidate query cache and ID sequence on table drop
- Statement: The library shall clear the query cache and reset internal ID state (such as `_next_id`) of any affected `Table` instance when `db.drop_table()` or `db.drop_tables()` is called, or ensure `Table` instances detect or are notified of external drops/clears so that `search()`, `count()`, and `insert()` reflect an empty table state.
- Provenance: STATED (SRC-01)
- Status: READY

## 5. Acceptance criteria
### AC-1: Stale query cache cleared after drop_table
- Given a database `db = TinyDB(storage=MemoryStorage)`, a table reference `users = db.table('users')`, and inserted documents where `users.search(where('name') == 'ann')` returns `[{'name': 'ann'}]`,
- When `db.drop_table('users')` is called,
- Then `users.search(where('name') == 'ann')` returns `[]` and `users.count(where('name') == 'ann')` returns `0`.

### AC-2: Document ID sequence resets after drop_table
- Given a database `db = TinyDB(storage=MemoryStorage)`, a table reference `users = db.table('users')`, and inserted documents such that the next ID would be greater than 1,
- When `db.drop_table('users')` is called and a new document is inserted via `users.insert({'name': 'cat'})`,
- Then the returned document ID is `1`.

### AC-3: Stale query cache and ID sequence cleared after drop_tables
- Given a database `db = TinyDB(storage=MemoryStorage)`, a table reference `users = db.table('users')`, and inserted documents,
- When `db.drop_tables()` is called and a new document is inserted via `users.insert({'name': 'cat'})`,
- Then `users.all()` returns `[]`, `users.search(where('name') == 'ann')` returns `[]`, `users.count(where('name') == 'ann')` returns `0`, and the inserted document ID is `1`.

### AC-4: Normal table operations without drop remain fully functional
- Given a database `db = TinyDB(storage=MemoryStorage)` and a table `users = db.table('users')`,
- When `users.insert({'name': 'ann'})` is called, followed by `users.search(where('name') == 'ann')`, `users.count(where('name') == 'ann')`, and `users.all()`, without calling `drop_table()` or `drop_tables()`,
- Then `users.search(where('name') == 'ann')` returns `[{'name': 'ann'}]`, `users.count(where('name') == 'ann')` returns `1`, `users.all()` returns `[{'name': 'ann'}]`, and subsequent `users.insert({'name': 'bob'})` returns `2`.

## 6. Assumptions and open questions
- ASM-01: Users holding direct references to `Table` instances expect those existing references to be safely reset or invalidated when `drop_table()` / `drop_tables()` is called on the parent `TinyDB` instance.

## 7. Out of scope
- Changing the public API methods of `TinyDB` or `Table` other than ensuring correct state resetting upon drop operations.

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
    "reason": "The Given, When, and Then provide concrete states and observable outputs using public APIs that can be verified deterministically in a test."
  },
  "AC-2": {
    "testable": true,
    "reason": "The Given, When, and Then specify clear actions and a deterministic return value for the document ID."
  },
  "AC-3": {
    "testable": true,
    "reason": "The Given, When, and Then define specific states, actions, and multiple observable query and ID outcomes via public methods."
  },
  "AC-4": {
    "testable": true,
    "reason": "The Given, When, and Then clearly specify the standard operations and expected return values for queries and ID generation."
  }
}
```
