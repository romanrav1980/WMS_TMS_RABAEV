@@../2026-10-08_stock_posting_core/224_ni032_resources_plan_rollback.sql
@@../2026-10-08_stock_posting_core/223_ni032_resources_core_rollback.sql
drop package RRL_TASK_RESOURCE_POLICY;
@@../2026-10-08_stock_posting_core/014b_recompile.sql
update RRL_SCHEMA_MIGRATIONS set STATUS='ROLLED_BACK' where MIGRATION_ID='2026-10-09-009-task-resource-policy';
commit;
/
