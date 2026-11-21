# Spec — Document IDs skip numbers after a failed insert_multiple
## 1. Source
SRC-01: GitHub issue #2 ("When `insert_multiple` fails half way (one of the items in my batch was bad), nothing is inserted — good — but the next document I insert gets an ID that skips over the IDs the failed batch would have used. We use doc IDs as visible ticket numbers, so the gaps confuse our users.")

## 2. Problem and goal
- **Problem:** When `insert_multiple` fails during a batch (e.g. due to an invalid non-mapping item or an existing document ID), `self._next_id` may be mutated or left modified during the iteration before the exception is raised, causing subsequent single or batch insertions to skip over IDs that were allocated or considered during the failed attempt.
- **Goal:** Ensure that a failed `insert_multiple` call leaves the table's next ID allocation state (and all stored/cached table state) completely unchanged, exactly as it was before the call.

## 3. Current behaviour (evidence)
- In `tinydb/table.py` around line 211, `self._next_id = None` is set inside the iteration loop when encountering a `Document` with an explicit ID, and `self._get_next_id()` advances/mutates `self._next_id` inside `tinydb/table.py` line 226 as it iterates through items in a batch. If a later item in the batch fails, the modifications to `self._next_id` persist even though `self._update_table(updater)` aborts the transaction/update.

## 4. Requirements
### FR-001 — Preserve next ID state on failed `insert_multiple`
- Statement: The library shall ensure that if `insert_multiple` raises an exception (such as `ValueError`), the internal next document ID generator state (`self._next_id`) remains unaffected and does not skip ID numbers.
- Provenance: STATED
- Status: READY

### FR-002 — Preserve existing ID allocation parity for single inserts following failure
- Statement: The library shall ensure that subsequent calls to `insert()` after a failed `insert_multiple` assign IDs sequentially starting immediately after the last successfully stored document.
- Provenance: DERIVED (from SRC-01 and FR-001)
- Status: READY

## 5. Acceptance criteria
### AC-1: `insert_multiple` failure leaves next ID unchanged for subsequent single insert (verifies FR-001, FR-002)
- Given `db = TinyDB(storage=MemoryStorage)` and `db.insert({'t': 'first'})` returning `1`
- When `db.insert_multiple([{'t': 'ok'}, 'oops not a dict', {'t': 'ok2'}])` is called and raises `ValueError`
- Then a subsequent call to `db.insert({'t': 'second'})` returns `2` and not `3`

### AC-2: `insert_multiple` failure due to existing duplicate ID leaves next ID unchanged (verifies FR-001, FR-002)
- Given `db = TinyDB(storage=MemoryStorage)` and `db.insert({'t': 'first'})` returning `1`
- When `db.insert_multiple([Document({'t': 'conflict'}, 1)])` is called and raises `ValueError`
- Then a subsequent call to `db.insert({'t': 'second'})` returns `2`

### AC-3: Successful `insert_multiple` behaviour remains correct (verifies regression safety)
- Given `db = TinyDB(storage=MemoryStorage)` and `db.insert({'t': 'first'})` returning `1`
- When `db.insert_multiple([{'t': 'second'}, {'t': 'third'}])` is called successfully returning `[2, 3]`
- Then a subsequent call to `db.insert({'t': 'fourth'})` returns `4`

## 6. Assumptions and open questions
- ASM-01: Preserving `self._next_id` can be achieved by working on a local copy of `self._next_id` during the `updater` function and only committing the new `_next_id` state if the entire batch succeeds without raising an exception.

## 7. Out of scope
- Changing the transactional storage backend persistence guarantees beyond table-level memory/storage consistency.

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
    "reason": "The Given, When, and Then provide explicit inputs, actions, and observable return values using a standard test setup."
  },
  "AC-2": {
    "testable": true,
    "reason": "The Given, When, and Then clearly define the state, exception trigger, and exact return value for the subsequent insert."
  },
  "AC-3": {
    "testable": true,
    "reason": "The Given, When, and Then steps are fully concrete, specifying exact inputs and expected return values for both batch and subsequent operations."
  }
}
```
