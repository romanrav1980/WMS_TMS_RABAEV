@@../2026-10-08_stock_posting_core/254_pool_command_rollback.sql
@@../2026-10-08_stock_posting_core/253_wave_launch_pool_rollback.sql
@@../2026-10-08_stock_posting_core/014b_recompile.sql
update RRL_SCHEMA_MIGRATIONS set STATUS='ROLLED_BACK' where MIGRATION_ID='2026-10-09-020-pool-wave-bridge';
commit;
/
