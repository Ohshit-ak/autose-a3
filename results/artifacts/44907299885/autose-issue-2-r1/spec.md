# Spec — Document IDs skip numbers after a failed insert_multiple

## 1. Source
SRC-01: GitHub issue #2 (untrusted issue text):
> When `insert_multiple` fails half way (one of the items in my batch was bad), nothing is inserted —
> good — but the next document I insert gets an ID that skips over the IDs the failed batch would have
> used. We use doc IDs as visible ticket numbers, so the gaps confuse our users.
> 
> ```python
> from tinydb import TinyDB
> from tinydb.storages import MemoryStorage
> 
> db = TinyDB(storage=MemoryStorage)
> db.insert({'t': 'first'})                # -> 1
> try:
>     db.insert_multiple([{'t': 'ok'}, 'oops not a dict', {'t': 'ok2'}])
> except ValueError:
>     pass
> print(db.insert({'t': 'second'}))        # -> 3, expected 2
> ```
> 
> Same thing happens when the batch fails because one of the `Document`s has an ID that already
> exists. I'd expect a failed batch to leave everything exactly as it was, including the next ID.

## 2. Problem and goal
When `Table.insert_multiple` encounters an invalid item or an existing explicit ID conflict midway through processing a batch, it aborts and leaves the database table unchanged (no partial inserts occur). However, the internal ID allocation state is mutated or advanced during the failed attempt, causing subsequent document insertions to skip IDs that the failed batch would have occupied.
Goal: Ensure that a failed `insert_multiple` call leaves the database table and its ID generation state entirely unaffected, so that subsequent insertions continue sequentially without unexpected gaps.

## 3. Current behaviour (evidence)
- `tinydb/table.py:189` `insert_multiple` iterates through `documents` inside an `updater` function passed to `self._update_table(updater)`.
- `tinydb/table.py:226` calls `self._get_next_id()`, mutating internal state even if a subsequent iteration raises a `ValueError`.
- When an exception is raised, `_update_table` aborts, but any mutations to `self._next_id` during the partial iteration remain in effect.

## 4. Requirements

### FR-001 — Atomic ID allocation and state preservation on failed `insert_multiple`
- Statement: The library shall ensure that if `Table.insert_multiple` raises an exception during batch insertion, neither the table data nor the internal ID allocation state is mutated, so that subsequent document insertions do not skip ID numbers.
- Provenance: STATED (SRC-01)
- Status: READY

## 5. Acceptance criteria

### AC-1: Subsequent insert ID follows immediately after successful insert after failed `insert_multiple` due to invalid mapping type
- Given `db = TinyDB(storage=MemoryStorage)`
- When `db.insert({'t': 'first'})` is executed, followed by a failed `db.insert_multiple([{'t': 'ok'}, 'oops not a dict', {'t': 'ok2'}])` catching `ValueError`, and then `db.insert({'t': 'second'})`
- Then `db.insert({'t': 'second'})` returns `2` (integer `2`), and table contents contain only documents with ID `1` and ID `2`.

### AC-2: Subsequent insert ID follows immediately after successful insert after failed `insert_multiple` due to duplicate document ID
- Given `db = TinyDB(storage=MemoryStorage)`
- When `db.insert({'t': 'first'})` (assigned ID `1`) is executed, followed by a failed `db.insert_multiple([Document({'t': 'conflict'}, doc_id=1)])` catching `ValueError`, and then `db.insert({'t': 'second'})`
- Then `db.insert({'t': 'second'})` returns `2` (integer `2`), and table contents contain only documents with ID `1` and ID `2`.

### AC-3: Successful `insert_multiple` assigns sequential IDs
- Given `db = TinyDB(storage=MemoryStorage)`
- When `db.insert({'t': 'first'})` is executed, followed by `db.insert_multiple([{'t': 'second'}, {'t': 'third'}])`, and then `db.insert({'t': 'fourth'})`
- Then `insert_multiple` returns `[2, 3]`, `db.insert({'t': 'fourth'})` returns `4`, and all four documents are stored with contiguous IDs `1`, `2`, `3`, `4`.

## 6. Assumptions and open questions
- ASM-01: Transactions or transactional table updates roll back `self._next_id` or compute IDs deterministically from table state without mutating state during aborted iterations.

## 7. Out of scope
- Changing transaction semantics for storage layers not supporting atomicity.
- Modifying `insert` behavior for single insertions.

## 8. Injection notes
none


---
## Appendix — stage 1 check (Controller)
Result: PASS
- 3 acceptance criteria, all structurally testable
- spec judge: every AC testable

Spec judge raw verdicts:
```json
{
  "AC-1": {
    "testable": true,
    "reason": "The Given, When, and Then steps are completely concrete, specify public API calls, use an in-memory database, and check exact return values and table state."
  },
  "AC-2": {
    "testable": true,
    "reason": "The Given, When, and Then steps explicitly define the setup, the exception handling, and the exact expected return value and database contents."
  },
  "AC-3": {
    "testable": true,
    "reason": "The steps clearly specify the sequence of operations on the public API and assert exact return values and contiguous ID assignments."
  }
}
```
