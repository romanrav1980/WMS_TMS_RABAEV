declare n number;
begin
 select count(*) into n from user_tab_columns where table_name='RRL_STORE_DISCREPANCY_CASE' and column_name='CASE_VERSION';
 if n=0 then execute immediate 'alter table RRL_STORE_DISCREPANCY_CASE add(
 CASE_VERSION number(19) default 1 not null,EXPEDITION_USER nvarchar2(50),SECURITY_USER nvarchar2(50),SEARCH_DEADLINE timestamp with time zone)';end if;
 select count(*) into n from user_tables where table_name='RRL_STORE_CASE_ACTION';
 if n=0 then execute immediate 'create table RRL_STORE_CASE_ACTION(
 OPERATION_ID varchar2(100) primary key references RRL_STOCK_OPERATION(OPERATION_ID),
 CASE_ID varchar2(100) not null references RRL_STORE_DISCREPANCY_CASE(CASE_ID),
 ACTION_CODE varchar2(30) not null,VERSION_BEFORE number(19) not null,VERSION_AFTER number(19) not null,
 ACTOR varchar2(50) not null,DETAILS_JSON clob not null check(DETAILS_JSON is json),
 CREATED_AT timestamp with time zone default systimestamp not null)';
 execute immediate 'create index RRL_STORE_CASE_ACTION_I1 on RRL_STORE_CASE_ACTION(CASE_ID,VERSION_AFTER)';end if;
 select count(*) into n from user_tables where table_name='RRL_STORE_CASE_FINDING';
 if n=0 then execute immediate 'create table RRL_STORE_CASE_FINDING(
 OPERATION_ID varchar2(100) primary key references RRL_STORE_CASE_ACTION(OPERATION_ID),
 CASE_ID varchar2(100) not null references RRL_STORE_DISCREPANCY_CASE(CASE_ID),
 ROLE_CODE varchar2(20) not null check(ROLE_CODE in(''EXPEDITION'',''SECURITY'')),REPORT_TEXT varchar2(2000) not null,
 REPORTED_BY varchar2(50) not null,CREATED_AT timestamp with time zone default systimestamp not null)';
 execute immediate 'create index RRL_STORE_CASE_FINDING_I1 on RRL_STORE_CASE_FINDING(CASE_ID,ROLE_CODE,REPORTED_BY)';end if;
 select count(*) into n from user_tables where table_name='RRL_STORE_LOSS_RECOGNITION';
 if n=0 then execute immediate 'create table RRL_STORE_LOSS_RECOGNITION(
 OPERATION_ID varchar2(100) primary key references RRL_STORE_CASE_ACTION(OPERATION_ID),
 CASE_ID varchar2(100) not null,LINE_NO number not null,LOT_UID varchar2(200) not null,
 ARTICLE varchar2(160) not null,BASE_UOM varchar2(20) not null,BASE_QTY number(27,9) not null check(BASE_QTY>0),
 REASON_TEXT varchar2(2000) not null,CONFIRMED_BY varchar2(50) not null,
 CREATED_AT timestamp with time zone default systimestamp not null,unique(CASE_ID,LINE_NO),
 foreign key(CASE_ID,LINE_NO) references RRL_STORE_RECEIPT_LINE(OPERATION_ID,LINE_NO))';end if;
end;
/
