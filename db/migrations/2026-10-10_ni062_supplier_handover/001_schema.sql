begin execute immediate q'[create table RRL_SUP_RETURN_HANDOVER(
 OPERATION_ID varchar2(100) primary key,PAYLOAD_HASH raw(32) not null,
 DISPATCH_OPERATION_ID varchar2(100) not null unique references RRL_STORE_RETURN_SUP_DISPATCH(OPERATION_ID),
 DOCUMENT_REFERENCE varchar2(255 byte) not null,DOCUMENT_SHA256 varchar2(64) not null,
 RECEIVER_NAME varchar2(500 byte) not null,ACTOR nvarchar2(50) not null,
 CREATED_AT timestamp with time zone default systimestamp not null,
 RESULT_JSON clob not null check(RESULT_JSON is json),
 check(regexp_like(DOCUMENT_SHA256,'^[0-9a-f]{64}$'))
)]';exception when others then if sqlcode!=-955 then raise;end if;end;
/
begin execute immediate q'[create table RRL_SUP_RETURN_CONFIRM(
 OPERATION_ID varchar2(100) primary key,PAYLOAD_HASH raw(32) not null,
 HANDOVER_OPERATION_ID varchar2(100) not null unique references RRL_SUP_RETURN_HANDOVER(OPERATION_ID),
 DECISION_REFERENCE varchar2(255 byte) not null,REASON_TEXT varchar2(2000 byte) not null,
 ACTOR nvarchar2(50) not null,CREATED_AT timestamp with time zone default systimestamp not null,
 RESULT_JSON clob not null check(RESULT_JSON is json)
)]';exception when others then if sqlcode!=-955 then raise;end if;end;
/
