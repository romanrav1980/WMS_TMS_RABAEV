declare n number;
 procedure make(name varchar2,ddl clob)is begin select count(*)into n from USER_TABLES where TABLE_NAME=name;if n=0 then execute immediate ddl;end if;end;
begin
 make('RRL_WORKLOAD_OPERATION',q'[create table RRL_WORKLOAD_OPERATION(
 OPERATION_ID varchar2(100)primary key,WARE_ID number not null,ACTION_KIND varchar2(20)not null,
 ACTOR nvarchar2(50)not null,REQUEST_HASH varchar2(64)not null,RESULT_JSON clob not null check(RESULT_JSON is json),
 CREATED_AT timestamp with time zone default systimestamp not null)]');
 make('RRL_WORKLOAD_NORM',q'[create table RRL_WORKLOAD_NORM(
 WARE_ID number not null,SITE_CODE varchar2(50)not null,ARTICLE varchar2(160)not null,BASE_UOM varchar2(20)not null,
 VERSION_NO number(19)not null check(VERSION_NO>=1),BASE_PER_HOUR number(38,9)not null check(BASE_PER_HOUR>0),
 ACTIVE number(1)not null check(ACTIVE in(0,1)),REASON nvarchar2(500)not null,
 OPERATION_ID varchar2(100)not null unique references RRL_WORKLOAD_OPERATION(OPERATION_ID),
 CREATED_BY nvarchar2(50)not null,CREATED_AT timestamp with time zone default systimestamp not null,
 primary key(WARE_ID,SITE_CODE,ARTICLE,BASE_UOM,VERSION_NO))]');
 make('RRL_WORKLOAD_ATTENDANCE',q'[create table RRL_WORKLOAD_ATTENDANCE(
 PLAN_OPERATION_ID varchar2(100)primary key references RRL_WORKLOAD_OPERATION(OPERATION_ID),
 WARE_ID number not null,SITE_CODE varchar2(50)not null,RESOURCE_ID number not null references RRL_RESOURCE(RESOURCE_ID),
 PERSON_ID nvarchar2(50)not null,START_AT timestamp with time zone not null,FINISH_AT timestamp with time zone not null,
 TASK_TYPE varchar2(40)not null check(TASK_TYPE='CASE_PICK'),REASON nvarchar2(500)not null,
 check(FINISH_AT>START_AT))]');
 make('RRL_WORKLOAD_ATTEND_CANCEL',q'[create table RRL_WORKLOAD_ATTEND_CANCEL(
 PLAN_OPERATION_ID varchar2(100)primary key references RRL_WORKLOAD_ATTENDANCE(PLAN_OPERATION_ID),
 CANCEL_OPERATION_ID varchar2(100)not null unique references RRL_WORKLOAD_OPERATION(OPERATION_ID),
 REASON nvarchar2(500)not null)]');
 select count(*)into n from USER_INDEXES where INDEX_NAME='RRL_WORKLOAD_ATTEND_WARE_I1';
 if n=0 then execute immediate 'create index RRL_WORKLOAD_ATTEND_WARE_I1 on RRL_WORKLOAD_ATTENDANCE(WARE_ID,START_AT,FINISH_AT)';end if;
end;
/
