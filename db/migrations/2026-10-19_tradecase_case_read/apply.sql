whenever sqlerror exit failure rollback
@@001_access.sql
alter package RRL_CASE_TASK_ACCESS compile body;
declare n number;begin
 select count(*)into n from user_errors where NAME in('RRL_TRADE_CASE_ACCESS','RRL_CASE_TASK_ACCESS');
 if n<>0 then raise_application_error(-20999,'TRADE_CASE_READ_COMPILE_ERRORS');end if;
end;
/
merge into RRL_SCHEMA_MIGRATIONS d using(select '2026-10-19-tradecase-case-read'MIGRATION_ID from dual)x on(d.MIGRATION_ID=x.MIGRATION_ID)
when matched then update set d.STATUS='APPLIED',d.APPLIED_AT=sysdate,d.APPLIED_BY=user
when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS)
values(x.MIGRATION_ID,'Filter CASE rows and totals by current legal-owner read grants',sysdate,user,'apply.sql','rollback.sql','APPLIED');
commit;
