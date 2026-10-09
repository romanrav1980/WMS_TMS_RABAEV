prompt NI01 physical receipt, putaway and durable SAP events
declare
 procedure ensure_table(p_name varchar2,p_ddl varchar2) is n number;
 begin select count(*) into n from user_tables where table_name=p_name;
 if n=0 then execute immediate p_ddl; end if; end;
begin
 if user!='RABAEV' or lower(sys_context('USERENV','SERVICE_NAME'))!='orcl' then
 raise_application_error(-20801,'Existing RABAEV/orcl only'); end if;
 ensure_table('RRL_SAP_PALLET_RECEIPT',q'[
 create table RRL_SAP_PALLET_RECEIPT(
 OPERATION_ID varchar2(100) not null,ORDER_ID varchar2(32) not null,LINE_NUMBER varchar2(20) not null,
 UID_PALLET varchar2(200) not null,SUPPLIER_BATCH varchar2(100) not null,
 PAYLOAD_HASH varchar2(64) not null,RESULT_JSON clob not null,
 RECEIVED_AT timestamp default systimestamp not null,RECEIVED_BY varchar2(100) not null,
 constraint RRL_SAP_PREC_PK primary key(OPERATION_ID),constraint RRL_SAP_PREC_PAL_UK unique(UID_PALLET),
 constraint RRL_SAP_PREC_LINE_FK foreign key(ORDER_ID,LINE_NUMBER) references RRL_SAP_SUPPLY_LINE(ORDER_ID,LINE_NUMBER),
 constraint RRL_SAP_PREC_JSON_CK check(RESULT_JSON is json))]');
 ensure_table('RRL_SAP_RECEIPT_OUTBOX',q'[
 create table RRL_SAP_RECEIPT_OUTBOX(
 EVENT_ID varchar2(100) not null,EVENT_TYPE varchar2(30) not null,PAYLOAD_JSON clob not null,
 STATUS varchar2(20) default 'PENDING' not null,CREATED_AT timestamp default systimestamp not null,
 EXPORTED_AT timestamp,FILE_NAME varchar2(255),LAST_ERROR varchar2(2000),
 constraint RRL_SAP_REC_OUT_PK primary key(EVENT_ID),constraint RRL_SAP_REC_OUT_JSON check(PAYLOAD_JSON is json),
 constraint RRL_SAP_REC_OUT_ST_CK check(STATUS in('PENDING','EXPORTED','ERROR')))]');
 execute immediate 'alter table RRL_WAREHOUSE_TASK drop constraint RRL_WAREHOUSE_TASK_CHK1';
 execute immediate q'[alter table RRL_WAREHOUSE_TASK add constraint RRL_WAREHOUSE_TASK_CHK1 check
 (TASK_TYPE in ('RAW_TO_PRODUCTION','FG_TO_STORAGE','REPLENISHMENT','PICKING_MOVE','OTHER','PUTAWAY'))]';
 execute immediate 'alter table RRL_WAREHOUSE_TASK drop constraint RRL_WAREHOUSE_TASK_CHK2';
 execute immediate q'[alter table RRL_WAREHOUSE_TASK add constraint RRL_WAREHOUSE_TASK_CHK2 check
 (TASK_SOURCE in ('MES_RAW_SUPPLY','MES_COMPLETION','PICKING','WAVE','MANUAL','SAP_RECEIPT'))]';
end;
/
create or replace package RRL_SAP_RECEIPT_API as
 function pallet_write_allowed return boolean;
 procedure register_pallet(p_sscc varchar2,p_articul varchar2,p_expiry date,p_produced date,
 p_qty number,p_naklad number,p_actor varchar2);
end;
/
create or replace package body RRL_SAP_RECEIPT_API as
 g_allowed boolean:=false;
 function pallet_write_allowed return boolean is begin return g_allowed; end;
 procedure register_pallet(p_sscc varchar2,p_articul varchar2,p_expiry date,p_produced date,
 p_qty number,p_naklad number,p_actor varchar2) is n number;
 begin
 select count(*) into n from RRL_SAP_SUPPLY_ORDER where NAKLAD_ID=p_naklad;
 if n!=1 or p_qty<=0 then raise_application_error(-20803,'Invalid SAP receiving document/quantity'); end if;
 g_allowed:=true;
 begin
 insert into RRL_PALLETS(UID_PALLET,SSCC,ARTICUL,CREATION_DATE,EXPIRY_DATE,PRODUCED_DATE,UNIT_COUNT,PRIHOD_NAKLAD_ID,KLADOVSHIK,PRINTED)
 values(p_sscc,p_sscc,p_articul,sysdate,p_expiry,p_produced,p_qty,p_naklad,substr(p_actor,1,15),0);
 g_allowed:=false;
 exception when others then g_allowed:=false; raise;
 end;
 end;
end;
/
-- Prevent legacy auto-palletization from deleting/replacing SAP fact pallets.
create or replace trigger RRL_SAP_PALLET_WRITE_GUARD
before insert or delete or update of UID_PALLET,UNIT_COUNT,PRIHOD_NAKLAD_ID on RRL_PALLETS
for each row
declare n number;
begin
 select count(*) into n from RRL_SAP_SUPPLY_ORDER
 where NAKLAD_ID=:new.PRIHOD_NAKLAD_ID or NAKLAD_ID=:old.PRIHOD_NAKLAD_ID;
 if n>0 and not RRL_SAP_RECEIPT_API.pallet_write_allowed then
 raise_application_error(-20804,'SAP incoming pallets require the physical receiving API'); end if;
end;
/
merge into RRL_SCHEMA_MIGRATIONS d using(select '2026-10-07-003-ni01-physical-receipt' MIGRATION_ID from dual)s
on(d.MIGRATION_ID=s.MIGRATION_ID)
when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS)
values(s.MIGRATION_ID,'NI01 physical receipt and atomic putaway events',sysdate,user,'003_apply.sql','003_rollback.sql','APPLIED');
commit;
