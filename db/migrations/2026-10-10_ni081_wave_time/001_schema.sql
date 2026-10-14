create table RRL_WAVE_TIME_PLAN(
 WAVE_ID number not null references RRL_PICK_WAVE(PICK_WAVE_ID),VERSION_NO number not null,
 OPERATION_ID varchar2(100)not null unique, ACTOR varchar2(50)not null,REQUEST_HASH varchar2(64)not null,
 WARE_ID number not null,ROUTE_ID number,DOCK_ID number,
 START_AT timestamp with time zone not null,FINISH_AT timestamp with time zone not null,
 TIME_ZONE varchar2(50)not null,LEGACY_START_AT date not null,LEGACY_FINISH_AT date not null,
 REASON varchar2(1000)not null,RESULT_JSON clob not null check(RESULT_JSON is json),
 CREATED_AT timestamp with time zone default systimestamp not null,
 constraint RRL_WAVE_TIME_PLAN_PK primary key(WAVE_ID,VERSION_NO),
 constraint RRL_WAVE_TIME_PLAN_PERIOD_CK check(FINISH_AT>START_AT)
);
/
