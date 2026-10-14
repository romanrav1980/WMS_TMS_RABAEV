@@../2026-10-08_stock_posting_core/267_repl_cont_plan_rollback.sql
@@../2026-10-08_stock_posting_core/268_repl_cont_core_rollback.sql
@@../2026-10-08_stock_posting_core/014b_recompile.sql
update RRL_SCHEMA_MIGRATIONS set STATUS='ROLLED_BACK' where MIGRATION_ID='2026-10-09-030-replenishment-continuation';
commit;
/
