@@../2026-10-08_stock_posting_core/269_physical_fulfillment_return_rollback.sql
@@../2026-10-08_stock_posting_core/014b_recompile.sql
-- Additive physical evidence retained; deploy matching prior application before rollback.
update RRL_SCHEMA_MIGRATIONS set STATUS='ROLLED_BACK' where MIGRATION_ID='2026-10-09-031-physical-fulfillment';
commit;
/
