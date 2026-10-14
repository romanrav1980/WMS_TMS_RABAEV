@@../2026-10-08_stock_posting_core/346_checkpoint_multi_hu_slot.sql
@@../2026-10-08_stock_posting_core/347_checkpoint_multi_hu_command.sql
@@../2026-10-08_stock_posting_core/014b_recompile.sql
update RRL_SCHEMA_MIGRATIONS set STATUS='ROLLED_BACK' where MIGRATION_ID='2026-10-10-068-multi-hu-slots';
commit;
/
