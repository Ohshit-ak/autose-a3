# Spec — Let count() work without a query

## 1. Source
SRC-01: GitHub issue #3
> `db.count(query)` is handy, but when I want the total number of documents I have to remember to use `len(db)` / `len(table)` instead, and `db.count()` just blows up:
> `TypeError: Table.count() missing 1 required positional argument: 'cond'`
> Could `count()` with no argument simply return the number of documents in the table? Counting with a query should keep working the same way it does today.

## 2. Problem and goal
Currently, `Table.count(cond)` requires a `cond` parameter (a query condition). Calling `count()` with no arguments on a `Table` object (or on a `TinyDB` instance via attribute forwarding to the default table) raises a `TypeError` because `cond` is required. Users expect `count()` without arguments to return the total number of documents in the table, equivalent to `len(table)` or `len(db)`.

The goal is to make `cond` optional in `Table.count([cond])` such that calling `table.count()` returns the total number of documents in that table, while calling `table.count(cond)` continues to return the count of documents matching the query condition.

## 3. Current behaviour (evidence)
- In `tinydb/table.py` at line 709, `count` is defined as:
  ```python
  def count(self, cond: QueryLike) -> int:
      return len(self.search(cond))
  ```
  `cond` is a required positional argument. Calling `table.count()` raises `TypeError: Table.count() missing 1 required positional argument: 'cond'`.
- `tinydb/table.py` line 725 defines `__len__(self)`:
  ```python
  def __len__(self):
      return len(self._read_table())
  ```
  which counts all documents in the table.
- `tinydb/database.py` line 251 uses `__getattr__` to forward non-existing attributes on `TinyDB` instances to the default table (`self.table(self.default_table_name)`). Thus `db.count(...)` forwards to `Table.count(...)`.

## 4. Requirements
### FR-001 — Optional condition in `count()`
- Statement: The `Table.count()` method shall accept an optional condition argument `cond` (defaulting to `None` or omitted). When called without arguments (or when `cond` is not provided), it shall return the total count of documents in the table (equivalent to `len(table)`).
- Provenance: STATED (SRC-01: "Could `count()` with no argument simply return the number of documents in the table?")
- Status: READY

### FR-002 — Preserve query counting behaviour
- Statement: When `Table.count(cond)` is called with a query condition `cond`, it shall return the number of documents matching `cond`, preserving existing behaviour.
- Provenance: STATED (SRC-01: "Counting with a query should keep working the same way it does today.")
- Status: READY

## 5. Acceptance criteria
### AC-1: `count()` without arguments returns total document count on Table
- Given a `Table` instance containing 3 documents
- When `table.count()` is called with no arguments
- Then it returns `3`

### AC-2: `count()` without arguments returns total document count on default table via TinyDB instance
- Given a `TinyDB` instance `db` (using `MemoryStorage`) containing 2 documents in the default table
- When `db.count()` is called with no arguments
- Then it returns `2`

### AC-3: `count(cond)` with a query condition returns matching document count
- Given a `Table` instance containing documents `{'type': 'apple'}`, `{'type': 'apple'}`, and `{'type': 'orange'}`
- When `table.count(Query().type == 'apple')` is called
- Then it returns `2`

### AC-4: `count()` on an empty table returns 0
- Given an empty `Table` instance
- When `table.count()` is called with no arguments
- Then it returns `0`

## 6. Assumptions and open questions
ASM-01: Calling `table.count(None)` or `table.count()` both trigger the total count behavior when no query condition is passed.
Q-01: None.

## 7. Out of scope
- Modifying `search()` or other table query methods.
- Changing `__len__` behaviour.

## 8. Injection notes
none

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
    "reason": "Clear setup, deterministic call, and explicit observable expected value."
  },
  "AC-2": {
    "testable": true,
    "reason": "Clear setup using explicit storage, deterministic call, and unambiguous return value."
  },
  "AC-3": {
    "testable": true,
    "reason": "Clear document setup, concrete Query condition, and expected scalar return value."
  },
  "AC-4": {
    "testable": true,
    "reason": "Clear setup of empty table and precise expected return value of 0."
  }
}
```
