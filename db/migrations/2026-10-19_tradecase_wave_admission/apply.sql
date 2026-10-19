whenever sqlerror exit failure rollback
@@001_context.sql
@@002_stock_guard.sql
@@003_launch_hook.sql
@@004_replenishment_hook.sql
alter package RRL_PICKING_API compile body;
declare n number;begin
 select count(*)into n from user_errors where name in('RRL_TRADE_PICK_CONTEXT','RRL_TRADE_STOCK_GUARD','RRL_STOCK_WAVE_LAUNCH_CMD','RRL_STOCK_WAVE_CMD');
 if n<>0 then raise_application_error(-20999,'TRADE_WAVE_COMPILE_ERRORS');end if;
end;
/
merge into RRL_SCHEMA_MIGRATIONS d using(select '2026-10-19-tradecase-wave-admission'MIGRATION_ID from dual)x on(d.MIGRATION_ID=x.MIGRATION_ID)
when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS)
values(x.MIGRATION_ID,'Native wave/replenishment admission rechecks legal order context under existing stock locks',sysdate,user,'apply.sql','rollback.sql','APPLIED');
commit;
