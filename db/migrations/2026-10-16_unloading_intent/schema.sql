create table RRL_STORE_UNLOAD_INTENT(
 CONTROL_OPERATION_ID varchar2(100)not null,ORIGINAL_OPERATION_ID varchar2(100)not null,
 LOAD_OPERATION_ID varchar2(100)not null,STORE_ADDR varchar2(255)not null,ACTOR varchar2(50)not null,
 OUTCOME varchar2(20)not null,ORIGINAL_JSON clob not null,CONTROL_JSON clob not null,
 RESULT_JSON clob not null,RECORDED_AT timestamp(6)with time zone default systimestamp not null,
 constraint RRL_UNLOAD_INTENT_PK primary key(CONTROL_OPERATION_ID),
 constraint RRL_UNLOAD_INTENT_OP_UK unique(ORIGINAL_OPERATION_ID),
 constraint RRL_UNLOAD_INTENT_LOAD_FK foreign key(LOAD_OPERATION_ID)references RRL_TT_HU_LOAD_FACT(LOAD_OPERATION_ID),
 constraint RRL_UNLOAD_INTENT_STATE_C check(OUTCOME in('ABANDONED','RECORDED')),
 constraint RRL_UNLOAD_INTENT_JSON_C check(ORIGINAL_JSON is json and CONTROL_JSON is json and RESULT_JSON is json)
);
