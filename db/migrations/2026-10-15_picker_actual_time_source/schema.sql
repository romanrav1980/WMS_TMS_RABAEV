create table RRL_PICKER_TIME_STREAM(
 OPERATOR_ID varchar2(100) constraint PT_STR_01 primary key,
 STREAM_VERSION number constraint PT_STR_02 not null constraint PT_STR_03 check(STREAM_VERSION>=1 and STREAM_VERSION=trunc(STREAM_VERSION)),
 SHIFT_STATE varchar2(8) constraint PT_STR_04 not null constraint PT_STR_05 check(SHIFT_STATE in('OFF','OPEN')),
 WORK_STATE varchar2(8) constraint PT_STR_06 not null constraint PT_STR_07 check(WORK_STATE in('IDLE','WORK','PAUSED')),
 WARE_ID number constraint PT_STR_08 references RRL_WARES(ID),RESOURCE_SESSION_ID number constraint PT_STR_09 references RRL_RESOURCE_SESSION(SESSION_ID),
 RESOURCE_ID number constraint PT_STR_10 references RRL_RESOURCE(RESOURCE_ID),SOURCE_KIND varchar2(24),SOURCE_ID number,
 SHIFT_START_AT timestamp with time zone,WORK_START_AT timestamp with time zone,PAUSE_START_AT timestamp with time zone,
 SHIFT_START_OP varchar2(100),WORK_START_OP varchar2(100),PAUSE_START_OP varchar2(100),
 LAST_EVENT_AT timestamp with time zone constraint PT_STR_11 not null,
 constraint PT_STR_12 check((SOURCE_KIND is null and SOURCE_ID is null)or(SOURCE_KIND is not null and SOURCE_KIND in('CASE_PICK_TASK','WAREHOUSE_TASK')and SOURCE_ID is not null and SOURCE_ID>0)),
 constraint PT_STR_13 check((SHIFT_STATE='OFF'and WORK_STATE='IDLE'and WARE_ID is null and RESOURCE_SESSION_ID is null and RESOURCE_ID is null and SHIFT_START_AT is null and SHIFT_START_OP is null)
    or(SHIFT_STATE='OPEN'and WARE_ID is not null and RESOURCE_SESSION_ID is not null and RESOURCE_ID is not null and SHIFT_START_AT is not null and SHIFT_START_OP is not null)),
 constraint PT_STR_14 check((WORK_STATE='IDLE'and WORK_START_AT is null and WORK_START_OP is null and SOURCE_KIND is null and SOURCE_ID is null)
    or(WORK_STATE in('WORK','PAUSED')and SHIFT_STATE='OPEN'and WORK_START_AT is not null and WORK_START_OP is not null and SOURCE_KIND is not null and SOURCE_ID is not null)),
 constraint PT_STR_15 check((WORK_STATE='PAUSED'and PAUSE_START_AT is not null and PAUSE_START_OP is not null)
    or(WORK_STATE!='PAUSED'and PAUSE_START_AT is null and PAUSE_START_OP is null))
);
create table RRL_PICKER_TIME_EVENT(
 OPERATION_ID varchar2(100) constraint PT_EV_01 primary key,OPERATOR_ID varchar2(100) constraint PT_EV_02 not null constraint PT_EV_03 references RRL_PICKER_TIME_STREAM(OPERATOR_ID),
 WARE_ID number constraint PT_EV_04 not null constraint PT_EV_05 references RRL_WARES(ID),RESOURCE_SESSION_ID number constraint PT_EV_06 not null constraint PT_EV_07 references RRL_RESOURCE_SESSION(SESSION_ID),
 RESOURCE_ID number constraint PT_EV_08 not null constraint PT_EV_09 references RRL_RESOURCE(RESOURCE_ID),ACTOR_ID varchar2(100) constraint PT_EV_10 not null,
 ACTION varchar2(24) constraint PT_EV_11 not null constraint PT_EV_12 check(ACTION in('ACTUAL_SHIFT_START','ACTUAL_SHIFT_FINISH','WORK_START','PAUSE','RESUME','WORK_FINISH')),
 EFFECTIVE_AT timestamp with time zone constraint PT_EV_13 not null,BEFORE_VERSION number constraint PT_EV_14 not null,AFTER_VERSION number constraint PT_EV_15 not null,
 SOURCE_KIND varchar2(24),SOURCE_ID number,SOURCE_MODE varchar2(24) default 'MANUAL_CONFIRMED' constraint PT_EV_16 not null constraint PT_EV_17 check(SOURCE_MODE='MANUAL_CONFIRMED'),
 REASON nvarchar2(1000) constraint PT_EV_18 not null,
 constraint PT_EV_19 check(BEFORE_VERSION>=0 and AFTER_VERSION=BEFORE_VERSION+1 and ACTOR_ID=OPERATOR_ID),
 constraint PT_EV_20 unique(OPERATOR_ID,AFTER_VERSION),
 constraint PT_EV_21 check((ACTION in('ACTUAL_SHIFT_START','ACTUAL_SHIFT_FINISH')and SOURCE_KIND is null and SOURCE_ID is null)
    or(ACTION in('WORK_START','PAUSE','RESUME','WORK_FINISH')and SOURCE_KIND is not null and SOURCE_KIND in('CASE_PICK_TASK','WAREHOUSE_TASK')and SOURCE_ID is not null and SOURCE_ID>0))
);
create index RRL_PICKER_TIME_EVENT_OP_IX on RRL_PICKER_TIME_EVENT(OPERATOR_ID,EFFECTIVE_AT);
create table RRL_PICKER_TIME_SPAN(
 SPAN_ID varchar2(130) constraint PT_SP_01 primary key,OPERATOR_ID varchar2(100) constraint PT_SP_02 not null constraint PT_SP_03 references RRL_PICKER_TIME_STREAM(OPERATOR_ID),
 KIND varchar2(16) constraint PT_SP_04 not null constraint PT_SP_05 check(KIND in('ACTUAL_SHIFT','WORK','PAUSE')),
 WARE_ID number constraint PT_SP_06 not null constraint PT_SP_07 references RRL_WARES(ID),RESOURCE_SESSION_ID number constraint PT_SP_08 not null constraint PT_SP_09 references RRL_RESOURCE_SESSION(SESSION_ID),
 SOURCE_KIND varchar2(24) constraint PT_SP_10 not null constraint PT_SP_11 check(SOURCE_KIND in('RESOURCE_SESSION','CASE_PICK_TASK','WAREHOUSE_TASK')),SOURCE_ID number constraint PT_SP_12 not null constraint PT_SP_13 check(SOURCE_ID>0),
 START_AT timestamp with time zone constraint PT_SP_14 not null,FINISH_AT timestamp with time zone constraint PT_SP_15 not null,
 START_OPERATION_ID varchar2(100) constraint PT_SP_16 not null constraint PT_SP_17 references RRL_PICKER_TIME_EVENT(OPERATION_ID),
 FINISH_OPERATION_ID varchar2(100) constraint PT_SP_18 not null constraint PT_SP_19 references RRL_PICKER_TIME_EVENT(OPERATION_ID),
 SOURCE_MODE varchar2(24) default 'MANUAL_CONFIRMED' constraint PT_SP_20 not null constraint PT_SP_21 check(SOURCE_MODE='MANUAL_CONFIRMED'),
 constraint PT_SP_22 check(FINISH_AT>START_AT),constraint PT_SP_23 unique(FINISH_OPERATION_ID,KIND),
 constraint PT_SP_24 check((KIND='ACTUAL_SHIFT'and SOURCE_KIND='RESOURCE_SESSION')or(KIND in('WORK','PAUSE')and SOURCE_KIND in('CASE_PICK_TASK','WAREHOUSE_TASK')))
);
create index RRL_PICKER_TIME_SPAN_OP_IX on RRL_PICKER_TIME_SPAN(OPERATOR_ID,FINISH_AT,START_AT);
create table RRL_PICKER_TIME_COMMAND(
 OPERATION_ID varchar2(100) constraint PT_CMD_01 primary key,ACTOR_ID varchar2(100) constraint PT_CMD_02 not null,
 WARE_ID number constraint PT_CMD_03 not null constraint PT_CMD_04 references RRL_WARES(ID),RESOURCE_SESSION_ID number constraint PT_CMD_05 not null constraint PT_CMD_06 references RRL_RESOURCE_SESSION(SESSION_ID),
 ACTION varchar2(24) constraint PT_CMD_07 not null constraint PT_CMD_08 check(ACTION in('ACTUAL_SHIFT_START','ACTUAL_SHIFT_FINISH','WORK_START','PAUSE','RESUME','WORK_FINISH')),
 OUTCOME varchar2(10) constraint PT_CMD_09 not null constraint PT_CMD_10 check(OUTCOME in('APPLIED','REJECTED')),ERROR_CODE varchar2(100),
 SOURCE_SHA256 varchar2(64) constraint PT_CMD_11 not null,SOURCE_JSON clob constraint PT_CMD_12 not null constraint PT_CMD_13 check(SOURCE_JSON is json),RESULT_JSON clob constraint PT_CMD_14 not null constraint PT_CMD_15 check(RESULT_JSON is json),
 BEFORE_VERSION number constraint PT_CMD_16 not null,AFTER_VERSION number constraint PT_CMD_17 not null,RECORDED_AT timestamp with time zone default systimestamp constraint PT_CMD_18 not null,
 constraint PT_CMD_19 check(BEFORE_VERSION>=0 and AFTER_VERSION>=BEFORE_VERSION),
 constraint PT_CMD_20 check((OUTCOME='APPLIED'and ERROR_CODE is null and AFTER_VERSION=BEFORE_VERSION+1)
    or(OUTCOME='REJECTED'and ERROR_CODE is not null and AFTER_VERSION=BEFORE_VERSION))
);
create index RRL_PICKER_TIME_CMD_OP_IX on RRL_PICKER_TIME_COMMAND(ACTOR_ID,RECORDED_AT);
