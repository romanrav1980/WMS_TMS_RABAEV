declare n number;begin
 select count(*)into n from USER_TABLES where TABLE_NAME='RRL_IW_RECOVERY_ST_BIND';
 if n=0 then execute immediate 'create table RRL_IW_RECOVERY_ST_BIND(
 OPERATION_ID varchar2(100)primary key,PAYLOAD_HASH raw(32)not null,
 RECOVERY_OPERATION_ID varchar2(100)not null unique references RRL_INTERWARE_RECOVERY_RECEIPT(OPERATION_ID),
 RECEIPT_OPERATION_ID varchar2(100)not null references RRL_INTERWARE_RECEIPT(OPERATION_ID),
 ST_ID number not null unique,ST_IDENTIFIER varchar2(50)not null unique,SOURCE_ST_ID number not null,SOURCE_LOAD_OPERATION_ID varchar2(100)not null,
 TARGET_TT_ID number not null,WARE_ID number not null,ROOT_UID varchar2(200)not null,STOCK_VERSION number not null,SOURCE_CELL varchar2(60)not null,
 FINAL_ADDRESS varchar2(255)not null,ORIGINAL_FULFILLMENT_JSON clob not null check(ORIGINAL_FULFILLMENT_JSON is json),
 REASON_TEXT varchar2(500 CHAR)not null,DECISION_REFERENCE varchar2(255 CHAR)not null,ACTOR varchar2(100)not null,
 CREATED_AT timestamp with time zone default systimestamp not null,RESULT_JSON clob not null check(RESULT_JSON is json),
 FINAL_ADDRESS_SOURCE varchar2(30)not null)';end if;
 select count(*)into n from USER_TABLES where TABLE_NAME='RRL_IW_RECOVERY_DISPATCH';
 if n=0 then execute immediate 'create table RRL_IW_RECOVERY_DISPATCH(
 OPERATION_ID varchar2(100)primary key,BIND_OPERATION_ID varchar2(100)not null unique references RRL_IW_RECOVERY_ST_BIND(OPERATION_ID),
 RECOVERY_OPERATION_ID varchar2(100)not null unique references RRL_INTERWARE_RECOVERY_RECEIPT(OPERATION_ID),
 RECEIPT_OPERATION_ID varchar2(100)not null references RRL_INTERWARE_RECEIPT(OPERATION_ID),
 SOURCE_LOAD_OPERATION_ID varchar2(100)not null,ST_ID number not null,ROOT_UID varchar2(200)not null,BASE_QTY number not null check(BASE_QTY>0),
 BASE_UOM varchar2(20)not null,ACTOR varchar2(100)not null,CREATED_AT timestamp with time zone default systimestamp not null)';end if;
 select count(*)into n from USER_INDEXES where INDEX_NAME='RRL_IW_REC_DISPATCH_SOURCE_IX';
 if n=0 then execute immediate 'create index RRL_IW_REC_DISPATCH_SOURCE_IX on RRL_IW_RECOVERY_DISPATCH(SOURCE_LOAD_OPERATION_ID,OPERATION_ID)';end if;
end;
/
