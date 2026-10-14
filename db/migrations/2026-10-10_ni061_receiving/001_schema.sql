begin execute immediate q'[create table RRL_INTERWARE_UNLOAD(
 OPERATION_ID varchar2(100) primary key references RRL_STOCK_OPERATION(OPERATION_ID),
 PLAN_OPERATION_ID varchar2(100) not null unique references RRL_INTERWARE_PLAN(OPERATION_ID),
 ROOT_UID varchar2(200) not null,WARE_ID number not null,VEHICLE_NUMBER varchar2(60) not null,
 INBOUND_DOCK varchar2(60) not null,ACTOR nvarchar2(50) not null,CREATED_AT timestamp with time zone default systimestamp not null
)]';exception when others then if sqlcode!=-955 then raise;end if;end;
/
begin execute immediate q'[create table RRL_INTERWARE_RECEIPT(
 OPERATION_ID varchar2(100) primary key references RRL_STOCK_OPERATION(OPERATION_ID),
 PLAN_OPERATION_ID varchar2(100) not null unique references RRL_INTERWARE_PLAN(OPERATION_ID),
 UNLOAD_OPERATION_ID varchar2(100) not null unique references RRL_INTERWARE_UNLOAD(OPERATION_ID),
 ROOT_UID varchar2(200) not null,WARE_ID number not null,RECEIVE_CELL varchar2(60) not null,
 ARTICLE varchar2(160) not null,BASE_QTY number not null check(BASE_QTY>0),BASE_UOM varchar2(20) not null,
 SOURCE_LOAD_OPERATION_ID varchar2(100) not null unique references RRL_TT_HU_LOAD_FACT(LOAD_OPERATION_ID),
 STOCK_EVENT_ID number not null,ACTOR nvarchar2(50) not null,
 CREATED_AT timestamp with time zone default systimestamp not null
)]';exception when others then if sqlcode!=-955 then raise;end if;end;
/
