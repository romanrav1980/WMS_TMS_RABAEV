drop trigger RRL_QC_MASS_POLICY_GUARD
/
@@../2026-10-08_stock_posting_core/330_checkpoint_quality_gate.sql
@@../2026-10-08_stock_posting_core/331_checkpoint_quality_weight.sql
@@../2026-10-08_stock_posting_core/014b_recompile.sql
update RRL_SCHEMA_MIGRATIONS set STATUS='ROLLED_BACK' where MIGRATION_ID='2026-10-10-061-si-quality-weight';
commit;
/