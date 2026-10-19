whenever sqlerror exit failure rollback
@@before_rrl_case_task_access.sql
drop package RRL_TRADE_CASE_ACCESS;
@@before_rrl_stock_case_pick_cmd_package_body.sql
@@before_rrl_trade_stock_guard_package_body.sql
@@before_rrl_trade_pick_context_package.sql
@@before_rrl_trade_pick_context_package_body.sql
alter package RRL_PICKING_API compile body;
alter package RRL_STOCK_WAVE_LAUNCH_CMD compile body;
alter package RRL_STOCK_WAVE_CMD compile body;
alter package RRL_STOCK_WAVE_READY compile body;
alter package RRL_TRADE_STOCK_GUARD compile body;
update RRL_SCHEMA_MIGRATIONS set STATUS='ROLLED_BACK'where MIGRATION_ID='2026-10-19-tradecase-case-admission';
commit;
