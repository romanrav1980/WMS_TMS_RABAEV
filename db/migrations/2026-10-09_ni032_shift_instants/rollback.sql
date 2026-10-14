@@../2026-10-08_stock_posting_core/273_shift_instant_policy_rollback.sql
@@../2026-10-08_stock_posting_core/274_shift_instant_plan_rollback.sql
@@../2026-10-08_stock_posting_core/275_shift_instant_core_rollback.sql
@@../2026-10-08_stock_posting_core/014b_recompile.sql
-- Keep recorded instants; deploy the prior matching task-assignment application.
update RRL_SCHEMA_MIGRATIONS set STATUS='ROLLED_BACK' where MIGRATION_ID='2026-10-09-035-shift-instants';
commit;
/
