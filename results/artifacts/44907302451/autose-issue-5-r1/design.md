# Design — Search crashes on older data

## Summary
When querying older documents where a field has an unexpected type (e.g. string instead of integer), comparison queries (`<`, `<=`, `>`, `>=`, `==`, `!=`) currently raise an unhandled `TypeError` during comparison, crashing the search. We will wrap the comparison test execution in `_generate_test` runner (or within the operator test functions) so that `TypeError` is caught and evaluated as returning `False` (for `<`, `<=`, `>`, `>=`, `==`) or `True` (for `!=` as per standard inequality semantics, or handled gracefully). Specifically, FR-001 requires `<, <=, >, >=` to return `False`, and FR-002 specifies equality/inequality handling as well. Since `_generate_test` catches `(KeyError, TypeError)` during path traversal, catching `TypeError` during the `test(value)` execution (or inside the comparison operators) prevents crashes.

## Files to change
| Path | Change | Functions/classes |
|---|---|---|
| tinydb/queries.py | modify | Query._generate_test |
| tests/test_autose_issue_5.py | NEW | tests for AC-1, AC-2, AC-3 (NEW) |

## Public interface
- `Query.__lt__`, `Query.__le__`, `Query.__gt__`, `Query.__ge__`, `Query.__eq__`, `Query.__ne__` return `QueryInstance` objects that, when evaluated against documents with incompatible types, catch `TypeError` and evaluate to `False` (or `True` for `!=`).

## Change plan
1. Modify `Query._generate_test` in `tinydb/queries.py` to catch `TypeError` around `test(value)` as well, or update `runner` such that `test(value)` catching `TypeError` returns `False`. Wait, `!=` should return `True` on `TypeError` (e.g., `'forty' != 30` is `True`, because a string is not equal to an integer). Let's check `__eq__` and `__ne__`:
   - For `==`: `value == rhs` raises `TypeError` for incompatible types in Python 3 (e.g. `'forty' == 30` returns `False` without raising, but some types might raise or we want to be safe). Wait, does `'forty' == 30` raise in Python? No, `==` returns `False` normally, but `!=` returns `True`. However, some custom classes or specific comparisons might raise `TypeError`. If we catch `TypeError` during `test(value)`, for `==` returning `False` is correct. For `!=`, if `value != rhs` raises `TypeError`, they are not equal, so it should return `True`.
   - Alternatively, handle `TypeError` specifically in the comparison operators or wrap `test(value)` with a try/except for `TypeError`, but noting whether it's `!=`.
   - Let's look at `_generate_test`:
     ```python
     def runner(value):
         try:
             # Resolve the path
             for part in self._path:
                 if isinstance(part, str):
                     value = value[part]
                 else:
                     value = part(value)
         except (KeyError, TypeError):
             return False
         else:
             # Perform the specified test
             try:
                 return test(value)
             except TypeError:
                 return False # Wait, what about __ne__?
     ```
   - For `__ne__`, the test is `lambda value: value != rhs`. If `value != rhs` raises `TypeError`, are they unequal? Yes, incompatible types are not equal, so `!=` should return `True`.
   - Therefore, we can handle `TypeError` inside the specific operator lambdas or handle inequality separately.
   - Let's check operators:
     - `__eq__`: `lambda value: value == rhs` (already returns `False` usually, but we can wrap in try/except returning `False`).
     - `__ne__`: `lambda value: value != rhs` (if raises `TypeError`, return `True`).
     - `__lt__`, `__le__`, `__gt__`, `__ge__`: catch `TypeError` and return `False`.

2. Write comprehensive tests in `tests/test_autose_issue_5.py` covering AC-1, AC-2, and AC-3.

## AC mapping
- AC-1 → `tests/test_autose_issue_5.py`: test greater-than query with incompatible types returns `[]` without raising `TypeError`.
- AC-2 → `tests/test_autose_issue_5.py`: test less-than-or-equal query with incompatible types returns `[]` without raising `TypeError`.
- AC-3 → `tests/test_autose_issue_5.py`: test valid comparison queries return matching documents successfully.

## Architecture constraints check
- C1-C5 kept. No changes to storage, database, or layering rules. `queries.py` remains independent of `table.py`.

## Risks
- None.


---
## Appendix — stage 2 check (Controller)
Result: PASS
- 2 file(s) named; all functions resolved; all ACs mapped
