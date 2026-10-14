-- Restore matching application code too. Retain all physical facts and scan evidence.
@@../2026-10-08_stock_posting_core/247_ni032_case_resources_rollback.sql
@@../2026-10-08_stock_posting_core/248_ni032_operator_plan_rollback.sql
@@../2026-10-08_stock_posting_core/249_ni032_case_metadata_rollback.sql
@@003_warehouse_before.sql
drop package RRL_CASE_RESOURCE_POLICY;
@@../2026-10-08_stock_posting_core/014b_recompile.sql
update RRL_SCHEMA_MIGRATIONS set STATUS='ROLLED_BACK' where MIGRATION_ID='2026-10-09-016-case-resources';
commit;
/
