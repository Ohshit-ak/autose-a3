# Spec — Search crashes on older data

## 1. Source
SRC-01: GitHub issue #5
> "Our app has been running for a couple of years and the database has some older records that were written by previous versions of our code, so not every document looks the same. Since then, some searches just crash with errors like
> `TypeError: '>' not supported between instances of 'str' and 'int'`
> and the whole page fails. Other searches work fine. I don't really want to migrate all the old data. TinyDB should be more forgiving here, or at least not take my whole app down because of one weird record."

## 2. Problem and goal
- **Problem:** When querying older documents where a field has an unexpected type (e.g. string instead of integer), comparison queries (such as `>`, `<`, `>=`, `<=`) raise an unhandled `TypeError` during comparison (e.g. `'str' and 'int'`), crashing the query evaluation and failing the application request.
- **Goal:** Make TinyDB query evaluation evaluate comparisons with incompatible types as returning `False` instead of raising an uncaught exception that crashes the application.

## 3. Current behaviour (evidence)
- In `tinydb/queries.py` lines 280–330, comparison operators (`__lt__`, `__le__`, `__gt__`, `__ge__`) evaluate `value < rhs`, `value <= rhs`, `value > rhs`, `value >= rhs` inside `_generate_test` runner without catching `TypeError` caused by incompatible types (e.g. `str` vs `int`):
  - `tinydb/queries.py:280` (`__lt__`)
  - `tinydb/queries.py:293` (`__le__`)
  - `tinydb/queries.py:306` (`__gt__`)
  - `tinydb/queries.py:319` (`__ge__`)
- When path resolution succeeds (`KeyError` or `TypeError` during path traversal is caught at line 243), but the comparison operation itself raises `TypeError`, it propagates out of the query callable and crashes the search call (`db.search(...)`).

## 4. Requirements

### FR-001 — Robust comparison operators against type errors
- Statement: The library shall catch `TypeError` exceptions raised during the execution of comparison query operations (`<`, `<=`, `>`, `>=`) and evaluate the query as returning `False` instead of raising an exception.
- Provenance: STATED (SRC-01)
- Status: READY
- Priority: MUST ("TinyDB should be more forgiving here, or at least not take my whole app down because of one weird record")

### FR-002 — Robust equality and inequality operators against type errors
- Statement: The library shall catch `TypeError` exceptions raised during equality (`==`) and inequality (`!=`) comparisons when comparing incompatible types, evaluating to `False` (for `==`) or `True` (for `!=`) respectively, or handling them without raising exceptions to caller.
- Provenance: DERIVED (DER-01: general robustness against heterogeneous document types during queries)
- Status: READY
- Priority: SHOULD

## 5. Acceptance criteria

### AC-1: Greater-than query with incompatible types returns False instead of crashing (verifies FR-001)
- Given a TinyDB database instance `db` containing a document with a string value for age `{'age': 'forty'}` and a query `Query().age > 30`
- When calling `db.search(Query().age > 30)`
- Then it returns an empty list `[]` and does not raise `TypeError`.

### AC-2: Less-than-or-equal query with incompatible types returns False instead of crashing (verifies FR-001)
- Given a TinyDB database instance `db` containing a document with a string value for age `{'age': 'forty'}` and a query `Query().age <= 50`
- When calling `db.search(Query().age <= 50)`
- Then it returns an empty list `[]` and does not raise `TypeError`.

### AC-3: Valid comparison queries return matching documents (verifies FR-001 and existing behaviour)
- Given a TinyDB database instance `db` containing a document with an integer age `{'age': 40}` and a query `Query().age > 30`
- When calling `db.search(Query().age > 30)`
- Then it returns the matching document list containing `{'age': 40}`.

## 6. Assumptions and open questions
- ASM-01: Type errors during comparison between document fields and query values should be treated as non-matching (returning `False` for comparisons like `<`, `<=`, `>`, `>=`, `==`, and `!=` as appropriate), mirroring how missing keys (`KeyError`) are treated as non-matching.

## 7. Out of scope
- Automatic data migration of older documents.
- Changing schema validation on insert.

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
    "reason": "Clear Given/When/Then with exact inputs, public API calls, and observable outputs (returns empty list without raising TypeError)."
  },
  "AC-2": {
    "testable": true,
    "reason": "Clear Given/When/Then with exact inputs, public API calls, and observable outputs (returns empty list without raising TypeError)."
  },
  "AC-3": {
    "testable": true,
    "reason": "Clear Given/When/Then with specific document input, query execution, and deterministic return value containing the matching document."
  }
}
```
