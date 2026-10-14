@@../2026-10-08_stock_posting_core/261_repl_bind_snapshot_rollback.sql
@@../2026-10-08_stock_posting_core/262_task_plan_snapshot_rollback.sql
@@../2026-10-08_stock_posting_core/263_task_core_snapshot_rollback.sql
@@../2026-10-08_stock_posting_core/014b_recompile.sql
update RRL_SCHEMA_MIGRATIONS set STATUS='ROLLED_BACK' where MIGRATION_ID='2026-10-09-025-binding-snapshot';
commit;
/
