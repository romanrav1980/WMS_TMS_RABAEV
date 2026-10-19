whenever sqlerror exit failure rollback
@@before_rrl_sap_pallet_write_guard.sql
@@before_rrl_stock_internal_cmd.sql
update RRL_SCHEMA_MIGRATIONS set STATUS='ROLLED_BACK'where MIGRATION_ID='2026-10-19-tradecase-split-origin';
commit;
