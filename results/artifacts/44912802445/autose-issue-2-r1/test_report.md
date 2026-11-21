# Test report — issue #2 (round 1, variant single-pass)

| Attempt | Builder summary (truncated) | Build | New tests | Full suite | Result |
|---|---|---|---|---|---|
| 1 | Implemented atomic ID tracking in Table.insert_multiple(). When insert_multiple() fails validation or collision checks m | ok | 3 passed in 0.01s | 230 passed, 1 skipped in 0.71s | PASS |

## Acceptance-criterion coverage

| AC | Tests | Red on base? |
|---|---|---|
| AC-1 | test_ac1_next_id_preserved_after_insert_multiple_invalid_type | test_ac1_next_id_preserved_after_insert_multiple_invalid_type: FAILED |
| AC-2 | test_ac2_next_id_preserved_after_insert_multiple_collision | test_ac2_next_id_preserved_after_insert_multiple_collision: PASSED |
| AC-3 | test_ac3_successful_insert_multiple_behavior | test_ac3_successful_insert_multiple_behavior: PASSED |

- New tests: `3 passed in 0.01s`
- Full suite: `230 passed, 1 skipped in 0.71s`
- *Red on base* = the new test FAILED against the unmodified code (the expected result for new behaviour; tests of unchanged behaviour pass on base by design).

## Check result: PASS
