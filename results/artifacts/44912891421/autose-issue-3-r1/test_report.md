# Test report — issue #3 (round 1, variant single-pass)

| Attempt | Builder summary (truncated) | Build | New tests | Full suite | Result |
|---|---|---|---|---|---|
| 1 | Successfully implemented optional query condition in Table.count() (and TinyDB.count()) so that calling count() without  | ok | 4 passed in 0.01s | 231 passed, 1 skipped in 0.54s | PASS |

## Acceptance-criterion coverage

| AC | Tests | Red on base? |
|---|---|---|
| AC-1 | test_ac1_count_without_condition | test_ac1_count_without_condition: FAILED |
| AC-2 | test_ac2_count_with_query | test_ac2_count_with_query: PASSED |
| AC-3 | test_ac3_table_count_without_condition | test_ac3_table_count_without_condition: FAILED |
| AC-4 | test_ac4_table_count_with_query | test_ac4_table_count_with_query: PASSED |

- New tests: `4 passed in 0.01s`
- Full suite: `231 passed, 1 skipped in 0.54s`
- *Red on base* = the new test FAILED against the unmodified code (the expected result for new behaviour; tests of unchanged behaviour pass on base by design).

## Check result: PASS
