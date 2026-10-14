declare n number;begin
 select count(*) into n from USER_TAB_COLUMNS where TABLE_NAME='RRL_STORE_RETURN_WARE_POLICY' and COLUMN_NAME='SUPPLIER_TARGET_CELL';
 if n=0 then execute immediate 'alter table RRL_STORE_RETURN_WARE_POLICY add(SUPPLIER_TARGET_CELL varchar2(60 byte),DISPOSAL_TARGET_CELL varchar2(60 byte))';end if;
end;
/
begin execute immediate q'[create table RRL_STORE_RETURN_PUT_PLAN(
 OPERATION_ID varchar2(100 byte) primary key references RRL_STOCK_OPERATION(OPERATION_ID),
 RECEIPT_OPERATION_ID varchar2(100 byte) not null references RRL_STORE_RETURN_RECEIPT(OPERATION_ID),
 TASK_ID number not null unique references RRL_WAREHOUSE_TASK(TASK_ID),
 POLICY_VERSION number(19) not null,
 TARGET_CELL varchar2(60 byte) not null,
 PLANNED_BY nvarchar2(50) not null,
 PLANNED_AT timestamp with time zone default systimestamp not null
)]';exception when others then if sqlcode!=-955 then raise;end if;end;
/
begin execute immediate 'create index RRL_STORE_RETURN_PUT_RECEIPT on RRL_STORE_RETURN_PUT_PLAN(RECEIPT_OPERATION_ID,TASK_ID)';exception when others then if sqlcode!=-955 then raise;end if;end;
/
begin execute immediate q'[create table RRL_STORE_RETURN_PLACEMENT(
 OPERATION_ID varchar2(100 byte) primary key references RRL_STOCK_OPERATION(OPERATION_ID),
 RECEIPT_OPERATION_ID varchar2(100 byte) not null unique references RRL_STORE_RETURN_RECEIPT(OPERATION_ID),
 TASK_ID number not null unique references RRL_WAREHOUSE_TASK(TASK_ID),
 UID_PALLET varchar2(200 byte) not null,
 TARGET_CELL varchar2(60 byte) not null,
 BASE_QTY number(27,9) not null check(BASE_QTY>0),
 BASE_UOM varchar2(20 byte) not null,
 PLACED_BY nvarchar2(50) not null,
 PLACED_AT timestamp with time zone default systimestamp not null
)]';exception when others then if sqlcode!=-955 then raise;end if;end;
/
begin execute immediate 'alter table RRL_STORE_RETURN_RECEIPT add constraint RRL_STORE_RETURN_RECEIPT_DOC_UQ unique(NAKLAD_ID)';exception when others then if sqlcode not in(-2264,-2261) then raise;end if;end;
/
