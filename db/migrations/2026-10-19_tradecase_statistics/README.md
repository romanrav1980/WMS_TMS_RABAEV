# 2026-10-19-tradecase-statistics
Measured problem: new TRADECASE tables had no optimizer statistics; receipt-unit statistics described408 rows and were stale. Mixed-owner query SQL95u68t05w9bsq required dynamic sampling and reached152ms on its first execution. V$SQL_PLAN is unavailable to this account; this migration does not broaden privileges or add an unproven index.

Apply preserves original receipt-unit/table-index statistics in RRL_TC_STATS_20261019, then gathers exact statistics on six small TRADECASE tables and receipt units. It changes no business rows, rights, reservations or quantities. Rollback deletes the previously absent statistics on those six tables and imports the saved receipt statistics. Keep the backup table for rollback; do not recreate its baseline on repeated apply.

Compare runtime/test-evidence/tradecase/2026-10-19/T12/reads-before-stats.json with reads-after-stats.json: identical sequential GETs,6samples/path, first request separate from median of5warm requests, exact result hashes. Shared pool was already warm and other UI reads may coexist. These measurements do not certify production throughput.
