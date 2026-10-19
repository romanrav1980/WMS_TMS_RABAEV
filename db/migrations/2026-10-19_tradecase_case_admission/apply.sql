whenever sqlerror exit failure rollback
@@001_context.sql
@@002_case_pick.sql
@@003_guard.sql
alter package RRL_PICKING_API compile body;
alter package RRL_STOCK_WAVE_LAUNCH_CMD compile body;
alter package RRL_STOCK_WAVE_CMD compile body;
alter package RRL_STOCK_WAVE_READY compile body;
declare n number;begin
 select count(*)into n from user_errors where name in('RRL_TRADE_PICK_CONTEXT','RRL_STOCK_CASE_PICK_CMD','RRL_TRADE_STOCK_GUARD','RRL_PICKING_API','RRL_STOCK_WAVE_LAUNCH_CMD','RRL_STOCK_WAVE_CMD','RRL_STOCK_WAVE_READY');
 if n<>0 then raise_application_error(-20999,'TRADE_CASE_ADMISSION_COMPILE_ERRORS');end if;
end;
/
merge into RRL_SCHEMA_MIGRATIONS d using(select '2026-10-19-tradecase-case-admission'MIGRATION_ID from dual)x on(d.MIGRATION_ID=x.MIGRATION_ID)
when matched then update set d.STATUS='APPLIED',d.APPLIED_AT=sysdate,d.APPLIED_BY=user
when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS)
values(x.MIGRATION_ID,'Apply bound legal owner MRC expiry and buyout admission to native CASE picking and movement',sysdate,user,'apply.sql','rollback.sql','APPLIED');
commit;
