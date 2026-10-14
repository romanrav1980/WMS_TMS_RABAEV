@@001_schema.sql
@@002_policy.sql
@@003_plan.sql
@@004_core.sql
@@../2026-10-08_stock_posting_core/014b_recompile.sql
declare n number;begin
 select count(*) into n from USER_OBJECTS where OBJECT_NAME in('RRL_TASK_RESOURCE_POLICY','RRL_STOCK_TASK_PLAN','RRL_STOCK_TASK_CORE') and OBJECT_TYPE in('PACKAGE','PACKAGE BODY') and STATUS='VALID';
 if n!=6 then raise_application_error(-20808,'SHIFT_INSTANT_POLICY_INVALID');end if;
end;
/
merge into RRL_SCHEMA_MIGRATIONS d using(select '2026-10-09-035-shift-instants' MIGRATION_ID from dual)s on(d.MIGRATION_ID=s.MIGRATION_ID)
when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS)
values(s.MIGRATION_ID,'Capture task start instant and shift clock timezone; compare explicit instants for finishing started step',sysdate,user,'apply.sql','rollback.sql','APPLIED');
commit;
/
