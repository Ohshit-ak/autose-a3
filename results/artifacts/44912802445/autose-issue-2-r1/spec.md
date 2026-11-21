# Spec — Document IDs skip numbers after a failed insert_multiple

## 1. Source
SRC-01: GitHub issue #2:
> When `insert_multiple` fails half way (one of the items in my batch was bad), nothing is inserted — good — but the next document I insert gets an ID that skips over the IDs the failed batch would have used. We use doc IDs as visible ticket numbers, so the gaps confuse our users.
>
> Same thing happens when the batch fails because one of the `Document`s has an ID that already exists. I'd expect a failed batch to leave everything exactly as it was, including the next ID.

## 2. Problem and goal
- **Problem:** When `Table.insert_multiple()` encounters a validation or collision error mid-execution, the transaction / update aborts and no documents are inserted into the table, but internal ID tracking state (`self._next_id`) has already been mutated during the failed batch processing. As a result, subsequent single document insertions (`insert()`) skip document ID numbers corresponding to the IDs that were allocated or considered during the failed batch.
- **Goal:** Ensure that a failed `insert_multiple()` invocation leaves the table and all internal sequence/ID generation state (`self._next_id`) completely unaffected, so that subsequent insertions receive contiguous document IDs without gaps.

## 3. Current behaviour (evidence)
- In `tinydb/table.py:179` (`insert_multiple`), when processing an iterable of documents, `self._next_id` is modified as individual items are evaluated via `_get_next_id()` (lines 225–226):
  ```python
  next_id = self._next_id
  if next_id is None:
      if table:
          next_id = max(
              self.document_id_class(i) for i in table.keys()
          ) + 1
      else:
          next_id = 1
  self._next_id = next_id
  doc_id = self._get_next_id()
  ```
- If an exception (such as `ValueError` due to a non-Mapping item or an existing document ID collision) occurs later in the loop (lines 193 or 198), `self._update_table(updater)` raises the exception and aborts table storage modification, but `self._next_id` on the `Table` instance has already been mutated in memory.

## 4. Requirements

### FR-001 — Atomic ID tracking on failed insert_multiple
- Statement: The library shall ensure that if `insert_multiple` fails and raises an exception (such as invalid document format or document ID collision), internal next-ID allocation state (`_next_id`) is not mutated or advanced.
- Provenance: STATED (SRC-01)
- Status: READY

### FR-002 — Contiguous ID allocation after failed batch
- Statement: The library shall ensure that any subsequent single `insert()` call immediately following a failed `insert_multiple()` call assigns the correct next sequential document ID without skipping numbers.
- Provenance: STATED (SRC-01)
- Status: READY

## 5. Acceptance criteria

### AC-1: Next ID is preserved after `insert_multiple` failure due to invalid document type
- Given a `TinyDB` instance with storage `MemoryStorage` containing one document with ID `1` (`db.insert({'t': 'first'})` -> `1`),
- When `db.insert_multiple([{'t': 'ok'}, 'oops not a dict', {'t': 'ok2'}])` is executed and catches `ValueError`,
- Then a subsequent call to `db.insert({'t': 'second'})` returns `2`.

### AC-2: Next ID is preserved after `insert_multiple` failure due to existing document ID collision
- Given a `TinyDB` instance with storage `MemoryStorage` containing a document with ID `1` (`db.insert({'t': 'first'})` -> `1`),
- When `db.insert_multiple([Document({'t': 'ok'}, 1)])` is executed and catches `ValueError` (due to ID `1` already existing),
- Then a subsequent call to `db.insert({'t': 'second'})` returns `2`.

### AC-3: Successful `insert_multiple` behavior remains unaffected
- Given an empty `TinyDB` instance with storage `MemoryStorage`,
- When `db.insert_multiple([{'t': 'a'}, {'t': 'b'}])` is executed successfully,
- Then the returned document IDs are `[1, 2]` and a subsequent call to `db.insert({'t': 'c'})` returns `3`.

## 6. Assumptions and open questions
- ASM-01: ID state preservation can be achieved either by computing IDs on a temporary copy or rolling back `_next_id` / postponing `_next_id` mutation until after validation/execution succeeds.

## 7. Out of scope
- Changing ID assignment behavior for successful insertions or custom document ID classes beyond fixing the gap bug on failure.

## 8. Injection notes
- none


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
    "reason": "The Given, When, and Then provide concrete steps, actions, and observable return values to write a deterministic pytest test."
  },
  "AC-2": {
    "testable": true,
    "reason": "The Given, When, and Then specify clear setup, expected exception handling, and a concrete observable return value for the subsequent insert."
  },
  "AC-3": {
    "testable": true,
    "reason": "The Given, When, and Then outline precise inputs, expected list of IDs, and the resulting ID for a subsequent insert, making it fully testable."
  }
}
```
