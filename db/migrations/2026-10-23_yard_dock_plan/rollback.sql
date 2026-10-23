whenever sqlerror exit failure rollback
declare begin if user<>'RABAEV' or sys_context('USERENV','SERVICE_NAME')<>'orcl' then raise_application_error(-20999,'WRONG_TARGET');end if;end;
/
-- Plans are working history: once any plan event exists the rollback refuses instead of deleting it (a separate keep-history plan).
declare n number;begin select count(*)into n from RRL_YARD_DOCK_PLAN_EVENT;if n<>0 then raise_application_error(-20999,'DOCK_PLAN_HISTORY_PRESENT');end if;end;
/
drop package RRL_YARD_DOCK_PLAN_API;
@@before_visit_spec.sql
@@before_visit_body.sql
drop table RRL_YARD_DOCK_PLAN_EVENT purge;
drop table RRL_YARD_DOCK_PLAN purge;
drop sequence RRL_YARD_DOCK_PLAN_SQ;
@@rollback_verify.sql
merge into RRL_SCHEMA_MIGRATIONS d using(select '2026-10-23-yard-dock-plan' MIGRATION_ID from dual)x on(d.MIGRATION_ID=x.MIGRATION_ID)
when matched then update set STATUS='ROLLED_BACK',APPLIED_AT=sysdate,APPLIED_BY=user
when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS)
values(x.MIGRATION_ID,'Planned dock intervals of yard visits, conflict per dock and per vehicle',sysdate,user,'apply.sql','rollback.sql','ROLLED_BACK');
commit;
