whenever sqlerror exit failure rollback
@@001_guard.sql
declare n number;begin select count(*)into n from user_errors where NAME='RRL_TRADE_STOCK_GUARD';if n<>0 then raise_application_error(-20999,'TRADE_CANCEL_COMPILE_ERRORS');end if;end;
/
merge into RRL_SCHEMA_MIGRATIONS d using(select '2026-10-19-tradecase-wave-cancel'MIGRATION_ID from dual)x on(d.MIGRATION_ID=x.MIGRATION_ID)when matched then update set d.STATUS='APPLIED',d.APPLIED_AT=sysdate,d.APPLIED_BY=user when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS)values(x.MIGRATION_ID,'Admit native wave reservation cancellation without goods movement',sysdate,user,'apply.sql','rollback.sql','APPLIED');
commit;
