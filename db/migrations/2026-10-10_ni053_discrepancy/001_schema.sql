declare n number;begin
 select count(*) into n from USER_TAB_COLUMNS where TABLE_NAME='RRL_STORE_RECEIPT_LINE' and COLUMN_NAME='REPORTED_EXTRA_BASE_QTY';
 if n=0 then execute immediate 'alter table RRL_STORE_RECEIPT_LINE add REPORTED_EXTRA_BASE_QTY number(27,9) default 0 not null check(REPORTED_EXTRA_BASE_QTY>=0)';end if;
 select count(*) into n from USER_TABLES where TABLE_NAME='RRL_STORE_DISCREPANCY_CASE';
 if n=0 then execute immediate q'[create table RRL_STORE_DISCREPANCY_CASE(
  CASE_ID varchar2(100) primary key references RRL_STORE_RECEIPT_FACT(OPERATION_ID),
  LOAD_OPERATION_ID varchar2(100) not null references RRL_TT_HU_LOAD_FACT(LOAD_OPERATION_ID),
  STORE_ADDR varchar2(255) not null,STATUS varchar2(30) default 'OPEN' not null,
  REASON_TEXT varchar2(2000) not null,REPORTED_BY varchar2(50) not null,
  CREATED_AT timestamp with time zone default systimestamp not null,
  ASSIGNED_TO varchar2(50),LAST_DECISION_OPERATION varchar2(100))]';
  execute immediate 'create index RRL_STORE_CASE_QUEUE_I1 on RRL_STORE_DISCREPANCY_CASE(STATUS,STORE_ADDR,CREATED_AT)';end if;
 select count(*) into n from USER_TABLES where TABLE_NAME='RRL_STORE_DELIVERY_OBLIGATION';
 if n=0 then execute immediate q'[create table RRL_STORE_DELIVERY_OBLIGATION(
  CASE_ID varchar2(100) not null references RRL_STORE_DISCREPANCY_CASE(CASE_ID),
  LINE_NO number not null,KIND varchar2(30) not null check(KIND in('MISSING_INVESTIGATION','REFUSED_RETURN_DECISION','DAMAGED_RETURN_DECISION','EXCESS_REVIEW')),
  BASE_QTY number(27,9) not null check(BASE_QTY>0),BASE_UOM varchar2(20) not null,
  STATUS varchar2(30) default 'OPEN' not null,
  constraint RRL_STORE_OBLIGATION_PK primary key(CASE_ID,LINE_NO,KIND),
  constraint RRL_STORE_OBLIGATION_LINE_FK foreign key(CASE_ID,LINE_NO) references RRL_STORE_RECEIPT_LINE(OPERATION_ID,LINE_NO))]';end if;
end;
/
