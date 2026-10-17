-- MIGRATION_ID: 2026-10-15-wave-launch-continuation
create table RRL_WAVE_CONTINUE(
 LAUNCH_OPERATION_ID varchar2(100) primary key,PICK_WAVE_ID number not null unique,ACTOR varchar2(50) not null,
 STATE varchar2(12) default 'PENDING' not null,SOURCES_FROZEN number(1) default 0 not null,
 CREATED_AT timestamp default systimestamp not null,UPDATED_AT timestamp default systimestamp not null,
 constraint RRL_WAVE_CONTINUE_STATE check(STATE in('PENDING','FAILED','COMPLETE')),
 constraint RRL_WAVE_CONTINUE_FROZEN check(SOURCES_FROZEN in(0,1)));
create table RRL_WAVE_CONTINUE_STEP(
 LAUNCH_OPERATION_ID varchar2(100) not null references RRL_WAVE_CONTINUE(LAUNCH_OPERATION_ID),
 STEP_NO number(1) not null,STEP_NAME varchar2(40) not null,STATE varchar2(12) not null,
 COMPLETED_AT timestamp,ERROR_CODE varchar2(100),
 constraint RRL_WAVE_CONTINUE_STEP_PK primary key(LAUNCH_OPERATION_ID,STEP_NO),
 constraint RRL_WAVE_CONTINUE_STEP_NO check(STEP_NO between 1 and 7),
 constraint RRL_WAVE_CONTINUE_STEP_ST check(STATE in('PENDING','FAILED','DONE')));
create table RRL_WAVE_CONTINUE_SOURCE(
 LAUNCH_OPERATION_ID varchar2(100) not null references RRL_WAVE_CONTINUE(LAUNCH_OPERATION_ID),
 REPLENISH_TASK_ID number not null,SOURCE_OPERATION_ID varchar2(100) not null unique,CANONICAL_REQUEST clob not null,
 constraint RRL_WAVE_CONTINUE_SOURCE_PK primary key(LAUNCH_OPERATION_ID,REPLENISH_TASK_ID),
 constraint RRL_WAVE_CONT_SOURCE_JSON check(CANONICAL_REQUEST is json));
