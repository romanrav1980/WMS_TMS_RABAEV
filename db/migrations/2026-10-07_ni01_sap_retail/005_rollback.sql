-- Explicit rollback is permitted only before any completion-layer facts/configuration exist.
declare n number;
begin
 if user!='RABAEV' or lower(sys_context('USERENV','SERVICE_NAME'))!='orcl' then raise_application_error(-20801,'Existing RABAEV/orcl only'); end if;
 select (select count(*) from RRL_RECEIPT_LABEL)+(select count(*) from RRL_SAP_RECEIPT_ACK)
 +(select count(*) from RRL_RECEIPT_SLOT_CLAIM)+(select count(*) from RRL_RECEIPT_WARE_SETTINGS)
 +(select count(*) from RRL_RECEIPT_SKU_RULE)+(select count(*) from RRL_RECEIPT_CELL_RULE)
 +(select count(*) from RRL_RECEIPT_TRAVEL_TIME)+(select count(*) from RRL_WMS_RECEIPT_CODE where CANONICAL_CODE is not null)
 +(select count(*) from RRL_SAP_SUPPLY_ORDER where CLOSED_AT is not null)
 +(select count(*) from RRL_SAP_RECEIPT_OUTBOX where FILE_HASH is not null or STATUS in('ACKNOWLEDGED','REJECTED')) into n from dual;
 if n>0 then raise_application_error(-20802,'Export/reconcile NI01 facts and configuration before rollback'); end if;
 execute immediate 'drop table RRL_SAP_RECEIPT_ACK';
 execute immediate 'drop table RRL_RECEIPT_SLOT_CLAIM';
 execute immediate 'drop table RRL_RECEIPT_LABEL';
 execute immediate 'drop table RRL_RECEIPT_TRAVEL_TIME';
 execute immediate 'drop table RRL_RECEIPT_CELL_RULE';
 execute immediate 'drop table RRL_RECEIPT_SKU_RULE';
 execute immediate 'drop table RRL_RECEIPT_WARE_SETTINGS';
 execute immediate 'drop sequence RRL_RECEIPT_SSCC_SQ';
 execute immediate 'drop index RRL_SAP_REC_OUT_QUEUE_IX';
 execute immediate 'alter table RRL_WMS_RECEIPT_CODE drop column CANONICAL_CODE';
 execute immediate 'alter table RRL_SAP_SUPPLY_ORDER drop column CLOSED_AT';
 execute immediate 'alter table RRL_SAP_SUPPLY_ORDER drop column RECONCILIATION_JSON';
 execute immediate 'alter table RRL_SAP_RECEIPT_OUTBOX drop column FILE_HASH';
 execute immediate 'alter table RRL_SAP_RECEIPT_OUTBOX drop column ACKNOWLEDGED_AT';
 execute immediate 'alter table RRL_SAP_RECEIPT_OUTBOX drop column EXTERNAL_DOCUMENT_ID';
 execute immediate 'alter table RRL_SAP_RECEIPT_OUTBOX drop constraint RRL_SAP_REC_OUT_ST_CK';
 execute immediate q'[alter table RRL_SAP_RECEIPT_OUTBOX add constraint RRL_SAP_REC_OUT_ST_CK check(STATUS in('PENDING','EXPORTED','ERROR'))]';
 update RRL_SCHEMA_MIGRATIONS set STATUS='ROLLED_BACK' where MIGRATION_ID='2026-10-07-005-ni01-completion';
 commit;
end;
/
