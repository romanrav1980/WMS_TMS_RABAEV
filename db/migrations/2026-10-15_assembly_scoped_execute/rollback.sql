@@after_sources.sql
@@history_guard.sql
@@restore_assembly_body.sql
@@restore_case_pick_body.sql
@@restore_resource_policy_body.sql
@@restore_lifecycle_body.sql
@@restore_case_access_spec.sql
@@restore_case_access_body.sql
drop package RRL_ASM_META_SCOPE;
@@compile_dependents.sql
@@before_sources.sql
declare n number;begin select count(*)into n from USER_OBJECTS where STATUS='INVALID';if n!=0 then raise_application_error(-20886,'ASM_SCOPE_ROLLBACK_INVALID');end if;end;
/
update RRL_SCHEMA_MIGRATIONS set STATUS='ROLLED_BACK'where MIGRATION_ID='2026-10-15-assembly-scoped-execute';
commit;
