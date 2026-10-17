-- MIGRATION_ID: 2026-10-15-case-scoped-confirmation
-- PREPARED: independent coordinator review/apply required. No seed/business writes.
@@case_access_spec.sql
@@case_access_body.sql
@@resource_policy_body.sql
@@case_pick_body.sql
@@compile_verify.sql
insert into RRL_SCHEMA_MIGRATIONS(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS)
values('2026-10-15-case-scoped-confirmation','Assigned ordinary count CASE scoped native confirmation; existing physical and legacy guards retained',sysdate,user,'apply.sql','rollback.sql','APPLIED');
commit;
