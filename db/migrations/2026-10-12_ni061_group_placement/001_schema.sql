begin execute immediate q'[create table RRL_IW_GROUP_PUT_PLAN(
 OPERATION_ID varchar2(100)primary key references RRL_STOCK_OPERATION(OPERATION_ID),
 RECEIPT_OPERATION_ID varchar2(100)not null unique references RRL_IW_GROUP_RECEIPT(OPERATION_ID),
 TASK_ID number not null unique references RRL_WAREHOUSE_TASK(TASK_ID),
 ROOT_UID varchar2(200)not null,WARE_ID number not null,FROM_CELL varchar2(60)not null,TARGET_CELL varchar2(60)not null,
 ACTOR nvarchar2(50)not null,CREATED_AT timestamp with time zone default systimestamp not null
)]';exception when others then if sqlcode!=-955 then raise;end if;end;
/
begin execute immediate q'[create table RRL_IW_GROUP_PLACEMENT(
 OPERATION_ID varchar2(100)primary key references RRL_STOCK_OPERATION(OPERATION_ID),
 RECEIPT_OPERATION_ID varchar2(100)not null unique references RRL_IW_GROUP_RECEIPT(OPERATION_ID),
 TASK_ID number not null unique references RRL_WAREHOUSE_TASK(TASK_ID),
 ROOT_UID varchar2(200)not null,WARE_ID number not null,TARGET_CELL varchar2(60)not null,
 ACTOR nvarchar2(50)not null,CREATED_AT timestamp with time zone default systimestamp not null
)]';exception when others then if sqlcode!=-955 then raise;end if;end;
/
