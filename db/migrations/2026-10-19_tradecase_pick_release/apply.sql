whenever sqlerror exit failure rollback
@@001_context.sql
@@002_readiness.sql
@@003_release_cmd.sql
@@004_stock_guard.sql
alter package RRL_PICKING_API compile body;
alter package RRL_STOCK_WAVE_LAUNCH_CMD compile body;
alter package RRL_STOCK_WAVE_CMD compile body;
declare n number;begin
 select count(*)into n from user_errors where name in('RRL_TRADE_PICK_CONTEXT','RRL_TRADE_STOCK_GUARD','RRL_STOCK_WAVE_READY','RRL_STOCK_WAVE_PICK_CMD','RRL_PICKING_API','RRL_STOCK_WAVE_LAUNCH_CMD','RRL_STOCK_WAVE_CMD');
 if n<>0 then raise_application_error(-20999,'TRADE_PICK_RELEASE_COMPILE_ERRORS');end if;
end;
/
merge into RRL_SCHEMA_MIGRATIONS d using(select '2026-10-19-tradecase-pick-release'MIGRATION_ID from dual)x on(d.MIGRATION_ID=x.MIGRATION_ID)
when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS)
values(x.MIGRATION_ID,'Actor-aware legal wave readiness and native picking release',sysdate,user,'apply.sql','rollback.sql','APPLIED');
commit;
