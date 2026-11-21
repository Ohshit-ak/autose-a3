# Spec — Operation to append a value to a list field
## 1. Source
SRC-01: GitHub issue #4 (quote the key sentences verbatim, as quotes)
> "`tinydb.operations` already has `increment`, `add`, `set`, `delete`... It would be great to have something like `operations.append('tags', 'db')` that appends a value to a list field (and starts a new list if the document doesn't have that field yet)."

## 2. Problem and goal
Users of TinyDB frequently need to append values (such as tag items) to list fields within documents. Currently, this requires writing custom transformation functions (e.g., using `.setdefault('tags', []).append(...)`). The goal is to add an `append` operation to `tinydb.operations` that appends a value to a specified list field, initializing the field as a new list if it does not already exist in the document.

## 3. Current behaviour (evidence)
- `tinydb.operations` contains operations like `delete`, `add`, `subtract`, `set`, `increment`, and `decrement` (`tinydb/operations.py:16-74`).
- There is no built-in `append` operation to append elements to list fields; users must supply a custom callable to `db.update(...)`.

## 4. Requirements
### FR-001 — Append operation for list fields
- Statement: The library shall provide an `append(field, value)` function in `tinydb.operations` that returns a transformation callable appending `value` to the list stored at `field`, creating a new list containing `value` if `field` is not present in the document.
- Provenance: STATED (SRC-01)
- Status: READY

### FR-002 — Existing operations preservation
- Statement: Existing update operations (`delete`, `add`, `subtract`, `set`, `increment`, `decrement`) shall continue to function correctly and remain unaffected by the addition of `append`.
- Provenance: DERIVED (implied standard regression requirement for library additions)
- Status: READY

## 5. Acceptance criteria
### AC-1: Append to existing list field (verifies FR-001)
- Given `db = TinyDB(storage=MemoryStorage)` containing a document `{'name': 'post-1', 'tags': ['python']}`
- When `db.update(append('tags', 'db'), where('name') == 'post-1')` is called
- Then `db.get(where('name') == 'post-1')['tags']` returns `['python', 'db']`

### AC-2: Append to missing field creates new list (verifies FR-001)
- Given `db = TinyDB(storage=MemoryStorage)` containing a document `{'name': 'post-2'}` (where `tags` field is absent)
- When `db.update(append('tags', 'python'), where('name') == 'post-2')` is called
- Then `db.get(where('name') == 'post-2')['tags']` returns `['python']`

### AC-3: Existing operations remain unaffected (verifies FR-002)
- Given `db = TinyDB(storage=MemoryStorage)` containing a document `{'name': 'post-1', 'int': 1, 'char': 'a'}`
- When `db.update(increment('int'), where('name') == 'post-1')` is called
- Then `db.get(where('name') == 'post-1')['int']` returns `2`

## 6. Assumptions and open questions
- ASM-01: The function signature will be `append(field: str, val: Any) -> Callable[[MutableMapping], None]`, matching the design pattern of other operations in `tinydb.operations`.

## 7. Out of scope
- Methods for prepending values, removing specific items from lists via operations, or nested field path list manipulations beyond standard top-level/dotted field handling consistent with other operations.

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
    "reason": "The Given, When, and Then provide concrete setup, a deterministic action via the public API, and a precise observable assertion."
  },
  "AC-2": {
    "testable": true,
    "reason": "The Given, When, and Then provide concrete setup for a missing field, a clear update action, and a precise expected list outcome."
  },
  "AC-3": {
    "testable": true,
    "reason": "The Given, When, and Then clearly specify an existing operation (increment) and verify that it continues to work correctly through the public API."
  }
}
```
