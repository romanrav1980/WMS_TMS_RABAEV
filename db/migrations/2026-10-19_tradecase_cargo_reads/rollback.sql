whenever sqlerror exit failure rollback
@@before_rrl_trade_transport_core.sql
@@before_rrl_trade_stock_api.sql
update RRL_SCHEMA_MIGRATIONS set STATUS='ROLLED_BACK'where MIGRATION_ID='2026-10-19-tradecase-cargo-reads';
commit;
