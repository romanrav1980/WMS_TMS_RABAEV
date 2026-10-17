-- MIGRATION_ID: 2026-10-15-picker-actual-time-source
-- Manual explicit shadow time; WORK completeness remains uncertified. No existing owner instrumentation.
@@before.sql
@@schema.sql
@@api_spec.sql
@@auth.sql
@@read.sql
@@write.sql
@@api_body.sql
@@guards.sql
@@verify.sql
insert into RRL_SCHEMA_MIGRATIONS(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS)
 values('2026-10-15-picker-actual-time-source','Explicit aware picker manual time stream and closed actual presence; WORK coverage remains uncertified',sysdate,user,'apply.sql','rollback.sql','APPLIED');
commit;
