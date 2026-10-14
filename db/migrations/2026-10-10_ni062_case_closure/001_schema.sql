begin execute immediate q'[create table RRL_STORE_CASE_CLOSURE(
 OPERATION_ID varchar2(100) primary key references RRL_STOCK_OPERATION(OPERATION_ID),
 CASE_ID varchar2(100) not null unique references RRL_STORE_DISCREPANCY_CASE(CASE_ID),
 WARE_ID number not null,EXPEDITION_FINDING_OP varchar2(100) not null references RRL_STORE_CASE_FINDING(OPERATION_ID),
 SECURITY_FINDING_OP varchar2(100) not null references RRL_STORE_CASE_FINDING(OPERATION_ID),
 REASON_TEXT varchar2(2000 byte) not null,DECISION_REFERENCE varchar2(255 byte) not null,
 ACTOR nvarchar2(50) not null,CREATED_AT timestamp with time zone default systimestamp not null
)]';exception when others then if sqlcode!=-955 then raise;end if;end;
/
