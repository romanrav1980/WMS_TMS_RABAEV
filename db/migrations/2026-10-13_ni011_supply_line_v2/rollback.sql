declare n number;begin
 select count(*)into n from(select ROW_ID from RRL_SAP_SUPPLY_LINE group by ROW_ID having count(*)>1);
 if n>0 then raise_application_error(-20801,'V2 shared rows exist; reconcile source mapping before rollback, no automatic deletion');end if;
 select count(*)into n from(select ORDER_ID,ARTICUL from RRL_SAP_SUPPLY_LINE group by ORDER_ID,ARTICUL having count(*)>1);
 if n>0 then raise_application_error(-20801,'V2 item lines exist; no destructive rollback');end if;
 execute immediate 'drop index RRL_SAP_SUP_ROW_IX';
 execute immediate 'drop index RRL_SAP_SUP_ART_IX';
 execute immediate 'alter table RRL_SAP_SUPPLY_LINE add constraint RRL_SAP_SUP_ROW_UK unique(ROW_ID)';
 execute immediate 'alter table RRL_SAP_SUPPLY_LINE add constraint RRL_SAP_SUP_ART_UK unique(ORDER_ID,ARTICUL)';
 execute immediate 'alter table RRL_SAP_SUPPLY_ORDER drop column GATEWAY_CONTRACT_VERSION';
end;
/
@@003_compile.sql
update RRL_SCHEMA_MIGRATIONS set STATUS='ROLLED_BACK'where MIGRATION_ID='2026-10-13-905-ni011-supply-line-v2';
/
