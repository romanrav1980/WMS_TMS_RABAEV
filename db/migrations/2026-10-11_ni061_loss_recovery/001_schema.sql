declare n number;begin
 select count(*)into n from USER_TABLES where TABLE_NAME='RRL_INTERWARE_RECOVERY_REQUEST';
 if n=0 then execute immediate 'create table RRL_INTERWARE_RECOVERY_REQUEST(
 OPERATION_ID varchar2(100)primary key,LOSS_OPERATION_ID varchar2(100)not null unique references RRL_INTERWARE_SHORTAGE_FACT(OPERATION_ID),
 RECEIPT_OPERATION_ID varchar2(100)not null references RRL_INTERWARE_RECEIPT(OPERATION_ID),WARE_ID number not null,
 BASE_QTY number not null check(BASE_QTY>0),BASE_UOM varchar2(20)not null,ACTOR varchar2(100)not null,
 REASON_TEXT varchar2(500 CHAR)not null,EVIDENCE_REFERENCE varchar2(255 CHAR)not null,SOURCE_JSON clob not null check(SOURCE_JSON is json),
 CREATED_AT timestamp with time zone default systimestamp not null)';end if;
 select count(*)into n from USER_TABLES where TABLE_NAME='RRL_INTERWARE_RECOVERY_APPROVAL';
 if n=0 then execute immediate 'create table RRL_INTERWARE_RECOVERY_APPROVAL(
 OPERATION_ID varchar2(100)primary key,REQUEST_OPERATION_ID varchar2(100)not null unique references RRL_INTERWARE_RECOVERY_REQUEST(OPERATION_ID),
 ACTOR varchar2(100)not null,REASON_TEXT varchar2(500 CHAR)not null,EVIDENCE_REFERENCE varchar2(255 CHAR)not null,
 SOURCE_JSON clob not null check(SOURCE_JSON is json),CREATED_AT timestamp with time zone default systimestamp not null)';end if;
 select count(*)into n from USER_TABLES where TABLE_NAME='RRL_INTERWARE_RECOVERY_RECEIPT';
 if n=0 then execute immediate 'create table RRL_INTERWARE_RECOVERY_RECEIPT(
 OPERATION_ID varchar2(100)primary key,APPROVAL_OPERATION_ID varchar2(100)not null unique references RRL_INTERWARE_RECOVERY_APPROVAL(OPERATION_ID),
 LOSS_OPERATION_ID varchar2(100)not null unique references RRL_INTERWARE_SHORTAGE_FACT(OPERATION_ID),WARE_ID number not null,ROOT_UID varchar2(200)not null unique,
 RECEIVE_CELL varchar2(60)not null,ARTICLE varchar2(160)not null,BASE_QTY number not null check(BASE_QTY>0),BASE_UOM varchar2(20)not null,
 STOCK_EVENT_ID number not null,ACTOR varchar2(100)not null,SOURCE_JSON clob not null check(SOURCE_JSON is json),
 CREATED_AT timestamp with time zone default systimestamp not null)';end if;
 select count(*)into n from USER_TABLES where TABLE_NAME='RRL_INTERWARE_RECOVERY_UNIT';
 if n=0 then execute immediate 'create table RRL_INTERWARE_RECOVERY_UNIT(
 PHYSICAL_UNIT_KEY varchar2(64)primary key,RECOVERY_OPERATION_ID varchar2(100)not null references RRL_INTERWARE_RECOVERY_RECEIPT(OPERATION_ID),
 LOSS_OPERATION_ID varchar2(100)not null references RRL_INTERWARE_SHORTAGE_FACT(OPERATION_ID),BASE_QTY number not null check(BASE_QTY>0),
 BASE_UOM varchar2(20)not null,PREVIOUS_UNIT_VERSION number not null)';end if;
end;
/
