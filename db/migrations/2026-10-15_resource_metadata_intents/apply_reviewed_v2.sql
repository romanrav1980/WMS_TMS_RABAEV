-- Additive reviewed v2 entry: UTF8 no BOM; frozen business bodies unchanged.
-- MIGRATION_ID: 2026-10-15-resource-metadata-intents
-- PREPARED ONLY; root applies sequentially after independent review and quiescing metadata writers.
@@before_current_v2.sql
@@schema.sql
@@spec.sql
@@case_spec.sql
@@task_spec.sql
@@body.sql
@@case_body.sql
@@task_body.sql
@@guards.sql
begin dbms_utility.compile_schema(schema=>user,compile_all=>false);end;
/
@@verify_current_v2.sql
merge into RRL_SCHEMA_MIGRATIONS d using(select '2026-10-15-resource-metadata-intents'MIGRATION_ID from dual)s on(d.MIGRATION_ID=s.MIGRATION_ID)
when matched then update set d.STATUS='APPLIED',d.APPLIED_AT=sysdate,d.APPLIED_BY=user where d.STATUS='ROLLED_BACK'
when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS)
 values(s.MIGRATION_ID,'CASE/TASK never-recorded metadata intent tombstones; no quantity effects',sysdate,user,'apply_reviewed_v2.sql','rollback_reviewed_v2.sql','APPLIED');
commit;
