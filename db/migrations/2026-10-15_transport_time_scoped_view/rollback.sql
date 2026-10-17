-- MIGRATION_ID: 2026-10-15-transport-time-scoped-view
@@before_rrl_tt_time_api.sql
update RRL_SCHEMA_MIGRATIONS set STATUS='ROLLED_BACK' where MIGRATION_ID='2026-10-15-transport-time-scoped-view';
commit;
