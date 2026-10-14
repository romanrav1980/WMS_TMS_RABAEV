-- Additive departure column/constraint retained for committed shipment history. Never reactivate shipped stock.
@@../2026-10-08_stock_posting_core/343_checkpoint_hu_shipping_core.sql
@@../2026-10-08_stock_posting_core/344_checkpoint_hu_shipping_root.sql
@@../2026-10-10_ni051_case_control/001_case.sql
@@../2026-10-10_ni041_hu_case/004_guard.sql
@@../2026-10-08_stock_posting_core/345_checkpoint_hu_shipping_read.sql
@@008_container_guard_rollback.sql
@@../2026-10-08_stock_posting_core/014b_recompile.sql
update RRL_SCHEMA_MIGRATIONS set STATUS='ROLLED_BACK' where MIGRATION_ID='2026-10-10-067-hu-case-shipping';
commit;
/
