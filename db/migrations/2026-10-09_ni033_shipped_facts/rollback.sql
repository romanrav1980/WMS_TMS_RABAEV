@@../2026-10-08_stock_posting_core/270_shipped_facts_shipping_rollback.sql
@@../2026-10-08_stock_posting_core/014b_recompile.sql
update RRL_SCHEMA_MIGRATIONS set STATUS='ROLLED_BACK' where MIGRATION_ID='2026-10-09-032-shipped-facts';
commit;
/
