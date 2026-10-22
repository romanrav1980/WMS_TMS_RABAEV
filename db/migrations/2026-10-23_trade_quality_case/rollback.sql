whenever sqlerror exit failure rollback
declare n number;begin
 if user<>'RABAEV' or sys_context('USERENV','SERVICE_NAME')<>'orcl' then raise_application_error(-20999,'WRONG_TARGET');end if;
 -- Quality cases are evidence of real decisions and posted documents; they are never dropped silently.
 select count(*)into n from RRL_TRADE_QUALITY_CASE;if n<>0 then raise_application_error(-20999,'QUALITY_HISTORY_PRESENT');end if;
end;
/
-- RRL_QUALITY_HOLD rows created by cases stay (existing entity); with no cases there are none.
drop package RRL_TRADE_QUALITY_CASE_API;
drop table RRL_TRADE_QUALITY_CASE_EVENT purge;
drop table RRL_TRADE_QUALITY_CASE_UNIT purge;
drop table RRL_TRADE_QUALITY_CASE purge;
drop sequence RRL_TRADE_QUALITY_CASE_SQ;
@@rollback_verify.sql
merge into RRL_SCHEMA_MIGRATIONS d using(select '2026-10-23-trade-quality-case' MIGRATION_ID from dual)x on(d.MIGRATION_ID=x.MIGRATION_ID)
when matched then update set STATUS='ROLLED_BACK',APPLIED_AT=sysdate,APPLIED_BY=user
when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS)
values(x.MIGRATION_ID,'TRADECASE quality cases: quarantine decision and approved write-off waiting native posting',sysdate,user,'apply.sql','rollback.sql','ROLLED_BACK');
commit;
