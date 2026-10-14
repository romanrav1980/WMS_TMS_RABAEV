-- Stop workers and restore matching application code first. Preserve additive columns/facts.
@@../2026-10-08_stock_posting_core/225_ni032_recovery_case_rollback.sql
@@../2026-10-08_stock_posting_core/226_ni032_recovery_short_rollback.sql
@@../2026-10-08_stock_posting_core/227_ni032_recovery_inventory_rollback.sql
@@../2026-10-08_stock_posting_core/228_ni032_recovery_domain_rollback.sql
@@../2026-10-08_stock_posting_core/229_ni032_recovery_plan_rollback.sql
@@../2026-10-08_stock_posting_core/230_ni032_recovery_wave_rollback.sql
@@../2026-10-08_stock_posting_core/231_ni032_recovery_eligibility_rollback.sql
@@../2026-10-08_stock_posting_core/232_ni032_recovery_reserve_acl_rollback.sql
@@../2026-10-08_stock_posting_core/233_ni032_recovery_unit_acl_rollback.sql
@@../2026-10-08_stock_posting_core/234_ni032_recovery_return_rollback.sql
@@../2026-10-08_stock_posting_core/235_ni032_recovery_metadata_rollback.sql
drop package RRL_STOCK_SHORT_RECOVERY;
@@../2026-10-08_stock_posting_core/014b_recompile.sql
update RRL_SCHEMA_MIGRATIONS set STATUS='ROLLED_BACK' where MIGRATION_ID='2026-10-09-010-short-recovery';
commit;
/
