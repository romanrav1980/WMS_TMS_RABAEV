@@../2026-10-08_stock_posting_core/342_checkpoint_hu_qc_invalidation.sql
@@../2026-10-08_stock_posting_core/014b_recompile.sql
update RRL_SCHEMA_MIGRATIONS set STATUS='ROLLED_BACK' where MIGRATION_ID='2026-10-10-066-hu-control-invalidation';
commit;
/
