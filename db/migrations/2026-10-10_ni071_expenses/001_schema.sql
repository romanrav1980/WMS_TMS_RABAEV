begin execute immediate q'[create table RRL_LOGISTICS_EXP_ARTICLE(
 CODE varchar2(40) primary key,NAME varchar2(500 byte) not null,
 OBJECT_SCOPE varchar2(10) not null check(OBJECT_SCOPE in('TRIP','VEHICLE','BOTH')),
 INCLUDED_IN_RATE number(1) not null check(INCLUDED_IN_RATE in(0,1)),
 ACTIVE_FLAG number(1) not null check(ACTIVE_FLAG in(0,1)),VERSION_NO number(19) not null check(VERSION_NO>0),
 ACTOR nvarchar2(50) not null,CHANGED_AT timestamp with time zone default systimestamp not null
)]';exception when others then if sqlcode!=-955 then raise;end if;end;
/
begin execute immediate q'[create table RRL_LOGISTICS_EXPENSE(
 OPERATION_ID varchar2(100) primary key,PAYLOAD_HASH raw(32) not null,
 ARTICLE_CODE varchar2(40) not null references RRL_LOGISTICS_EXP_ARTICLE(CODE),ARTICLE_VERSION number(19) not null,
 ARTICLE_NAME varchar2(500 byte) not null,WARE_ID number not null,
 OBJECT_KIND varchar2(10) not null check(OBJECT_KIND in('TRIP','VEHICLE')),OBJECT_ID number not null,
 AMOUNT number(27,2) not null check(AMOUNT>0),CURRENCY varchar2(3) not null check(regexp_like(CURRENCY,'^[A-Z]{3}$')),
 EXPENSE_DATE date not null,DOCUMENT_REFERENCE varchar2(255 byte) not null,REASON_TEXT varchar2(2000 byte) not null,
 ACTOR nvarchar2(50) not null,CREATED_AT timestamp with time zone default systimestamp not null,
 RESULT_JSON clob not null check(RESULT_JSON is json)
)]';exception when others then if sqlcode!=-955 then raise;end if;end;
/
begin execute immediate q'[create table RRL_LOGISTICS_EXP_DECISION(
 OPERATION_ID varchar2(100) primary key,PAYLOAD_HASH raw(32) not null,
 EXPENSE_OPERATION_ID varchar2(100) not null references RRL_LOGISTICS_EXPENSE(OPERATION_ID),
 PHASE varchar2(10) not null check(PHASE in('LOGIST','FINANCE')),OUTCOME varchar2(10) not null check(OUTCOME in('APPROVE','REJECT')),
 DISTRIBUTION_BASIS varchar2(20) not null check(DISTRIBUTION_BASIS in('NONE','BASE_QUANTITY','WEIGHT')),
 DECISION_REFERENCE varchar2(255 byte) not null,REASON_TEXT varchar2(2000 byte) not null,
 ACTOR nvarchar2(50) not null,CREATED_AT timestamp with time zone default systimestamp not null,
 RESULT_JSON clob not null check(RESULT_JSON is json),
 unique(EXPENSE_OPERATION_ID,PHASE)
)]';exception when others then if sqlcode!=-955 then raise;end if;end;
/
begin execute immediate 'create index RRL_LOG_EXP_OBJECT_IDX on RRL_LOGISTICS_EXPENSE(OBJECT_KIND,OBJECT_ID,WARE_ID,EXPENSE_DATE)';exception when others then if sqlcode!=-955 then raise;end if;end;
/
