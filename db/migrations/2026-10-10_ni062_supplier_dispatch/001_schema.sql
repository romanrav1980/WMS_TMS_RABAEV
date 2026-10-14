begin execute immediate q'[create table RRL_STORE_RETURN_SUP_BIND(
 OPERATION_ID varchar2(100) primary key,
 PAYLOAD_HASH raw(32) not null,
 RECEIPT_OPERATION_ID varchar2(100) not null unique references RRL_STORE_RETURN_RECEIPT(OPERATION_ID),
 ST_ID number not null unique references RRL_SBORKA_PALLETS(ID),
 ST_IDENTIFIER varchar2(80 byte) not null,
 SUPPLIER_INN varchar2(255 byte) not null,
 DECISION_REFERENCE varchar2(255 byte) not null,REASON_TEXT varchar2(2000 byte) not null,
 ACTOR nvarchar2(50) not null,CREATED_AT timestamp with time zone default systimestamp not null,
 RESULT_JSON clob not null check(RESULT_JSON is json)
)]';exception when others then if sqlcode!=-955 then raise;end if;end;
/
begin execute immediate q'[create table RRL_STORE_RETURN_SUP_DISPATCH(
 OPERATION_ID varchar2(100) primary key references RRL_STOCK_OPERATION(OPERATION_ID),
 BIND_OPERATION_ID varchar2(100) not null unique references RRL_STORE_RETURN_SUP_BIND(OPERATION_ID),
 RECEIPT_OPERATION_ID varchar2(100) not null unique references RRL_STORE_RETURN_RECEIPT(OPERATION_ID),
 ST_ID number not null references RRL_SBORKA_PALLETS(ID),
 UID_PALLET varchar2(200 byte) not null,
 BASE_QTY number(27,9) not null check(BASE_QTY>0),BASE_UOM varchar2(20) not null,
 SUPPLIER_INN varchar2(255 byte) not null,
 ACTOR nvarchar2(50) not null,CREATED_AT timestamp with time zone default systimestamp not null
)]';exception when others then if sqlcode!=-955 then raise;end if;end;
/
