whenever sqlerror exit failure rollback
declare n number;begin
 if user<>'RABAEV' or sys_context('USERENV','SERVICE_NAME')<>'orcl' then raise_application_error(-20999,'WRONG_TARGET');end if;
 select count(*)into n from USER_CONSTRAINTS where CONSTRAINT_NAME='RRL_TRADE_TOPUP_SAP_ORDER_UK' and TABLE_NAME='RRL_TRADE_TOPUP_PROPOSAL' and CONSTRAINT_TYPE='U';
 if n<>1 then raise_application_error(-20999,'TOPUP_ORDER_KEY_BASELINE_MISSING');end if;
end;
/
alter table RRL_TRADE_TOPUP_PROPOSAL drop constraint RRL_TRADE_TOPUP_SAP_ORDER_UK;
create unique index RRL_TRADE_TOPUP_SAP_ORDER_UK on RRL_TRADE_TOPUP_PROPOSAL(
 case when SAP_ORDER_ID is not null then WARE_ID end,case when SAP_ORDER_ID is not null then SAP_ORDER_ID end);
@@verify.sql
merge into RRL_SCHEMA_MIGRATIONS d using(select '2026-10-22-trade-topup-sap-order-key' MIGRATION_ID from dual)s on(d.MIGRATION_ID=s.MIGRATION_ID)
when matched then update set STATUS='APPLIED',APPLIED_AT=sysdate,APPLIED_BY=user
when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS)
values(s.MIGRATION_ID,'Allow multiple proposals before a SAP order while retaining order uniqueness',sysdate,user,'apply.sql','rollback.sql','APPLIED');
commit;