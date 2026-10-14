@@../2026-10-08_stock_posting_core/366_checkpoint_fullpal_hu_shipping_core.sql
@@../2026-10-08_stock_posting_core/367_checkpoint_fullpal_hu_command.sql
@@../2026-10-08_stock_posting_core/014b_recompile.sql
update RRL_SCHEMA_MIGRATIONS set STATUS='ROLLED_BACK' where MIGRATION_ID='2026-10-10-075-fullpal-hu-shipping';
commit;
/
