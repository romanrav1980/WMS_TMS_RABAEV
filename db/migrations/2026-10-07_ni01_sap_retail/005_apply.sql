prompt NI01 completion: SSCC, canonical marks, receipt reconciliation and SAP acknowledgements
declare
 n number;
 procedure ensure_table(p_name varchar2,p_ddl varchar2) is n number;
 begin select count(*) into n from user_tables where table_name=p_name;
 if n=0 then execute immediate p_ddl; end if; end;
 procedure add_column(p_table varchar2,p_column varchar2,p_ddl varchar2) is n number;
 begin select count(*) into n from user_tab_columns where table_name=p_table and column_name=p_column;
 if n=0 then execute immediate p_ddl; end if; end;
begin
 if user!='RABAEV' or lower(sys_context('USERENV','SERVICE_NAME'))!='orcl' then raise_application_error(-20801,'Existing RABAEV/orcl only'); end if;
 add_column('RRL_WMS_RECEIPT_CODE','CANONICAL_CODE','alter table RRL_WMS_RECEIPT_CODE add CANONICAL_CODE varchar2(4000)');
 add_column('RRL_SAP_SUPPLY_ORDER','CLOSED_AT','alter table RRL_SAP_SUPPLY_ORDER add CLOSED_AT timestamp');
 add_column('RRL_SAP_SUPPLY_ORDER','RECONCILIATION_JSON','alter table RRL_SAP_SUPPLY_ORDER add RECONCILIATION_JSON clob');
 add_column('RRL_SAP_RECEIPT_OUTBOX','FILE_HASH','alter table RRL_SAP_RECEIPT_OUTBOX add FILE_HASH varchar2(64)');
 add_column('RRL_SAP_RECEIPT_OUTBOX','ACKNOWLEDGED_AT','alter table RRL_SAP_RECEIPT_OUTBOX add ACKNOWLEDGED_AT timestamp');
 add_column('RRL_SAP_RECEIPT_OUTBOX','EXTERNAL_DOCUMENT_ID','alter table RRL_SAP_RECEIPT_OUTBOX add EXTERNAL_DOCUMENT_ID varchar2(100)');
 select count(*) into n from user_constraints where constraint_name='RRL_SAP_REC_OUT_ST_CK';
 if n>0 then execute immediate 'alter table RRL_SAP_RECEIPT_OUTBOX drop constraint RRL_SAP_REC_OUT_ST_CK'; end if;
 execute immediate q'[alter table RRL_SAP_RECEIPT_OUTBOX add constraint RRL_SAP_REC_OUT_ST_CK check(STATUS in('PENDING','EXPORTED','ERROR','ACKNOWLEDGED','REJECTED'))]';
 ensure_table('RRL_RECEIPT_WARE_SETTINGS',q'[
 create table RRL_RECEIPT_WARE_SETTINGS(WARE_ID number not null,COMPANY_PREFIX varchar2(12),EXTENSION_DIGIT number(1) default 0 not null,
 COORDINATE_UNIT_M number default 1 not null,REACHTRUCK_MPS number default 1 not null,LIFT_MPS number default 0.5 not null,
 PLACEMENT_METRIC varchar2(20) default 'DISTANCE' not null,UPDATED_BY varchar2(100),UPDATED_AT timestamp default systimestamp,
 constraint RRL_REC_WSET_PK primary key(WARE_ID),constraint RRL_REC_WSET_SPEED_CK check(COORDINATE_UNIT_M>0 and REACHTRUCK_MPS>0 and LIFT_MPS>0),
 constraint RRL_REC_WSET_METRIC_CK check(PLACEMENT_METRIC in('DISTANCE','TIME')),constraint RRL_REC_WSET_EXT_CK check(EXTENSION_DIGIT between 0 and 9))]');
 ensure_table('RRL_RECEIPT_SKU_RULE',q'[
 create table RRL_RECEIPT_SKU_RULE(WARE_ID number not null,ARTICUL varchar2(40) not null,PICK_CELL varchar2(60) not null,
 TEMP_MIN number,TEMP_MAX number,MIN_SHELF_DAYS number default 0 not null,
 constraint RRL_REC_SKUR_PK primary key(WARE_ID,ARTICUL),constraint RRL_REC_SKUR_TEMP_CK check(TEMP_MIN<=TEMP_MAX),constraint RRL_REC_SKUR_SHELF_CK check(MIN_SHELF_DAYS>=0))]');
 ensure_table('RRL_RECEIPT_CELL_RULE',q'[
 create table RRL_RECEIPT_CELL_RULE(WARE_ID number not null,CELL varchar2(60) not null,TEMP_MIN number,TEMP_MAX number,
 constraint RRL_REC_CELLR_PK primary key(WARE_ID,CELL),constraint RRL_REC_CELLR_TEMP_CK check(TEMP_MIN<=TEMP_MAX))]');
 ensure_table('RRL_RECEIPT_TRAVEL_TIME',q'[
 create table RRL_RECEIPT_TRAVEL_TIME(WARE_ID number not null,CELL varchar2(60) not null,PICK_CELL varchar2(60) not null,
 TRAVEL_SEC number not null,BASIS varchar2(30) not null,UPDATED_BY varchar2(100),UPDATED_AT timestamp default systimestamp,
 constraint RRL_REC_TRAVEL_PK primary key(WARE_ID,CELL,PICK_CELL),constraint RRL_REC_TRAVEL_SEC_CK check(TRAVEL_SEC>=0),
 constraint RRL_REC_TRAVEL_BASIS_CK check(BASIS in('MEASURED','ROUTE_GRAPH','NORMATIVE')))]');
 ensure_table('RRL_RECEIPT_SLOT_CLAIM',q'[
 create table RRL_RECEIPT_SLOT_CLAIM(TASK_ID number not null,UID_PALLET varchar2(200) not null,CELL varchar2(60) not null,
 CELL_SLOT_ID number not null,STATUS varchar2(20) default 'RESERVED' not null,
 constraint RRL_REC_SLOT_PK primary key(TASK_ID),constraint RRL_REC_SLOT_PAL_UK unique(UID_PALLET),constraint RRL_REC_SLOT_SLOT_UK unique(CELL_SLOT_ID),
 constraint RRL_REC_SLOT_ST_CK check(STATUS in('RESERVED','OCCUPIED')))]');
 ensure_table('RRL_RECEIPT_LABEL',q'[
 create table RRL_RECEIPT_LABEL(LABEL_ID varchar2(32) not null,OPERATION_ID varchar2(100) not null,ORDER_ID varchar2(32) not null,LINE_NUMBER varchar2(20) not null,
 SSCC varchar2(18) not null,PAYLOAD_HASH varchar2(64) not null,PAYLOAD_JSON clob not null,STATUS varchar2(20) default 'ISSUED' not null,
 CREATED_AT timestamp default systimestamp not null,CREATED_BY varchar2(100) not null,CONFIRMED_AT timestamp,CONFIRMED_BY varchar2(100),
 constraint RRL_REC_LABEL_PK primary key(LABEL_ID),constraint RRL_REC_LABEL_OP_UK unique(OPERATION_ID),constraint RRL_REC_LABEL_SSCC_UK unique(SSCC),
 constraint RRL_REC_LABEL_JSON_CK check(PAYLOAD_JSON is json),constraint RRL_REC_LABEL_ST_CK check(STATUS in('ISSUED','CONFIRMED','USED')))]');
 ensure_table('RRL_SAP_RECEIPT_ACK',q'[
 create table RRL_SAP_RECEIPT_ACK(SENDER varchar2(100) not null,MESSAGE_ID varchar2(100) not null,EVENT_ID varchar2(100) not null,
 PAYLOAD_HASH varchar2(64) not null,RAW_XML clob not null,RESULT_JSON clob not null,RECEIVED_AT timestamp default systimestamp not null,RECEIVED_BY varchar2(100),
 constraint RRL_SAP_REC_ACK_PK primary key(SENDER,MESSAGE_ID),constraint RRL_SAP_REC_ACK_FK foreign key(EVENT_ID) references RRL_SAP_RECEIPT_OUTBOX(EVENT_ID))]');
 select count(*) into n from user_sequences where sequence_name='RRL_RECEIPT_SSCC_SQ';
 if n=0 then execute immediate 'create sequence RRL_RECEIPT_SSCC_SQ start with 1 increment by 1 nocycle cache 100'; end if;
 select count(*) into n from user_indexes where index_name='RRL_SAP_REC_OUT_QUEUE_IX';
 if n=0 then execute immediate 'create index RRL_SAP_REC_OUT_QUEUE_IX on RRL_SAP_RECEIPT_OUTBOX(STATUS,CREATED_AT)'; end if;
end;
/
merge into RRL_SCHEMA_MIGRATIONS d using(select '2026-10-07-005-ni01-completion' MIGRATION_ID from dual)s on(d.MIGRATION_ID=s.MIGRATION_ID)
when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS)
values(s.MIGRATION_ID,'NI01 labels, canonical mark identities, reconciliation, placement rules and SAP ACK',sysdate,user,'005_apply.sql','005_rollback.sql','APPLIED');
commit;
