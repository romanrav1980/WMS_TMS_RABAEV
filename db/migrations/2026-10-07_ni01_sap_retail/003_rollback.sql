-- Refuse rollback while physical receipt facts or SAP tasks exist.
declare n number;
begin
 if user!='RABAEV' then raise_application_error(-20801,'RABAEV only'); end if;
 select (select count(*) from RRL_SAP_PALLET_RECEIPT)+(select count(*) from RRL_SAP_RECEIPT_OUTBOX)
 +(select count(*) from RRL_WAREHOUSE_TASK where TASK_SOURCE='SAP_RECEIPT' or TASK_TYPE='PUTAWAY') into n from dual;
 if n>0 then raise_application_error(-20802,'Physical facts exist: reconcile before rollback'); end if;
 execute immediate 'drop trigger RRL_SAP_PALLET_WRITE_GUARD';
 execute immediate 'drop package RRL_SAP_RECEIPT_API';
 execute immediate 'drop table RRL_SAP_RECEIPT_OUTBOX';
 execute immediate 'drop table RRL_SAP_PALLET_RECEIPT';
 execute immediate 'alter table RRL_WAREHOUSE_TASK drop constraint RRL_WAREHOUSE_TASK_CHK1';
 execute immediate q'[alter table RRL_WAREHOUSE_TASK add constraint RRL_WAREHOUSE_TASK_CHK1 check
 (TASK_TYPE in ('RAW_TO_PRODUCTION','FG_TO_STORAGE','REPLENISHMENT','PICKING_MOVE','OTHER'))]';
 execute immediate 'alter table RRL_WAREHOUSE_TASK drop constraint RRL_WAREHOUSE_TASK_CHK2';
 execute immediate q'[alter table RRL_WAREHOUSE_TASK add constraint RRL_WAREHOUSE_TASK_CHK2 check
 (TASK_SOURCE in ('MES_RAW_SUPPLY','MES_COMPLETION','PICKING','WAVE','MANUAL'))]';
 update RRL_SCHEMA_MIGRATIONS set STATUS='ROLLED_BACK' where MIGRATION_ID='2026-10-07-003-ni01-physical-receipt';
 commit;
end;
/
