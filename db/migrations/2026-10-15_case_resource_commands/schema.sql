alter table RRL_CASE_PICK_TASK add(ASSIGNMENT_VERSION number default 0 not null check(ASSIGNMENT_VERSION>=0 and ASSIGNMENT_VERSION=trunc(ASSIGNMENT_VERSION)));
create table RRL_CASE_RESOURCE_COMMAND(
 OPERATION_ID varchar2(100)primary key,CASE_PICK_TASK_ID number not null references RRL_CASE_PICK_TASK(CASE_PICK_TASK_ID),
 ACTOR_ID nvarchar2(50)not null,ACTION varchar2(10)not null check(ACTION in('CLAIM','START')),
 OUTCOME varchar2(10)not null check(OUTCOME in('APPLIED','REJECTED')),ERROR_CODE varchar2(100),
 SOURCE_SHA256 varchar2(64)not null,SOURCE_JSON clob not null check(SOURCE_JSON is json),
 RESULT_JSON clob not null check(RESULT_JSON is json),BEFORE_VERSION number not null,AFTER_VERSION number not null,
 RESOURCE_SESSION_ID number not null check(RESOURCE_SESSION_ID>0),RECORDED_AT timestamp with time zone default systimestamp not null,
 check(BEFORE_VERSION>=0 and AFTER_VERSION>=BEFORE_VERSION),
 check((OUTCOME='APPLIED'and ERROR_CODE is null)or(OUTCOME='REJECTED'and ERROR_CODE is not null and BEFORE_VERSION=AFTER_VERSION))
);
create index RRL_CASE_RESOURCE_TASK_IX on RRL_CASE_RESOURCE_COMMAND(CASE_PICK_TASK_ID,ACTOR_ID,RECORDED_AT);
