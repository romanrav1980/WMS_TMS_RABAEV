begin execute immediate q'[create table RRL_IW_GROUP_ONWARD(
 OPERATION_ID varchar2(100)primary key,PAYLOAD_HASH raw(32)not null,
 RECEIPT_OPERATION_ID varchar2(100)not null unique references RRL_IW_GROUP_RECEIPT(OPERATION_ID),
 ACTOR nvarchar2(50)not null,RESULT_JSON clob not null check(RESULT_JSON is json),
 CREATED_AT timestamp with time zone default systimestamp not null
)]';exception when others then if sqlcode!=-955 then raise;end if;end;
/
begin execute immediate q'[create table RRL_IW_GROUP_ST_BIND(
 OPERATION_ID varchar2(100)primary key,ONWARD_OPERATION_ID varchar2(100)not null references RRL_IW_GROUP_ONWARD(OPERATION_ID),
 RECEIPT_OPERATION_ID varchar2(100)not null references RRL_IW_GROUP_RECEIPT(OPERATION_ID),
 ST_ID number not null unique references RRL_SBORKA_PALLETS(ID),ST_IDENTIFIER varchar2(50)not null unique,
 SOURCE_ST_ID number not null,SOURCE_LOAD_OPERATION_ID varchar2(100)not null,TARGET_TT_ID number not null,
 WARE_ID number not null,ROOT_UID varchar2(200)not null,STOCK_VERSION number not null,SOURCE_CELL varchar2(60)not null,
 FINAL_ADDRESS varchar2(4000)not null,ORIGINAL_FULFILLMENT_JSON clob not null check(ORIGINAL_FULFILLMENT_JSON is json),
 ACTOR nvarchar2(50)not null,RESULT_JSON clob not null check(RESULT_JSON is json),
 constraint RRL_IW_GROUP_BIND_LOT_UQ unique(RECEIPT_OPERATION_ID,ROOT_UID)
)]';exception when others then if sqlcode!=-955 then raise;end if;end;
/
begin execute immediate q'[create table RRL_IW_GROUP_DISPATCH(
 OPERATION_ID varchar2(100)not null references RRL_STOCK_OPERATION(OPERATION_ID),
 BIND_OPERATION_ID varchar2(100)not null unique references RRL_IW_GROUP_ST_BIND(OPERATION_ID),
 RECEIPT_OPERATION_ID varchar2(100)not null,SOURCE_LOAD_OPERATION_ID varchar2(100)not null,
 ST_ID number not null,ROOT_UID varchar2(200)not null,BASE_QTY number not null check(BASE_QTY>0),
 BASE_UOM varchar2(20)not null,ACTOR nvarchar2(50)not null,
 CREATED_AT timestamp with time zone default systimestamp not null,
 constraint RRL_IW_GROUP_DISPATCH_PK primary key(OPERATION_ID,ST_ID)
)]';exception when others then if sqlcode!=-955 then raise;end if;end;
/
begin execute immediate 'create index RRL_IW_GROUP_DISPATCH_SRC_IX on RRL_IW_GROUP_DISPATCH(SOURCE_LOAD_OPERATION_ID,ROOT_UID)';exception when others then if sqlcode!=-955 then raise;end if;end;
/
