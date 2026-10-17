@@before_rrl_wave_exec_access.sql
@@before_rrl_stock_posting_api.sql
@@before_rrl_stock_wave_launch_cmd.sql
update RRL_SCHEMA_MIGRATIONS set STATUS='ROLLED_BACK'where MIGRATION_ID='2026-10-15-wave-launch-scope';
commit;
