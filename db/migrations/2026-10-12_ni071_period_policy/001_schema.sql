begin execute immediate q'[create table RRL_LOG_COST_PERIOD_HEAD(WARE_ID number primary key,VERSION_NO number(19)not null check(VERSION_NO>=0))]';exception when others then if sqlcode!=-955 then raise;end if;end;
/
begin execute immediate q'[create table RRL_LOG_COST_PERIOD_HISTORY(
 WARE_ID number not null references RRL_LOG_COST_PERIOD_HEAD(WARE_ID),VERSION_NO number(19)not null,
 OPERATION_ID varchar2(100)not null unique,PAYLOAD_HASH raw(32)not null,
 PERIOD_MODE varchar2(20)not null check(PERIOD_MODE in('LOADED_UTC','CASE_ASSEMBLY')),
 TIME_ZONE varchar2(64),ACTOR nvarchar2(50)not null,REASON_TEXT varchar2(2000 byte)not null,DECISION_REFERENCE varchar2(255 byte)not null,
 CREATED_AT timestamp with time zone default systimestamp not null,RESULT_JSON clob not null check(RESULT_JSON is json),
 primary key(WARE_ID,VERSION_NO),check((PERIOD_MODE='LOADED_UTC'and TIME_ZONE is null)or(PERIOD_MODE='CASE_ASSEMBLY'and TIME_ZONE is not null))
)]';exception when others then if sqlcode!=-955 then raise;end if;end;
/
declare n number;begin select count(*)into n from USER_TAB_COLUMNS where TABLE_NAME='RRL_LOGISTICS_COST_LINE'and COLUMN_NAME='RATE_DATE';
 if n=0 then execute immediate 'alter table RRL_LOGISTICS_COST_LINE add(RATE_DATE date,PERIOD_MODE varchar2(20),PERIOD_TIME_ZONE varchar2(64),PERIOD_POLICY_VERSION number(19))';end if;
end;
/
