@@../2026-10-08_stock_posting_core/339_checkpoint_case_control_command.sql
@@../2026-10-08_stock_posting_core/340_checkpoint_case_control_read.sql
@@../2026-10-08_stock_posting_core/341_checkpoint_case_control_hu_read.sql
@@../2026-10-08_stock_posting_core/014b_recompile.sql
update RRL_SCHEMA_MIGRATIONS set STATUS='ROLLED_BACK' where MIGRATION_ID='2026-10-10-065-case-control-projection';
commit;
/