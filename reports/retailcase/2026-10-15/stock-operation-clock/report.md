# Independent clock acceptance — 15.10.2026

`python scripts/stock_operation_clock_smoke.py` — PASS, 8 checks, 1.396 s.

The runner reused the bounded WAVE395 source from `warehouse_task_scoped_complete_smoke.py` and its temporary user/resource/task/grant setup and cleanup. Native `prepare_command` + `execute_prepared` ran inside a caller transaction deliberately rolled back. No `NativeAPI.post` and no stock commit.

- Fresh TASK_COMPLETE reached APPLIED and produced exactly one clock with the same operation/actor/kind, source ORACLE_SYSTIMESTAMP, UTC offset 0, and timestamp between the two actual Oracle time observations.
- UPDATE and DELETE were rejected with STOCK_CLOCK_APPEND_ONLY.
- Caller rollback removed operation and clock and restored source/location physical quantity, hard reservation and stock version exactly.
- Existing committed original request replayed unchanged. Changed body conflicted, revoked current actor could not replay, and the original operation received no clock backfill.
- Temporarily committed fixture metadata was removed and historical QA user identity restored exactly. Native access audit history was retained.
- Counts before/after: 5021 stock operations, 0 clock rows. Zero clock rows after the test is intentional rollback evidence, not absence of the positive in-transaction assertion.
- Both actual USER_SOURCE trigger bodies matched the migration file after whitespace normalization; migration ledger APPLIED and INVALID0 before/after. SHA256 values are in [native-report.json](native-report.json).

Fresh RRL_SQL_SLOW_LOG interval: positive 267 ms, changed-body refusal 81 ms, exact replay 73 ms, revoked replay 11 ms. No new entry above 500 ms. Decision: retain address lookup by operation PK and fixed fixture identifiers; no new index or widening query required. This is a bounded functional test, not a throughput/load result.

The first runner attempt stopped at its SELECT using Oracle-reserved bind name `:start` (ORA-01745). Stock transaction rolled back and fixture cleanup ran. Renaming that test bind to `:clock_begin` yielded the PASS above; no production SQL was changed to satisfy the test.

Limits: clock records APPLIED observation inside the transaction, not commit time or physical pick time. Oracle wall-clock synchronization remains an operational requirement. No historical timezone inference, KPI denominator or physical device acceptance is established here.
