create table RRL_ASSEMBLY_STATION(
 DEVICE_ID varchar2(100)primary key,VERSION_NO number not null,CONFIRMATION_MODE varchar2(10)not null,
 MAX_SESSION_SECONDS number not null,CUMULATIVE_TOLERANCE_KG number not null,ACTIVE_FLAG number(1)not null,CHANGED_BY nvarchar2(50)not null,
 CHANGED_AT timestamp with time zone default systimestamp not null,
 check(CONFIRMATION_MODE in('AUTO','BUTTON')),check(MAX_SESSION_SECONDS between 60 and 28800),check(CUMULATIVE_TOLERANCE_KG>=0),check(ACTIVE_FLAG in(0,1))
);
create table RRL_ASSEMBLY_SKU_POLICY(
 WARE_ID number not null,ARTICUL varchar2(100)not null,BASE_UOM varchar2(20)not null,
 VERSION_NO number not null,MIN_UNIT_KG number not null,MAX_UNIT_KG number not null,MIN_DELTA_KG number not null,
 TOLERANCE_KG number not null,ACTIVE_FLAG number(1)not null,EVIDENCE_REFERENCE varchar2(200)not null,
 CHANGED_BY nvarchar2(50)not null,CHANGED_AT timestamp with time zone default systimestamp not null,
 primary key(WARE_ID,ARTICUL),check(BASE_UOM='EA'),check(MIN_UNIT_KG>0 and MAX_UNIT_KG>=MIN_UNIT_KG),
 check(MIN_DELTA_KG>0 and TOLERANCE_KG>=0),check(ACTIVE_FLAG in(0,1))
);
create table RRL_ASSEMBLY_POLICY_EVENT(
 OPERATION_ID varchar2(100)not null unique,POLICY_KIND varchar2(20)not null,POLICY_KEY varchar2(255)not null,VERSION_NO number not null,
 SOURCE_JSON clob not null check(SOURCE_JSON is json),ACTOR nvarchar2(50)not null,
 RECORDED_AT timestamp with time zone default systimestamp not null,primary key(POLICY_KIND,POLICY_KEY,VERSION_NO)
);
create table RRL_ASSEMBLY_SESSION(
 SESSION_ID varchar2(100)primary key,CASE_PICK_TASK_ID number not null,DEVICE_ID varchar2(100)not null,
 WARE_ID number not null,POST_CELL varchar2(60)not null,OPERATOR_ID nvarchar2(50)not null,SENDER_ID nvarchar2(50)not null,
 CARRIER_IDENTIFIER varchar2(150)not null,TARE_CAPTURE_KEY varchar2(64)not null,
 DEVICE_POLICY_VERSION number not null,STATION_POLICY_VERSION number not null,DEVICE_MODE varchar2(20)not null,
 CALIBRATION_REF varchar2(100)not null,CONFIRMATION_MODE varchar2(10)not null,CUMULATIVE_TOLERANCE_KG number not null,
 INITIAL_CONTENT_VERSION number not null,LAST_CONTENT_VERSION number not null,LAST_SEQUENCE number default 0 not null,
 TARE_WEIGHT_KG number not null,LAST_WEIGHT_KG number not null,STATE varchar2(20)not null,
 OPENED_AT timestamp with time zone default systimestamp not null,EXPIRES_AT timestamp with time zone not null,
 REQUEST_JSON clob not null check(REQUEST_JSON is json),FINAL_CAPTURE_KEY varchar2(64),BLOCK_REASON varchar2(200),
 check(CUMULATIVE_TOLERANCE_KG>=0),check(STATE in('OPEN','BLOCKED','FINALIZED')),check(CONFIRMATION_MODE in('AUTO','BUTTON'))
);
create unique index RRL_ASSEMBLY_DEVICE_OPEN_UK on RRL_ASSEMBLY_SESSION(case when STATE in('OPEN','BLOCKED')then DEVICE_ID end);
create unique index RRL_ASSEMBLY_TASK_OPEN_UK on RRL_ASSEMBLY_SESSION(case when STATE in('OPEN','BLOCKED')then CASE_PICK_TASK_ID end);
create table RRL_ASSEMBLY_STEP(
 STEP_ID varchar2(100)primary key,SESSION_ID varchar2(100)not null,OPERATION_ID varchar2(100)not null unique,
 SEQUENCE_NO number not null,CASE_PICK_LINE_ID number not null,ARTICUL varchar2(100)not null,
 SOURCE_VERSION number not null,PREVIOUS_QTY number not null,QUANTITY number not null,FACT_QTY number not null,
 SCAN_SOURCE_CELL varchar2(60)not null,SCAN_PRODUCT varchar2(512)not null,SCAN_CONTAINER varchar2(150)not null,
 SKU_POLICY_VERSION number not null,MIN_DELTA_KG number not null,LOWER_DELTA_KG number not null,UPPER_DELTA_KG number not null,
 CONSENT_TO_AUTO number(1)not null,BUTTON_INTENT_AT timestamp with time zone,
 STATE varchar2(30)not null,BEFORE_CAPTURE_ID varchar2(100)not null,AFTER_CAPTURE_ID varchar2(100)not null,
 BEFORE_WEIGHT_KG number,AFTER_WEIGHT_KG number,DELTA_KG number,BLOCK_REASON varchar2(200),
 OPENED_AT timestamp with time zone default systimestamp not null,REQUEST_JSON clob not null check(REQUEST_JSON is json),
 foreign key(SESSION_ID)references RRL_ASSEMBLY_SESSION(SESSION_ID),unique(SESSION_ID,SEQUENCE_NO),
 check(STATE in('WAITING_BEFORE','ARMED','READY','APPLIED','DISCREPANCY')),check(CONSENT_TO_AUTO in(0,1)),
 check(QUANTITY>0 and QUANTITY=trunc(QUANTITY)),check(LOWER_DELTA_KG>0 and UPPER_DELTA_KG>=LOWER_DELTA_KG)
);
create table RRL_ASSEMBLY_CAPTURE(
 DEVICE_ID varchar2(100)not null,CAPTURE_ID varchar2(100)not null,SESSION_ID varchar2(100)not null,STEP_ID varchar2(100)not null,
 PHASE varchar2(10)not null,WARE_ID number not null,POST_CELL varchar2(60)not null,
 WEIGHT_KG number not null,MEASURED_AT timestamp with time zone not null,DEVICE_POLICY_VERSION number not null,
 SOURCE_SHA256 varchar2(64)not null,SOURCE_JSON clob not null check(SOURCE_JSON is json),
 RESULT_JSON clob not null check(RESULT_JSON is json),RECORDED_BY nvarchar2(50)not null,
 RECORDED_AT timestamp with time zone default systimestamp not null,
 primary key(DEVICE_ID,CAPTURE_ID),unique(STEP_ID,PHASE),foreign key(STEP_ID)references RRL_ASSEMBLY_STEP(STEP_ID),
 check(PHASE in('BEFORE','AFTER'))
);
create table RRL_ASSEMBLY_STEP_USE(
 STEP_ID varchar2(100)primary key,STOCK_OPERATION_ID varchar2(100)not null unique,OPERATOR_ID nvarchar2(50)not null,
 USED_AT timestamp with time zone default systimestamp not null,
 foreign key(STEP_ID)references RRL_ASSEMBLY_STEP(STEP_ID)
);
