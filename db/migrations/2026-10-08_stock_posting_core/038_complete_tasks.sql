declare n number;
begin
 select count(*) into n from user_objects where OBJECT_NAME in(
 'RRL_STOCK_PLAN_HELPER','RRL_STOCK_TRANSFER_CORE','RRL_STOCK_TASK_PLAN',
 'RRL_STOCK_TASK_CORE','RRL_STOCK_TASK_DOMAIN','RRL_STOCK_MES_CORE')
 and OBJECT_TYPE in('PACKAGE','PACKAGE BODY') and STATUS='VALID';
 if n!=12 then raise_application_error(-20808,'TASK_POSTING_COMPILATION_FAILED');end if;
 select count(*) into n from RRL_STOCK_RELEASE where RELEASE_ID=1 and STATE='PREPARED';
 if n!=1 then raise_application_error(-20808,'TASK_INSTALL_REQUIRES_PREPARED');end if;
end;
/
merge into RRL_SCHEMA_MIGRATIONS d using(select '2026-10-08-017-stock-task-composition' MIGRATION_ID from dual)s
on(d.MIGRATION_ID=s.MIGRATION_ID)
when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS)
values(s.MIGRATION_ID,'Dormant task posting, physical-unit binding fields and reservation coverage transfer',
sysdate,user,'038_install_tasks.sql','038_task_rollback.sql','APPLIED');
commit;
