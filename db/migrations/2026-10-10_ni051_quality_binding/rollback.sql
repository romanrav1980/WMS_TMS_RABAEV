-- Rollback code only; retain additive columns and immutable QC operation history.
drop trigger RRL_QC_STAMP_GUARD
/
drop trigger RRL_QC_ROWS_INVALIDATE
/
drop trigger RRL_QC_ROWS_INSERT
/
@@../2026-10-08_stock_posting_core/328_checkpoint_qc_shipping.sql
@@../2026-10-08_stock_posting_core/329_checkpoint_qc_command.sql
@@../2026-10-08_stock_posting_core/014b_recompile.sql
update RRL_SCHEMA_MIGRATIONS set STATUS='ROLLED_BACK' where MIGRATION_ID='2026-10-10-060-quality-composition-binding';
commit;
/