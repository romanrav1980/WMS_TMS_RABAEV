declare n number;begin
 select count(*)into n from USER_TABLES where TABLE_NAME='RRL_INTERWARE_SHORTAGE_REQUEST';
 if n=0 then execute immediate 'create table RRL_INTERWARE_SHORTAGE_REQUEST(
 OPERATION_ID varchar2(100)primary key,RECEIPT_OPERATION_ID varchar2(100)not null unique references RRL_INTERWARE_RECEIPT(OPERATION_ID),
 PLAN_OPERATION_ID varchar2(100)not null references RRL_INTERWARE_PLAN(OPERATION_ID),SOURCE_LOAD_OPERATION_ID varchar2(100)not null,
 ORIGINAL_UID varchar2(200)not null,ACCEPTED_UID varchar2(200)not null,WARE_ID number not null,
 EXPECTED_QTY number not null,ACCEPTED_QTY number not null,SHORT_QTY number not null,BASE_UOM varchar2(20)not null,
 ACTOR varchar2(100)not null,REASON_TEXT varchar2(500 CHAR)not null,EVIDENCE_REFERENCE varchar2(255 CHAR)not null,
 SOURCE_JSON clob not null check(SOURCE_JSON is json),CREATED_AT timestamp with time zone default systimestamp not null,
 check(EXPECTED_QTY=ACCEPTED_QTY+SHORT_QTY and ACCEPTED_QTY>0 and SHORT_QTY>0))';end if;
 select count(*)into n from USER_TABLES where TABLE_NAME='RRL_INTERWARE_SHORTAGE_FACT';
 if n=0 then execute immediate 'create table RRL_INTERWARE_SHORTAGE_FACT(
 OPERATION_ID varchar2(100)primary key,REQUEST_OPERATION_ID varchar2(100)not null unique references RRL_INTERWARE_SHORTAGE_REQUEST(OPERATION_ID),
 RECEIPT_OPERATION_ID varchar2(100)not null unique references RRL_INTERWARE_RECEIPT(OPERATION_ID),
 ACTOR varchar2(100)not null,REASON_TEXT varchar2(500 CHAR)not null,EVIDENCE_REFERENCE varchar2(255 CHAR)not null,
 SHORT_QTY number not null check(SHORT_QTY>0),SOURCE_JSON clob not null check(SOURCE_JSON is json),
 CREATED_AT timestamp with time zone default systimestamp not null)';end if;
 select count(*)into n from USER_TABLES where TABLE_NAME='RRL_INTERWARE_SHORTAGE_UNIT';
 if n=0 then execute immediate 'create table RRL_INTERWARE_SHORTAGE_UNIT(
 PHYSICAL_UNIT_KEY varchar2(64)primary key,FACT_OPERATION_ID varchar2(100)not null references RRL_INTERWARE_SHORTAGE_FACT(OPERATION_ID),
 ORIGINAL_UID varchar2(200)not null,UNIT_VERSION number not null,BASE_QTY number not null check(BASE_QTY>0),BASE_UOM varchar2(20)not null)';end if;
end;
/
