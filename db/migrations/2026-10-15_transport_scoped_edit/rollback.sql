-- MIGRATION_ID: 2026-10-15-transport-scoped-edit
-- Restore captured package bodies; no business row restoration.
@@before_rrl_transport_plan_rules.sql
@@before_rrl_transport_edit_api.sql
update RRL_SCHEMA_MIGRATIONS set STATUS='ROLLED_BACK' where MIGRATION_ID='2026-10-15-transport-scoped-edit';
commit;
