-- Stop recovery worker and restore matching code first.
@@../2026-10-08_stock_posting_core/241_ni032_capacity_wave_rollback.sql
@@../2026-10-08_stock_posting_core/242_ni032_capacity_plan_rollback.sql
@@../2026-10-08_stock_posting_core/243_ni032_capacity_core_rollback.sql
@@../2026-10-08_stock_posting_core/244_ni032_wave_state_case_rollback.sql
drop package RRL_STOCK_REPL_CAPACITY;
@@../2026-10-08_stock_posting_core/014b_recompile.sql
update RRL_SCHEMA_MIGRATIONS set STATUS='ROLLED_BACK' where MIGRATION_ID='2026-10-09-014-replenishment-capacity';
commit;
/
