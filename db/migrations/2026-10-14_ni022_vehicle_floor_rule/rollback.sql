@@000_rrl_vehicle_profile_api_spec.sql
@@000_rrl_vehicle_profile_api_body.sql
@@000_rrl_transport_plan_rules_body.sql
update RRL_SCHEMA_MIGRATIONS set STATUS='ROLLED_BACK' where MIGRATION_ID='2026-10-14-1185-vehicle-floor-rule';
/
alter package RRL_TRANSPORT_PLAN_API compile body;
/
alter package RRL_STOCK_LOAD_THERMAL compile body;
/
