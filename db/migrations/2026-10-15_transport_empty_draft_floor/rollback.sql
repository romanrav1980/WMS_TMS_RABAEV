-- MIGRATION_ID: 2026-10-15-transport-empty-draft-floor
@@before_rrl_transport_plan_rules.sql
update RRL_SCHEMA_MIGRATIONS set STATUS='ROLLED_BACK'where MIGRATION_ID='2026-10-15-transport-empty-draft-floor';
commit;
