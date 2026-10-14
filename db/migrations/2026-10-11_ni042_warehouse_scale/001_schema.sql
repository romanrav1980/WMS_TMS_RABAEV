-- MIGRATION_ID:2026-10-11-187-warehouse-scale-archive
create table RRL_WH_SCALE_DEVICE(
 DEVICE_ID varchar2(100)primary key,WARE_ID number not null,POST_CELL varchar2(60)not null,
 SENDER_ID nvarchar2(50)not null,POLICY_VERSION number(10)default 1 not null check(POLICY_VERSION>=1),
 ACTIVE_FLAG number(1)default 0 not null check(ACTIVE_FLAG in(0,1)),
 DEVICE_MODE varchar2(10)not null check(DEVICE_MODE in('TEST','HARDWARE')),
 MEASUREMENT_BASIS varchar2(5)not null check(MEASUREMENT_BASIS in('NET','GROSS')),
 CAPACITY_KG number(27,9)not null check(CAPACITY_KG>0),RESOLUTION_KG number(27,9)not null check(RESOLUTION_KG>0),
 CALIBRATION_REF varchar2(100)not null,CALIBRATED_UNTIL timestamp with time zone not null,
 CHANGED_BY varchar2(50)not null,CHANGED_AT timestamp with time zone default systimestamp not null);
create table RRL_WH_SCALE_CAPTURE(
 CAPTURE_KEY varchar2(64)primary key,DEVICE_ID varchar2(100)not null references RRL_WH_SCALE_DEVICE(DEVICE_ID),
 CAPTURE_ID varchar2(100)not null,WARE_ID number not null,POST_CELL varchar2(60)not null,
 CASE_PICK_TASK_ID number not null references RRL_CASE_PICK_TASK(CASE_PICK_TASK_ID),
 CASE_PICK_LINE_ID number not null references RRL_CASE_PICK_LINE(CASE_PICK_LINE_ID),
 CASE_CONTENT_VERSION number not null,ARTICLE varchar2(160)not null,SOURCE_CELL varchar2(60)not null,
 CARRIER_IDENTIFIER varchar2(150)not null,SCANNED_PRODUCT varchar2(512)not null,
 DEVICE_POLICY_VERSION number(10)not null,DEVICE_MODE varchar2(10)not null,
 MEASUREMENT_BASIS varchar2(5)not null,WEIGHT_KG number(27,9)not null check(WEIGHT_KG>0),
 RESOLUTION_KG number(27,9)not null,CALIBRATION_REF varchar2(100)not null,
 MEASURED_AT timestamp with time zone not null,RECEIVED_AT timestamp with time zone default systimestamp not null,
 RECORDED_BY varchar2(50)not null,SOURCE_SHA256 varchar2(64)not null,
 SOURCE_JSON clob not null check(SOURCE_JSON is json),RESULT_JSON clob not null check(RESULT_JSON is json),
 unique(DEVICE_ID,CAPTURE_ID));
create index RRL_WH_SCALE_LINE_IDX on RRL_WH_SCALE_CAPTURE(CASE_PICK_TASK_ID,CASE_PICK_LINE_ID,RECEIVED_AT);
