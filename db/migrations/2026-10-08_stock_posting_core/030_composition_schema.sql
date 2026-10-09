-- Extend original receipt-unit provenance with a single CURRENT physical binding.
-- PREPARED only; quantities remain unchanged. B0 normalization fills current fields at cutover.
declare n number;
 procedure col(p_table varchar2,p_name varchar2,p_definition varchar2) is v number;
 begin
  select count(*) into v from user_tab_columns where TABLE_NAME=p_table and COLUMN_NAME=p_name;
  if v=0 then execute immediate 'alter table '||p_table||' add('||p_definition||')'; end if;
 end;
begin
 select count(*) into n from RRL_STOCK_RELEASE where RELEASE_ID=1 and STATE='PREPARED';
 if n!=1 then raise_application_error(-20808,'COMPOSITION_INSTALL_REQUIRES_PREPARED'); end if;
 col('RRL_WMS_RECEIPT_UNIT','PHYSICAL_UNIT_KEY','PHYSICAL_UNIT_KEY varchar2(64)');
 col('RRL_WMS_RECEIPT_UNIT','CURRENT_UID','CURRENT_UID varchar2(200)');
 col('RRL_WMS_RECEIPT_UNIT','CURRENT_CELL','CURRENT_CELL varchar2(60)');
 col('RRL_WMS_RECEIPT_UNIT','BASE_UOM','BASE_UOM varchar2(20)');
 col('RRL_WMS_RECEIPT_UNIT','STOCK_STATUS','STOCK_STATUS varchar2(20)');
 col('RRL_WMS_RECEIPT_UNIT','UNIT_VERSION','UNIT_VERSION number default 0 not null');
 col('RRL_WMS_RECEIPT_UNIT','HARD_RESERVATION_ID','HARD_RESERVATION_ID number');
 col('RRL_WAREHOUSE_TASK','TARGET_UID_PALLET','TARGET_UID_PALLET varchar2(200)');
 col('RRL_WAREHOUSE_TASK_STOCK_MOVE','OPERATION_ID','OPERATION_ID varchar2(100)');
 col('RRL_WAREHOUSE_TASK_STOCK_MOVE','BASE_QTY','BASE_QTY number');
 col('RRL_WAREHOUSE_TASK_STOCK_MOVE','BASE_UOM','BASE_UOM varchar2(20)');
 col('RRL_WAREHOUSE_TASK_STOCK_MOVE','TARGET_UID_PALLET','TARGET_UID_PALLET varchar2(200)');
 select count(*) into n from user_indexes where INDEX_NAME='RRL_RECEIPT_UNIT_PHYSICAL_UK';
 if n=0 then execute immediate 'create unique index RRL_RECEIPT_UNIT_PHYSICAL_UK on RRL_WMS_RECEIPT_UNIT(PHYSICAL_UNIT_KEY)'; end if;
 select count(*) into n from user_indexes where INDEX_NAME='RRL_RECEIPT_UNIT_CURRENT_IX';
 if n=0 then execute immediate 'create index RRL_RECEIPT_UNIT_CURRENT_IX on RRL_WMS_RECEIPT_UNIT(CURRENT_UID,CURRENT_CELL,STOCK_STATUS)'; end if;
 select count(*) into n from user_indexes where INDEX_NAME='RRL_STOCK_RESERVE_SOURCE_IX';
 if n=0 then execute immediate 'create index RRL_STOCK_RESERVE_SOURCE_IX on RRL_STOCK_RESERVATION(UID_PALLET,CELL,STATUS,RESERVATION_KIND)'; end if;
 select count(*) into n from user_indexes where INDEX_NAME='RRL_WH_TASK_SOURCE_STATUS_IX';
 if n=0 then execute immediate 'create index RRL_WH_TASK_SOURCE_STATUS_IX on RRL_WAREHOUSE_TASK(TASK_SOURCE,SOURCE_TASK_ID,STATUS)';end if;
 select count(*) into n from user_tables where TABLE_NAME='RRL_STOCK_B0_UNITS';
 if n=0 then execute immediate 'create table RRL_STOCK_B0_UNITS(
  BASELINE_ID varchar2(100) not null references RRL_STOCK_BASELINE(BASELINE_ID),
  PHYSICAL_UNIT_KEY varchar2(64) not null, CURRENT_UID varchar2(200), CURRENT_CELL varchar2(60),
  BASE_QTY number not null, BASE_UOM varchar2(20), STOCK_STATUS varchar2(20), HARD_RESERVATION_ID number,
  UNIT_VERSION number not null, constraint RRL_STOCK_B0_UNITS_PK primary key(BASELINE_ID,PHYSICAL_UNIT_KEY))'; end if;
end;
/
