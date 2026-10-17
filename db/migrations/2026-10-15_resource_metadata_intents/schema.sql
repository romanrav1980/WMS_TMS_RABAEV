-- PREPARED ONLY. No application by author.
begin
 execute immediate q'[create table RRL_RESOURCE_INTENT_ABANDON(
  CONTROL_OPERATION_ID varchar2(100)primary key,DOMAIN varchar2(4)not null,
  ORIGINAL_OPERATION_ID varchar2(100)not null,ACTOR_ID nvarchar2(100)not null,
  CASE_TASK_ID number references RRL_CASE_PICK_TASK(CASE_PICK_TASK_ID),
  TASK_ID number references RRL_WAREHOUSE_TASK(TASK_ID),ACTION varchar2(10)not null,TARGET_ID nvarchar2(100)not null,
  ORIGINAL_EXPECTED_VERSION number not null,VERSION_AT_ABANDON number not null,
  ORIGINAL_SHA256 varchar2(64)not null,CONTROL_SHA256 varchar2(64)not null,
  ORIGINAL_JSON clob not null check(ORIGINAL_JSON is json),SOURCE_JSON clob not null check(SOURCE_JSON is json),
  RESULT_JSON clob not null check(RESULT_JSON is json),RECORDED_AT timestamp with time zone default systimestamp not null,
  constraint RRL_RESOURCE_INTENT_OLD_UK unique(DOMAIN,ORIGINAL_OPERATION_ID),
  check((DOMAIN='CASE'and CASE_TASK_ID is not null and TASK_ID is null and ACTION in('CLAIM','START'))
     or(DOMAIN='TASK'and TASK_ID is not null and CASE_TASK_ID is null and ACTION in('ASSIGN','START'))),
  check(ORIGINAL_EXPECTED_VERSION>=0 and ORIGINAL_EXPECTED_VERSION=trunc(ORIGINAL_EXPECTED_VERSION)),
  check(VERSION_AT_ABANDON>=0 and VERSION_AT_ABANDON=trunc(VERSION_AT_ABANDON))
 )]';
end;
/
