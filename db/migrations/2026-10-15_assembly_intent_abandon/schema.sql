create table RRL_ASM_INTENT_ABANDON(
 ABANDONMENT_ID varchar2(100)primary key,IDENTITY_KEY varchar2(64)not null unique,
 INTENT_KIND varchar2(20)not null,ACTOR_ID nvarchar2(50)not null,CASE_PICK_TASK_ID number not null,
 SESSION_ID varchar2(100)not null,STEP_ID varchar2(100),ORIGINAL_OPERATION_ID varchar2(100),
 SOURCE_SHA256 varchar2(64)not null,SOURCE_JSON clob not null check(SOURCE_JSON is json),
 ORIGINAL_JSON clob not null check(ORIGINAL_JSON is json),RESULT_JSON clob not null check(RESULT_JSON is json),
 RECORDED_AT timestamp with time zone default systimestamp not null,
 foreign key(CASE_PICK_TASK_ID)references RRL_CASE_PICK_TASK(CASE_PICK_TASK_ID),
 check(INTENT_KIND in('OPEN_SESSION','OPEN_STEP')),
 check((INTENT_KIND='OPEN_SESSION'and STEP_ID is null and ORIGINAL_OPERATION_ID is null)or(INTENT_KIND='OPEN_STEP'and STEP_ID is not null and ORIGINAL_OPERATION_ID is not null))
);
create index RRL_ASM_INTENT_OLD_OP_IX on RRL_ASM_INTENT_ABANDON(ACTOR_ID,CASE_PICK_TASK_ID,ORIGINAL_OPERATION_ID);
