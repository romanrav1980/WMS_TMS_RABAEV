whenever sqlerror exit failure rollback
@@before_rrl_stock_posting_api.sql
@@before_rrl_trade_stock_guard.sql
@@before_rrl_outgoing_qc_access.sql
update RRL_SCHEMA_MIGRATIONS set STATUS='ROLLED_BACK'where MIGRATION_ID='2026-10-19-tradecase-quality-admission';
commit;
