-- Stop worker and restore matching application code; keep all physical facts.
@@../2026-10-09_ni032_replenishment_capacity/002_wave.sql
@@../2026-10-08_stock_posting_core/245_ni032_chunk_recovery_rollback.sql
@@../2026-10-08_stock_posting_core/246_ni032_chunk_case_rollback.sql
@@../2026-10-08_stock_posting_core/014b_recompile.sql
update RRL_SCHEMA_MIGRATIONS set STATUS='ROLLED_BACK' where MIGRATION_ID='2026-10-09-015-recovery-chunks';
commit;
/
