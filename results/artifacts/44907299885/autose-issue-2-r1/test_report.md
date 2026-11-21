# Test report — issue #2 (round 1, variant default)

| Attempt | Builder summary (truncated) | Build | New tests | Full suite | Result |
|---|---|---|---|---|---|
| 1 | Preserved `self._next_id` when `insert_multiple` raises an exception during batch processing. In `tinydb/table.py`, save | ok | 3 passed in 0.01s | 230 passed, 1 skipped in 0.55s | PASS |

## Acceptance-criterion coverage

| AC | Tests | Red on base? |
|---|---|---|
| AC-1 | test_ac1_insert_multiple_invalid_mapping_type | test_ac1_insert_multiple_invalid_mapping_type: FAILED |
| AC-2 | test_ac2_insert_multiple_duplicate_document_id | test_ac2_insert_multiple_duplicate_document_id: PASSED |
| AC-3 | test_ac3_successful_insert_multiple_sequential_ids | test_ac3_successful_insert_multiple_sequential_ids: PASSED |

- New tests: `3 passed in 0.01s`
- Full suite: `230 passed, 1 skipped in 0.55s`
- *Red on base* = the new test FAILED against the unmodified code (the expected result for new behaviour; tests of unchanged behaviour pass on base by design).

## Check result: PASS
