whenever sqlerror exit failure rollback
@@before_rrl_trade_order_api.sql
@@before_rrl_trade_pick_context.sql
@@before_rrl_trade_stock_guard.sql
@@before_rrl_trade_transport_core.sql
@@before_rrl_trade_buyout_core.sql
@@before_rrl_trade_stock_api.sql
drop package RRL_TRADE_TRANSIT_PROOF;
update RRL_SCHEMA_MIGRATIONS set STATUS='ROLLED_BACK'where MIGRATION_ID='2026-10-19-tradecase-transport-review';
commit;
