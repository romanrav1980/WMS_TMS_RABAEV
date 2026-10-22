whenever sqlerror exit failure rollback
declare n number;begin
 if user<>'RABAEV' or sys_context('USERENV','SERVICE_NAME')<>'orcl' then raise_application_error(-20999,'WRONG_TARGET');end if;
 -- Visit history is evidence of real yard events; it is never dropped silently.
 select count(*)into n from RRL_YARD_VISIT;if n<>0 then raise_application_error(-20999,'YARD_HISTORY_PRESENT');end if;
end;
/
drop package RRL_YARD_VISIT_API;
drop table RRL_YARD_VISIT_EVENT purge;
drop table RRL_YARD_VISIT purge;
drop sequence RRL_YARD_VISIT_SQ;
@@rollback_verify.sql
merge into RRL_SCHEMA_MIGRATIONS d using(select '2026-10-22-yard-visit' MIGRATION_ID from dual)x on(d.MIGRATION_ID=x.MIGRATION_ID)
when matched then update set STATUS='ROLLED_BACK',APPLIED_AT=sysdate,APPLIED_BY=user
when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS)
values(x.MIGRATION_ID,'TRADECASE yard visits: versioned dock/vehicle occupancy without stock effects',sysdate,user,'apply.sql','rollback.sql','ROLLED_BACK');
commit;
