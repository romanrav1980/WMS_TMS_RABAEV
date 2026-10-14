@@rollback_index.sql
@@../2026-10-08_stock_posting_core/222_ni032_task_plan_rollback.sql
@@../2026-10-08_stock_posting_core/221_ni032_task_core_rollback.sql
@@verify.sql
update RRL_SCHEMA_MIGRATIONS set STATUS='ROLLED_BACK' where MIGRATION_ID='2026-10-09-008-task-recovery';
commit;
/
