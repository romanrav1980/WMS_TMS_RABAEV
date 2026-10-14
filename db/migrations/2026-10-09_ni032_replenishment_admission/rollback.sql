@@../2026-10-08_stock_posting_core/265_repl_admission_wave_rollback.sql
@@../2026-10-08_stock_posting_core/266_repl_admission_core_rollback.sql
-- Keep additive policy data for investigation; reverting behavior is explicit.
@@../2026-10-08_stock_posting_core/014b_recompile.sql
update RRL_SCHEMA_MIGRATIONS set STATUS='ROLLED_BACK' where MIGRATION_ID='2026-10-09-029-replenishment-admission';
commit;
/
