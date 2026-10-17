-- MIGRATION_ID: 2026-10-15-case-assignment-context
@@before.sql
create context RRL_CASE_ASSIGNMENT_CTX using RRL_CASE_ASSIGNMENT_API;
/
@@verify.sql
insert into RRL_SCHEMA_MIGRATIONS(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS)values('2026-10-15-case-assignment-context','Install missing trusted CASE metadata context; no business writes',sysdate,user,'apply.sql','rollback.sql','APPLIED');
commit;
