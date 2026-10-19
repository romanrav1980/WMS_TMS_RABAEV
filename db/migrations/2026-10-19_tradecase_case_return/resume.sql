whenever sqlerror exit failure rollback
@@002_guard.sql
@@003_trade_access.sql
@@004_case_access.sql
@@005_return.sql
declare n number;begin select count(*)into n from user_errors where NAME in('RRL_TRADE_CASE_RETURN','RRL_TRADE_STOCK_GUARD','RRL_TRADE_CASE_ACCESS','RRL_CASE_TASK_ACCESS','RRL_STOCK_CASE_RETURN_CMD');if n<>0 then raise_application_error(-20999,'TRADE_CASE_RETURN_COMPILE_ERRORS');end if;end;
/
merge into RRL_SCHEMA_MIGRATIONS d using(select '2026-10-19-tradecase-case-return'MIGRATION_ID from dual)x on(d.MIGRATION_ID=x.MIGRATION_ID)when matched then update set d.STATUS='APPLIED',d.APPLIED_AT=sysdate,d.APPLIED_BY=user when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS)values(x.MIGRATION_ID,'Native bound CASE return with durable unit references for current owner authorization',sysdate,user,'apply.sql','rollback.sql','APPLIED');
commit;
