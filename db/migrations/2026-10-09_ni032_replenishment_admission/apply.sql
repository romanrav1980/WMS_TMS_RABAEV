@@001_schema.sql
@@002_policy.sql
@@003_wave.sql
@@004_task_core.sql
@@../2026-10-08_stock_posting_core/014b_recompile.sql
declare n number;begin
 select count(*) into n from USER_OBJECTS where OBJECT_NAME in('RRL_STOCK_REPL_ADMISSION','RRL_STOCK_WAVE_CMD','RRL_STOCK_TASK_CORE') and OBJECT_TYPE in('PACKAGE','PACKAGE BODY') and STATUS='VALID';
 if n!=6 then raise_application_error(-20808,'REPLENISHMENT_ADMISSION_INVALID');end if;
end;
/
merge into RRL_SCHEMA_MIGRATIONS d using(select '2026-10-09-029-replenishment-admission' MIGRATION_ID from dual)s on(d.MIGRATION_ID=s.MIGRATION_ID)
when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS)
values(s.MIGRATION_ID,'Existing ABC category B, pick batch-mix policy and whole pallet admission',''||sysdate,user,'apply.sql','rollback.sql','APPLIED');
commit;
/
