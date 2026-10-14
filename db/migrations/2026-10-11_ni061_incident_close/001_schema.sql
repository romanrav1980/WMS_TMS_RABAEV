declare n number;begin
 select count(*)into n from USER_TABLES where TABLE_NAME='RRL_INTERWARE_INCIDENT_CLOSE';
 if n=0 then execute immediate 'create table RRL_INTERWARE_INCIDENT_CLOSE(
 OPERATION_ID varchar2(100)primary key,PLAN_OPERATION_ID varchar2(100)not null,INCIDENT_OPERATION_ID varchar2(100)not null unique,
 FOLLOWUP_RECEIPT_OPERATION_ID varchar2(100)not null,ACTOR varchar2(100)not null,REASON_TEXT varchar2(500 CHAR)not null,EVIDENCE_REFERENCE varchar2(255 CHAR)not null,
 REQUEST_HASH varchar2(64)not null,REQUEST_JSON clob not null check(REQUEST_JSON is json),RESULT_JSON clob not null check(RESULT_JSON is json),CLOSED_AT timestamp with time zone default systimestamp not null,
 foreign key(PLAN_OPERATION_ID)references RRL_INTERWARE_PLAN(OPERATION_ID),foreign key(INCIDENT_OPERATION_ID)references RRL_INTERWARE_DECISION(OPERATION_ID),
 foreign key(FOLLOWUP_RECEIPT_OPERATION_ID)references RRL_INTERWARE_RECEIPT(OPERATION_ID))';end if;
end;
/
