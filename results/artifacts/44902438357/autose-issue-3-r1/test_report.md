# Test report — issue #3 (round 1, variant default)

| Attempt | Builder summary (truncated) | Build | New tests | Full suite | Result |
|---|---|---|---|---|---|
| 1 | Made `cond` parameter optional in `Table.count(self, cond: Optional[QueryLike] = None) -> int`. When `cond` is `None` (o | ok | 4 passed in 0.01s | 231 passed, 1 skipped in 0.66s | PASS |

## Acceptance-criterion coverage

| AC | Tests | Red on base? |
|---|---|---|
| AC-1 | test_ac1_table_count_without_argument | test_ac1_table_count_without_argument: FAILED |
| AC-2 | test_ac2_tinydb_count_without_argument | test_ac2_tinydb_count_without_argument: FAILED |
| AC-3 | test_ac3_table_count_with_query_preserves_existing_behaviour | test_ac3_table_count_with_query_preserves_existing_behaviour: PASSED |
| AC-4 | test_ac4_unchanged_len_behaviour_remains_the_same | test_ac4_unchanged_len_behaviour_remains_the_same: PASSED |

- New tests: `4 passed in 0.01s`
- Full suite: `231 passed, 1 skipped in 0.66s`
- *Red on base* = the new test FAILED against the unmodified code (the expected result for new behaviour; tests of unchanged behaviour pass on base by design).

## Check result: PASS
