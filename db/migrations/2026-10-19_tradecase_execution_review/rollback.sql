whenever sqlerror exit failure rollback
@@before_rrl_trade_stock_api.sql
@@before_rrl_trade_buyout_core.sql
@@before_rrl_stock_posting_api.sql
@@before_rrl_trade_sort_guard.sql
update RRL_SCHEMA_MIGRATIONS set STATUS='ROLLED_BACK'where MIGRATION_ID='2026-10-19-tradecase-execution-review';
commit;
