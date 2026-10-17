-- MIGRATION_ID: 2026-10-15-wave-scoped-views
@@before_rrl_wave_exec_access.sql
@@before_rrl_wave_time_api.sql
update RRL_SCHEMA_MIGRATIONS set STATUS='ROLLED_BACK' where MIGRATION_ID='2026-10-15-wave-scoped-views';
commit;
