@@001_shared.sql
@@002_helper.sql
@@003_wave.sql
@@004_core.sql
@@../2026-10-08_stock_posting_core/014b_recompile.sql
declare n number;begin
 select count(*) into n from USER_OBJECTS where OBJECT_NAME in('RRL_STOCK_REPL_SHARED','RRL_STOCK_PLAN_HELPER','RRL_STOCK_WAVE_CMD','RRL_STOCK_TASK_CORE') and OBJECT_TYPE in('PACKAGE','PACKAGE BODY') and STATUS='VALID';
 if n!=8 then raise_application_error(-20808,'SHARED_REPLENISHMENT_INVALID');end if;
end;
/
merge into RRL_SCHEMA_MIGRATIONS d using(select '2026-10-09-045-shared-replenishment' MIGRATION_ID from dual)s on(d.MIGRATION_ID=s.MIGRATION_ID)
when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS)
values(s.MIGRATION_ID,'Shared whole replenishment may preserve other CASE reservations only for same destination; owner rows in ordered closure',sysdate,user,'apply.sql','rollback.sql','APPLIED');
commit;
/
