begin execute immediate q'[create table RRL_INTERWARE_ONWARD_BIND(
 OPERATION_ID varchar2(100) primary key,PAYLOAD_HASH raw(32) not null,
 RECEIPT_OPERATION_ID varchar2(100) not null unique references RRL_INTERWARE_RECEIPT(OPERATION_ID),
 ST_ID number not null unique references RRL_SBORKA_PALLETS(ID),ST_IDENTIFIER varchar2(50) not null unique,
 SOURCE_ST_ID number not null references RRL_SBORKA_PALLETS(ID),SOURCE_LOAD_OPERATION_ID varchar2(100) not null references RRL_TT_HU_LOAD_FACT(LOAD_OPERATION_ID),
 TARGET_TT_ID number not null references RRL_TRANSPORT_TASK(ID),WARE_ID number not null,
 ROOT_UID varchar2(200) not null,STOCK_VERSION number not null,SOURCE_CELL varchar2(60) not null,
 FINAL_ADDRESS varchar2(255) not null,ORIGINAL_FULFILLMENT_JSON clob not null check(ORIGINAL_FULFILLMENT_JSON is json),
 REASON_TEXT varchar2(2000 byte) not null,DECISION_REFERENCE varchar2(255 byte) not null,
 ACTOR nvarchar2(50) not null,CREATED_AT timestamp with time zone default systimestamp not null,RESULT_JSON clob not null check(RESULT_JSON is json)
)]';exception when others then if sqlcode!=-955 then raise;end if;end;
/
begin execute immediate q'[create table RRL_INTERWARE_ONWARD_DISPATCH(
 OPERATION_ID varchar2(100) primary key references RRL_STOCK_OPERATION(OPERATION_ID),
 BIND_OPERATION_ID varchar2(100) not null unique references RRL_INTERWARE_ONWARD_BIND(OPERATION_ID),
 RECEIPT_OPERATION_ID varchar2(100) not null unique references RRL_INTERWARE_RECEIPT(OPERATION_ID),
 SOURCE_LOAD_OPERATION_ID varchar2(100) not null references RRL_TT_HU_LOAD_FACT(LOAD_OPERATION_ID),
 ST_ID number not null references RRL_SBORKA_PALLETS(ID),ROOT_UID varchar2(200) not null,
 BASE_QTY number not null,BASE_UOM varchar2(20) not null,ACTOR nvarchar2(50) not null,CREATED_AT timestamp with time zone default systimestamp not null
)]';exception when others then if sqlcode!=-955 then raise;end if;end;
/

begin execute immediate q'[alter table RRL_INTERWARE_ONWARD_BIND add(FINAL_ADDRESS_SOURCE varchar2(30) default 'FROZEN_LOAD' not null check(FINAL_ADDRESS_SOURCE in('FROZEN_LOAD','CURRENT_GUARDED_LEGACY')))]';exception when others then if sqlcode!=-1430 then raise;end if;end;
/
