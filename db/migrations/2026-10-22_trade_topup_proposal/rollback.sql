whenever sqlerror exit failure rollback
declare n number;begin
 if user<>'RABAEV' or sys_context('USERENV','SERVICE_NAME')<>'orcl' then raise_application_error(-20999,'WRONG_TARGET');end if;
 -- Physical holds and decision history are business evidence: release/archive them first, never drop silently.
 select count(*)into n from RRL_TRADE_TOPUP_PROPOSAL;if n<>0 then raise_application_error(-20999,'TOPUP_DATA_PRESENT_RELEASE_AND_ARCHIVE_FIRST');end if;
end;
/
@@before_rrl_trade_pick_context.sql
@@before_rrl_trade_stock_guard.sql
@@before_rrl_stock_posting_api.sql
drop package RRL_TRADE_TOPUP_CMD;
drop package RRL_TRADE_TOPUP_API;
drop package RRL_TRADE_TOPUP_READ;
@@before_rrl_stock_reserve_core_spec.sql
@@before_rrl_stock_unit_core_spec.sql
drop table RRL_TRADE_TOPUP_EVENT purge;
drop table RRL_TRADE_TOPUP_HOLD purge;
drop table RRL_TRADE_TOPUP_DECISION purge;
drop table RRL_TRADE_TOPUP_PROPOSAL purge;
drop sequence RRL_TRADE_TOPUP_PROPOSAL_SQ;
begin dbms_utility.compile_schema(user,false);end;
/
@@rollback_verify.sql
merge into RRL_SCHEMA_MIGRATIONS d using(select '2026-10-22-trade-topup-proposal' MIGRATION_ID from dual)x on(d.MIGRATION_ID=x.MIGRATION_ID)
when matched then update set STATUS='ROLLED_BACK',APPLIED_AT=sysdate,APPLIED_BY=user
when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS)
values(x.MIGRATION_ID,'Durable top-up proposals, atomic hold+SAP request confirmation, own release, wave adoption gate',sysdate,user,'apply.sql','rollback.sql','ROLLED_BACK');
commit;
