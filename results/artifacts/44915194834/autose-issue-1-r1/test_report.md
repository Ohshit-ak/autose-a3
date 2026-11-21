# Test report — issue #1 (round 1, variant default)

| Attempt | Builder summary (truncated) | Build | New tests | Full suite | Result |
|---|---|---|---|---|---|
| 1 | Implemented fix for issue #1: Table still returns old documents after drop_table() and drop_tables(). Added Table._reset | ok | 4 passed in 0.01s | 231 passed, 1 skipped in 0.57s | PASS |

## Acceptance-criterion coverage

| AC | Tests | Red on base? |
|---|---|---|
| AC-1 | test_ac1_stale_query_cache_cleared_after_drop_table | test_ac1_stale_query_cache_cleared_after_drop_table: FAILED |
| AC-2 | test_ac2_document_id_sequence_resets_after_drop_table | test_ac2_document_id_sequence_resets_after_drop_table: FAILED |
| AC-3 | test_ac3_stale_query_cache_and_id_sequence_cleared_after_drop_tables | test_ac3_stale_query_cache_and_id_sequence_cleared_after_drop_tables: FAILED |
| AC-4 | test_ac4_normal_table_operations_without_drop_remain_fully_functional | test_ac4_normal_table_operations_without_drop_remain_fully_functional: PASSED |

- New tests: `4 passed in 0.01s`
- Full suite: `231 passed, 1 skipped in 0.57s`
- *Red on base* = the new test FAILED against the unmodified code (the expected result for new behaviour; tests of unchanged behaviour pass on base by design).

## Check result: PASS
