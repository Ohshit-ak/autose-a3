# Design — Operation to append a value to a list field

## Summary
Add an `append(field, val)` operation to `tinydb.operations`. It returns a transformation function that appends `val` to an existing list stored at `field` in a document, or initializes `field` with a new single-element list `[val]` if `field` is not present in the document.

## Files to change
| Path | Change | Functions/classes |
|---|---|---|
| tinydb/operations.py | modify | append (NEW) |
| tests/test_autose_issue_4.py | NEW | tests for AC-1..AC-3 (NEW) |

## Public interface
```python
from collections.abc import Callable, MutableMapping
from typing import Any

def append(field: str, val: Any) -> Callable[[MutableMapping], None]:
    """
    Return a function that appends ``val`` to the list stored at ``field`` in a document.

    If ``field`` does not exist in the document, initialize it as a list containing ``val``.

    :param field: The field name to append to.
    :param val: The value to append.
    :return: A transformation function suitable for ``db.update(...)``.
    """
```

## Change plan

1. **`tinydb/operations.py`**:
   - Define `append(field: str, val: Any) -> Callable[[MutableMapping], None]`.
   - Inside `append`, define the inner function `transform(doc: MutableMapping)`:
     - Check if `field` is present in `doc`.
     - If `field in doc`, call `doc[field].append(val)`.
     - Otherwise, set `doc[field] = [val]`.
   - Return `transform`.

2. **`tests/test_autose_issue_4.py` (NEW)**:
   - Test appending to an existing list field (`AC-1`).
   - Test appending to a non-existent field, asserting a new list `[val]` is created (`AC-2`).
   - Test that existing operations (such as `increment`) continue to function properly (`AC-3`).

## AC mapping
- AC-1 → `tinydb/operations.py`: `append (NEW)` — `db.update(append('tags', 'db'), ...)` appends `'db'` to `['python']`, yielding `['python', 'db']`.
- AC-2 → `tinydb/operations.py`: `append (NEW)` — `db.update(append('tags', 'python'), ...)` initializes missing `'tags'` field to `['python']`.
- AC-3 → `tinydb/operations.py` (and `tests/test_autose_issue_4.py`) — Existing update operations like `increment` remain untouched and functional.

## Architecture constraints check
- C1 (Storages): Kept. Storage implementations are unchanged.
- C2 (Table mutations via `_update_table`): Kept. `append` returns a standard transformation callable passed to `db.update` / `Table.update`, which processes document modifications through `_update_table`.
- C3 (Query caching): Kept. No query structure or cache hashing logic is altered.
- C4 (Layering rules): Kept. `tinydb/operations.py` relies only on standard library types (`collections.abc.Callable`, `collections.abc.MutableMapping`, `typing.Any`) and does not import `table.py` or `database.py`.
- C5 (Storage options): Kept. No storage or middleware constructors are modified.

## Risks
None identified. This is a purely additive utility operation with no external dependencies and no side effects on existing modules.

---
## Appendix — stage 2 check (Controller)
Result: PASS
- 2 file(s) named; all functions resolved; all ACs mapped
