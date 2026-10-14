declare n number;begin
 select count(*)into n from USER_TABLES where TABLE_NAME='RRL_IW_RECOVERY_CANCEL';
 if n=0 then execute immediate 'create table RRL_IW_RECOVERY_CANCEL(
 OPERATION_ID varchar2(100)primary key,REQUEST_OPERATION_ID varchar2(100)not null unique references RRL_INTERWARE_RECOVERY_REQUEST(OPERATION_ID),
 LOSS_OPERATION_ID varchar2(100)not null references RRL_INTERWARE_SHORTAGE_FACT(OPERATION_ID),WARE_ID number not null,
 BASE_QTY number not null check(BASE_QTY>0),BASE_UOM varchar2(20)not null,ACTOR varchar2(100)not null,
 REASON_TEXT varchar2(500 CHAR)not null,EVIDENCE_REFERENCE varchar2(255 CHAR)not null,SOURCE_JSON clob not null check(SOURCE_JSON is json),
 CREATED_AT timestamp with time zone default systimestamp not null)';end if;
end;
/
