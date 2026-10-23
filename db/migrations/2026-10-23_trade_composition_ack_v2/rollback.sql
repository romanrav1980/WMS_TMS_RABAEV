whenever sqlerror exit failure rollback
declare begin if user<>'RABAEV' or sys_context('USERENV','SERVICE_NAME')<>'orcl' then raise_application_error(-20999,'WRONG_TARGET');end if;end;
/
-- Reported compositions and acknowledgments are working history: once any exists the rollback refuses instead of deleting it.
declare n number;begin select count(*)into n from RRL_TRADE_ORDER_COMPOSITION;if n<>0 then raise_application_error(-20999,'COMPOSITION_HISTORY_PRESENT');end if;end;
/
drop package RRL_TRADE_COMPOSITION_API;
drop table RRL_TRADE_COMPOSITION_ACK purge;
drop table RRL_TRADE_ORDER_COMPOSITION purge;
@@rollback_verify.sql
merge into RRL_SCHEMA_MIGRATIONS d using(select '2026-10-23-trade-composition-ack-v2' MIGRATION_ID from dual)x on(d.MIGRATION_ID=x.MIGRATION_ID)
when matched then update set STATUS='ROLLED_BACK',APPLIED_AT=sysdate,APPLIED_BY=user
when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS)
values(x.MIGRATION_ID,'Assembled order composition reported once with separate SAP and SKM acknowledgments',sysdate,user,'apply.sql','rollback.sql','ROLLED_BACK');
commit;
