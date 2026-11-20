# Hidden acceptance tests

Written by hand for each of the five issues, before any agent ran, and **never committed to the
fork**: agents cannot see them. Run them with `tools/run_hidden.sh <issue> <PR|diff.patch>`.

Validation against the fork's `main` (pytest, Python 3.12). "Guard" tests check behaviour that must
*not* change, so they pass on base by design:

| Issue | Tests | On base | With `reference/issue_<k>.patch` | Full existing suite with the reference fix |
|---|---|---|---|---|
| 1 dropped table stale | 4 (1 guard) | 3 failed, 1 passed | 4 passed | 227 passed, 1 skipped |
| 2 insert_multiple ids | 4 (1 guard) | 3 failed, 1 passed | 4 passed | 227 passed, 1 skipped |
| 3 count() | 4 (1 guard) | 3 failed, 1 passed | 4 passed | 227 passed, 1 skipped |
| 4 operations.append | 3 | 3 failed | 3 passed | 227 passed, 1 skipped |
| 5 messy data (vague) | 4 (1 guard) | 3 failed, 1 passed | 4 passed | 227 passed, 1 skipped |

Issue 5 is vague. Its hidden tests encode the most conservative reading: incomparable values do not
match, and the search does not raise. An agent that picks another reasonable reading (e.g. raising a
clearer error) will fail them. That is a threat to validity, and the report discusses it.

**Note from building the issue set.** The first bug candidate ("mutating a document returned by
`search()` corrupts the query cache") was dropped. Upstream pins the current behaviour with an
existing test (`tests/test_tinydb.py::test_query_cache_documents_are_shared_with_cache`). Any fix
must break that test, and our stage-4 check ("all existing tests pass", agents cannot edit existing
tests) would correctly stop the run. It was replaced by the stale-`drop_table` bug.
