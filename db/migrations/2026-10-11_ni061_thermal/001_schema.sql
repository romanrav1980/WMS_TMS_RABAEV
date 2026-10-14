create table RRL_INTERWARE_THERMAL_FACT(
 OPERATION_ID varchar2(100)constraint RRL_IW_THERM_PK primary key,
 PLAN_OPERATION_ID varchar2(100)not null references RRL_INTERWARE_PLAN(OPERATION_ID),
 REVISION_NO number(10)not null,DECISION_KIND varchar2(10)not null check(DECISION_KIND in('HOLD','PROCEED')),
 OBSERVED_C number(8,3)not null,OBSERVATION_REFERENCE nvarchar2(200)not null,
 TASK_TEMP_MIN number(8,3),TASK_TEMP_MAX number(8,3),SKU_TEMP_MIN number,SKU_TEMP_MAX number,
 REASON_TEXT nvarchar2(500)not null,DECISION_REFERENCE varchar2(60)not null,ACTOR nvarchar2(50)not null,
 PAYLOAD_HASH raw(32)not null,CANONICAL_REQUEST clob not null check(CANONICAL_REQUEST is json),
 RESULT_JSON clob not null check(RESULT_JSON is json),CREATED_AT timestamp with time zone default systimestamp not null,
 constraint RRL_IW_THERM_REV_UK unique(PLAN_OPERATION_ID,REVISION_NO),
 constraint RRL_IW_THERM_RANGE_CK check((TASK_TEMP_MIN is null and TASK_TEMP_MAX is null)or(TASK_TEMP_MIN is not null and TASK_TEMP_MAX is not null and TASK_TEMP_MIN<=TASK_TEMP_MAX))
);
alter table RRL_INTERWARE_PUT_PLAN add(
 TEMP_DECISION_OPERATION_ID varchar2(100) references RRL_INTERWARE_THERMAL_FACT(OPERATION_ID),
 TASK_TEMP_MIN number(8,3),TASK_TEMP_MAX number(8,3)
);
