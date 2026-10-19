whenever sqlerror exit failure rollback
@@before_rrl_stock_wave_cmd.sql
@@before_rrl_stock_wave_launch_cmd.sql
@@before_rrl_trade_stock_guard.sql
@@before_rrl_trade_pick_context_spec.sql
@@before_rrl_trade_pick_context.sql
alter package RRL_PICKING_API compile body;
delete from RRL_SCHEMA_MIGRATIONS where MIGRATION_ID='2026-10-19-tradecase-wave-admission';
commit;
