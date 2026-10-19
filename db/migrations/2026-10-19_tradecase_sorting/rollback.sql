whenever sqlerror exit failure rollback
@@before_rrl_stock_posting_api.sql
@@before_rrl_stock_internal_cmd.sql
drop package RRL_TRADE_SORT_GUARD;
update RRL_SCHEMA_MIGRATIONS set STATUS='ROLLED_BACK'where MIGRATION_ID='2026-10-19-tradecase-sorting';
commit;
