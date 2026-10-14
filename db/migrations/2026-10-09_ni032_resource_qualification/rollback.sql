-- Stop worker and restore matching app first. Keep additive metadata/history.
@@236_policy_before.sql
@@../2026-10-08_stock_posting_core/237_ni032_qualification_core_rollback.sql
@@../2026-10-08_stock_posting_core/238_ni032_qualification_metadata_rollback.sql
@@../2026-10-09_ni032_short_recovery/003_recovery.sql
@@../2026-10-08_stock_posting_core/014b_recompile.sql
update RRL_SCHEMA_MIGRATIONS set STATUS='ROLLED_BACK' where MIGRATION_ID='2026-10-09-011-resource-qualification';
commit;
/
