whenever sqlerror exit failure rollback
declare n number;
begin
 if user<>'RABAEV' or sys_context('USERENV','SERVICE_NAME')<>'orcl' then raise_application_error(-20999,'WRONG_TARGET');end if;
 select count(*)into n from RRL_YARD_DOCK_STATUS_EVENT;
 if n<>0 then raise_application_error(-20999,'DOCK_STATUS_HISTORY_PRESENT');end if;
end;
/
drop package RRL_YARD_DOCK_STATUS_API;
drop table RRL_YARD_DOCK_STATUS_EVENT purge;
@@rollback_verify.sql
merge into RRL_SCHEMA_MIGRATIONS d using(select '2026-10-27-yard-dock-status' MIGRATION_ID from dual)x on(d.MIGRATION_ID=x.MIGRATION_ID)
when matched then update set STATUS='ROLLED_BACK',APPLIED_AT=sysdate,APPLIED_BY=user
when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS)
values(x.MIGRATION_ID,'Journaled block/reopen command for TRADECASE yard docks',sysdate,user,'apply.sql','rollback.sql','ROLLED_BACK');
commit;
