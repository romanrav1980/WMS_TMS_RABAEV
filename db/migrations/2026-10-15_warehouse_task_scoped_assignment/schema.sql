create table RRL_WTASK_ASSIGN_VERSION(
 TASK_ID number primary key references RRL_WAREHOUSE_TASK(TASK_ID),
 ASSIGNMENT_VERSION number not null check(ASSIGNMENT_VERSION>=0 and ASSIGNMENT_VERSION=trunc(ASSIGNMENT_VERSION)),
 CHANGED_AT timestamp with time zone default systimestamp not null
);
create table RRL_WTASK_RESOURCE_COMMAND(
 OPERATION_ID varchar2(100)primary key,TASK_ID number not null references RRL_WAREHOUSE_TASK(TASK_ID),ACTOR_ID varchar2(100)not null,
 TARGET_ID varchar2(100)not null,ACTION varchar2(10)not null check(ACTION in('ASSIGN','START')),
 OUTCOME varchar2(10)not null check(OUTCOME in('APPLIED','REJECTED')),ERROR_CODE varchar2(100),
 SOURCE_SHA256 varchar2(64)not null,SOURCE_JSON clob not null check(SOURCE_JSON is json),RESULT_JSON clob not null check(RESULT_JSON is json),
 BEFORE_VERSION number not null,AFTER_VERSION number not null,RECORDED_AT timestamp with time zone default systimestamp not null,
 check(BEFORE_VERSION>=0 and AFTER_VERSION>=BEFORE_VERSION),
 check((OUTCOME='APPLIED'and ERROR_CODE is null)or(OUTCOME='REJECTED'and ERROR_CODE is not null and BEFORE_VERSION=AFTER_VERSION))
);
create index RRL_WTASK_COMMAND_TASK_IX on RRL_WTASK_RESOURCE_COMMAND(TASK_ID,ACTOR_ID,RECORDED_AT);
