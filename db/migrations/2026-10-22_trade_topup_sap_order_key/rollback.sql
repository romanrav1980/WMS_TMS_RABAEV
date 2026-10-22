whenever sqlerror exit failure rollback
declare n number;begin
 if user<>'RABAEV' or sys_context('USERENV','SERVICE_NAME')<>'orcl' then raise_application_error(-20999,'WRONG_TARGET');end if;
 select count(*)into n from(select WARE_ID from RRL_TRADE_TOPUP_PROPOSAL where SAP_ORDER_ID is null group by WARE_ID having count(*)>1);
 if n>0 then raise_application_error(-20999,'TOPUP_PENDING_HISTORY_PREVENTS_LEGACY_KEY');end if;
end;
/
drop index RRL_TRADE_TOPUP_SAP_ORDER_UK;
alter table RRL_TRADE_TOPUP_PROPOSAL add constraint RRL_TRADE_TOPUP_SAP_ORDER_UK unique(WARE_ID,SAP_ORDER_ID);
update RRL_SCHEMA_MIGRATIONS set STATUS='ROLLED_BACK',APPLIED_AT=sysdate,APPLIED_BY=user where MIGRATION_ID='2026-10-22-trade-topup-sap-order-key';
commit;