-- No schema/stock changes: restore paired exact-before packages, retain operation history.
@@before_case_access_spec.sql
@@before_case_access_body.sql
@@before_resource_policy_spec.sql
@@before_resource_policy_body.sql
@@before_case_pick_spec.sql
@@before_case_pick_body.sql
begin dbms_utility.compile_schema(schema=>user,compile_all=>false);end;
/
update RRL_SCHEMA_MIGRATIONS set STATUS='ROLLED_BACK'where MIGRATION_ID='2026-10-15-case-scoped-confirmation';
commit;
