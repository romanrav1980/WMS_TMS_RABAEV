@@001_schema.sql
@@002_readiness.sql
@@003_command.sql
@@004_posting.sql
@@005_case_pick.sql
@@006_case_policy.sql
@@007_task_policy.sql
@@../2026-10-08_stock_posting_core/014b_recompile.sql
declare n number;begin
 select count(*) into n from USER_OBJECTS where OBJECT_NAME in('RRL_STOCK_WAVE_READY','RRL_STOCK_WAVE_PICK_CMD','RRL_STOCK_POSTING_API','RRL_STOCK_CASE_PICK_CMD','RRL_CASE_RESOURCE_POLICY','RRL_TASK_RESOURCE_POLICY') and OBJECT_TYPE in('PACKAGE','PACKAGE BODY') and STATUS='VALID';
 if n!=12 then raise_application_error(-20808,'WAVE_PICK_RELEASE_INVALID');end if;
end;
/
merge into RRL_SCHEMA_MIGRATIONS d using(select '2026-10-09-038-wave-pick-release' MIGRATION_ID from dual)s on(d.MIGRATION_ID=s.MIGRATION_ID)
when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS)
values(s.MIGRATION_ID,'Explicit root picking release after actual replenishment and owned eligible selected-wave coverage',sysdate,user,'apply.sql','rollback.sql','APPLIED');
commit;
/
