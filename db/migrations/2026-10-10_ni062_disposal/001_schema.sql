begin execute immediate q'[create table RRL_RETURN_DISPOSAL_REQUEST(
 OPERATION_ID varchar2(100) primary key,PAYLOAD_HASH raw(32) not null,
 RECEIPT_OPERATION_ID varchar2(100) not null unique references RRL_STORE_RETURN_RECEIPT(OPERATION_ID),
 DOCUMENT_REFERENCE varchar2(255 byte) not null,DOCUMENT_SHA256 varchar2(64) not null,
 REASON_TEXT varchar2(2000 byte) not null,ACTOR nvarchar2(50) not null,
 CREATED_AT timestamp with time zone default systimestamp not null,
 RESULT_JSON clob not null check(RESULT_JSON is json),
 check(regexp_like(DOCUMENT_SHA256,'^[0-9a-f]{64}$'))
)]';exception when others then if sqlcode!=-955 then raise;end if;end;
/
begin execute immediate q'[create table RRL_RETURN_DISPOSAL_FACT(
 OPERATION_ID varchar2(100) primary key references RRL_STOCK_OPERATION(OPERATION_ID),
 REQUEST_OPERATION_ID varchar2(100) not null unique references RRL_RETURN_DISPOSAL_REQUEST(OPERATION_ID),
 RECEIPT_OPERATION_ID varchar2(100) not null unique references RRL_STORE_RETURN_RECEIPT(OPERATION_ID),
 UID_PALLET varchar2(200) not null,BASE_QTY number(27,9) not null check(BASE_QTY>0),
 BASE_UOM varchar2(20) not null,LOSS_STORE_ADDR varchar2(255) not null,
 DECISION_REFERENCE varchar2(255 byte) not null,ACTOR nvarchar2(50) not null,
 CREATED_AT timestamp with time zone default systimestamp not null
)]';exception when others then if sqlcode!=-955 then raise;end if;end;
/
