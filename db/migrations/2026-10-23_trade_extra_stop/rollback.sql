whenever sqlerror exit failure rollback
declare n number;begin
 if user<>'RABAEV' or sys_context('USERENV','SERVICE_NAME')<>'orcl' then raise_application_error(-20999,'WRONG_TARGET');end if;
 -- Dispatcher decisions are evidence; the journal is never dropped with content.
 select count(*)into n from RRL_TRADE_EXTRA_STOP_EVENT;if n<>0 then raise_application_error(-20999,'EXTRA_STOP_HISTORY_PRESENT');end if;
end;
/
drop package RRL_TRADE_EXTRA_STOP_API;
drop table RRL_TRADE_EXTRA_STOP_EVENT purge;
drop table RRL_TRADE_ROUTE_STOP_POLICY purge;
@@rollback_verify.sql
merge into RRL_SCHEMA_MIGRATIONS d using(select '2026-10-23-trade-extra-stop' MIGRATION_ID from dual)x on(d.MIGRATION_ID=x.MIGRATION_ID)
when matched then update set STATUS='ROLLED_BACK',APPLIED_AT=sysdate,APPLIED_BY=user
when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS)
values(x.MIGRATION_ID,'TRADECASE extra-stop decision on the native route recalculation and per-trip new-point ban',sysdate,user,'apply.sql','rollback.sql','ROLLED_BACK');
commit;
