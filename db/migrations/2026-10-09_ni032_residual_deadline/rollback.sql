@@../2026-10-08_stock_posting_core/250_ni032_residual_deadline_rollback.sql
@@../2026-10-08_stock_posting_core/014b_recompile.sql
update RRL_SCHEMA_MIGRATIONS set STATUS='ROLLED_BACK' where MIGRATION_ID='2026-10-09-018-residual-deadline';
commit;
/
