begin execute immediate q'[create table RRL_IW_GROUP_UNLOAD(
 OPERATION_ID varchar2(100)primary key references RRL_STOCK_OPERATION(OPERATION_ID),
 PLAN_OPERATION_ID varchar2(100)not null unique references RRL_IW_GROUP_PLAN(OPERATION_ID),
 ROOT_UID varchar2(200)not null,WARE_ID number not null,ACTOR nvarchar2(50)not null,
 CREATED_AT timestamp with time zone default systimestamp not null
)]';exception when others then if sqlcode!=-955 then raise;end if;end;
/
begin execute immediate q'[create table RRL_IW_GROUP_RECEIPT(
 OPERATION_ID varchar2(100)primary key references RRL_STOCK_OPERATION(OPERATION_ID),
 PLAN_OPERATION_ID varchar2(100)not null unique references RRL_IW_GROUP_PLAN(OPERATION_ID),
 UNLOAD_OPERATION_ID varchar2(100)not null unique references RRL_IW_GROUP_UNLOAD(OPERATION_ID),
 ROOT_UID varchar2(200)not null,WARE_ID number not null,RECEIVE_CELL varchar2(60)not null,
 ACTOR nvarchar2(50)not null,CREATED_AT timestamp with time zone default systimestamp not null
)]';exception when others then if sqlcode!=-955 then raise;end if;end;
/
begin execute immediate q'[create table RRL_IW_GROUP_RECEIPT_LINE(
 OPERATION_ID varchar2(100)not null references RRL_IW_GROUP_RECEIPT(OPERATION_ID),
 ROOT_UID varchar2(200)not null,ST_ID number not null references RRL_SBORKA_PALLETS(ID),
 ARTICLE varchar2(160)not null,BASE_QTY number not null check(BASE_QTY>0),BASE_UOM varchar2(20)not null,
 STOCK_EVENT_ID number not null,
 constraint RRL_IW_GROUP_REC_LINE_PK primary key(OPERATION_ID,ROOT_UID),
 constraint RRL_IW_GROUP_REC_ST_UQ unique(OPERATION_ID,ST_ID)
)]';exception when others then if sqlcode!=-955 then raise;end if;end;
/
