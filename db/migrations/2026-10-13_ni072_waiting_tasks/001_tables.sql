create table RRL_ST_DEFER_WAIT_RUN(
 OPERATION_ID varchar2(100) primary key,DECISION_OPERATION_ID varchar2(100) not null,
 ACTOR varchar2(100) not null,REQUEST_JSON clob not null,RESULT_JSON clob not null,CREATED_AT timestamp default systimestamp not null,
 constraint RRL_DWAIT_RUN_DEC_FK foreign key(DECISION_OPERATION_ID)references RRL_ST_DEFER_DECISION(OPERATION_ID),
 constraint RRL_DWAIT_RUN_REQ_JSON check(REQUEST_JSON is json),constraint RRL_DWAIT_RUN_RES_JSON check(RESULT_JSON is json));
/
create table RRL_ST_DEFER_WAIT_PLAN(
 TASK_ID number primary key,PLAN_OPERATION_ID varchar2(100) not null,
 UID_PALLET varchar2(50 char) not null,FROM_CELL varchar2(50) not null,TARGET_CELL varchar2(50) not null,
 BASE_QTY number not null,BASE_UOM varchar2(20) not null,STOCK_VERSION number not null,SOURCE_MEMBERS_JSON clob not null,
 constraint RRL_DWAIT_TASK_FK foreign key(TASK_ID)references RRL_WAREHOUSE_TASK(TASK_ID),
 constraint RRL_DWAIT_RUN_FK foreign key(PLAN_OPERATION_ID)references RRL_ST_DEFER_WAIT_RUN(OPERATION_ID),
 constraint RRL_DWAIT_UID_UQ unique(PLAN_OPERATION_ID,UID_PALLET),
 constraint RRL_DWAIT_QTY_CHECK check(BASE_QTY>0),constraint RRL_DWAIT_MEMBERS_JSON check(SOURCE_MEMBERS_JSON is json));
/
