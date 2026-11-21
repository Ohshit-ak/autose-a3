# Spec — Table still returns old documents after drop_table()
## 1. Source
SRC-01: GitHub issue #1 (quote the key sentences verbatim, as quotes)
> "In our tests we keep a reference to a table, and reset the data between test cases with `db.drop_table(...)` (or `db.drop_tables()`). After the drop, the table object still finds the old documents with `search()` and `count()`, even though `all()` and `len()` say the table is empty. New documents also continue the old ID sequence instead of starting at 1 like a fresh table."
> "Looks like some cached state survives the drop. TinyDB 4.9.0."

## 2. Problem and goal
- Problem: When a user retains a Python reference to a `Table` instance, invoking `db.drop_table(name)` or `db.drop_tables()` removes the table data from storage and clears the database instance's table cache (`db._tables`), but does not invalidate or reset the internal cached state of existing `Table` instances (such as query caches and ID generation/tracking state like `_next_id`). Consequently, operations like `search()`, `count()`, and new insertions on the retained `Table` instance exhibit stale behavior (returning old query results and continuing previous ID sequences).
- Goal: Ensure that when a table is dropped via `db.drop_table()` or `db.drop_tables()`, any existing or subsequently accessed instances of that table are correctly reset or invalidated so that queries, counts, and ID generation behave as a brand new, empty table.

## 3. Current behaviour (evidence)
- `TinyDB.drop_table(name)` deletes the table from the storage read data dict and removes `name` from `self._tables`, but leaves any pre-existing `Table` Python object instances unaffected. (`tinydb/database.py:176-205`)
- `Table` instances maintain a query cache (`self._query_cache`) and ID tracking (`self._next_id`), which are not cleared or reset when the underlying storage data for the table is deleted or emptied. (`tinydb/table.py:105-110`)
- `Table.all()` and `Table.__len__()` read directly from storage via `_read_table()`, returning empty results, while `Table.search()` and `Table.count()` return stale results from `self._query_cache`.

## 4. Requirements
### FR-001 — Table drop invalidates query cache and internal state
- Statement: The library shall ensure that dropping a table via `TinyDB.drop_table()` or `TinyDB.drop_tables()` clears the query cache and resets internal tracking state (such as ID sequence counters) of any associated table instances.
- Provenance: STATED (SRC-01)
- Status: READY

### FR-002 — Retained table instances reflect empty state on all read operations
- Statement: The library shall ensure that methods like `search()`, `count()`, `all()`, and `len()` on any table instance return results consistent with an empty table after the table has been dropped and recreated or emptied.
- Provenance: STATED (SRC-01)
- Status: READY

### FR-003 — New insertions on dropped and re-accessed tables start ID sequence at 1
- Statement: The library shall ensure that when documents are inserted into a table after it has been dropped and recreated, document IDs begin at 1.
- Provenance: STATED (SRC-01)
- Status: READY

## 5. Acceptance criteria
### AC-1: Retained table search and count return empty results after drop_table
- Given `db = TinyDB(storage=MemoryStorage)` and `users = db.table('users')` containing inserted documents
- When `db.drop_table('users')` is called while holding a reference to `users`
- Then `users.search(where('name') == 'ann')` returns `[]` and `users.count(where('name') == 'ann')` returns `0`

### AC-2: Retained table ID sequence restarts at 1 after drop_table
- Given `db = TinyDB(storage=MemoryStorage)` and `users = db.table('users')` with inserted documents
- When `db.drop_table('users')` is called, followed by `users.insert({'name': 'cat'})`
- Then the returned document ID is `1` (or the first ID for a fresh table)

### AC-3: Drop tables clears query cache and ID state across all tables
- Given `db = TinyDB(storage=MemoryStorage)`, with multiple tables containing documents, and references held to those tables
- When `db.drop_tables()` is called
- Then calling `search()` and `count()` on those table references returns empty results, and subsequent insertions start at ID `1`

### AC-4: Unaffected database operations remain functional
- Given `db = TinyDB(storage=MemoryStorage)` and `users = db.table('users')`
- When documents are inserted, queried normally without a drop, and retrieved via `all()` and `search()`, normal TinyDB database operations continue to function correctly.
- Then documents are found and returned correctly as in standard TinyDB usage.

## 6. Assumptions and open questions
- ASM-01: Retained `Table` Python object instances should remain usable (i.e. empty) after being dropped rather than raising errors upon subsequent method calls. (Rationale: matches user expectations in tests where table variables are held across setup/teardown steps).

## 7. Out of scope
- Changing the underlying storage engines or persistence file formats.
- Adding database-level transactions or rollbacks.

## 8. Injection notes
- none


---
## Appendix — stage 1 check (Controller)
Result: FAIL
- AC-4: vague wording ['correctly']
- skipped: lint failed

Spec judge raw verdicts:
```json
{}
```
