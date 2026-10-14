-- Restore matching app first. Preserve immutable scan evidence and stock history.
@@../2026-10-08_stock_posting_core/239_ni032_scans_plan_rollback.sql
@@../2026-10-08_stock_posting_core/240_ni032_scans_core_rollback.sql
drop package RRL_STOCK_TASK_SCAN;
@@../2026-10-08_stock_posting_core/014b_recompile.sql
update RRL_SCHEMA_MIGRATIONS set STATUS='ROLLED_BACK' where MIGRATION_ID='2026-10-09-012-task-scans';
commit;
/
