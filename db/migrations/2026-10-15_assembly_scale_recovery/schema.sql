create table RRL_ASM_RECONCILIATION(
 RECONCILIATION_ID varchar2(100)primary key,SESSION_ID varchar2(100)not null,STEP_ID varchar2(100)not null,
 EXPECTED_CONTENT_VERSION number not null,EXPECTED_WEIGHT_KG number not null,STATE varchar2(20)not null,
 REQUESTER_ID nvarchar2(50)not null,REQUESTED_AT timestamp with time zone default systimestamp not null,
 REQUEST_JSON clob not null check(REQUEST_JSON is json),REQUEST_RESULT clob not null check(REQUEST_RESULT is json),
 AUTHORIZE_OPERATION_ID varchar2(100)unique,CONTROLLER_ID nvarchar2(50),AUTHORIZED_AT timestamp with time zone,
 AUTHORIZE_JSON clob check(AUTHORIZE_JSON is json),AUTHORIZE_RESULT clob check(AUTHORIZE_RESULT is json),
 CAPTURE_ID varchar2(100)not null,COMPLETED_AT timestamp with time zone,
 foreign key(SESSION_ID)references RRL_ASSEMBLY_SESSION(SESSION_ID),foreign key(STEP_ID)references RRL_ASSEMBLY_STEP(STEP_ID),
 check(STATE in('REQUESTED','AUTHORIZED','COMPLETED','DISCREPANCY'))
);
create unique index RRL_ASM_RECON_OPEN_UK on RRL_ASM_RECONCILIATION(case when STATE in('REQUESTED','AUTHORIZED')then SESSION_ID end);
create table RRL_ASM_RECON_CAPTURE(
 DEVICE_ID varchar2(100)not null,CAPTURE_ID varchar2(100)not null,RECONCILIATION_ID varchar2(100)not null unique,
 SESSION_ID varchar2(100)not null,STEP_ID varchar2(100)not null,WARE_ID number not null,POST_CELL varchar2(60)not null,
 WEIGHT_KG number not null,MEASURED_AT timestamp with time zone not null,DEVICE_POLICY_VERSION number not null,
 SOURCE_SHA256 varchar2(64)not null,SOURCE_JSON clob not null check(SOURCE_JSON is json),RESULT_JSON clob not null check(RESULT_JSON is json),
 RECORDED_BY nvarchar2(50)not null,RECORDED_AT timestamp with time zone default systimestamp not null,
 primary key(DEVICE_ID,CAPTURE_ID),foreign key(RECONCILIATION_ID)references RRL_ASM_RECONCILIATION(RECONCILIATION_ID)
);
declare name_value varchar2(128);begin
 select CONSTRAINT_NAME into name_value from USER_CONSTRAINTS where TABLE_NAME='RRL_ASSEMBLY_STEP'and CONSTRAINT_TYPE='C'and lower(SEARCH_CONDITION_VC) like '%state in%';
 execute immediate 'alter table RRL_ASSEMBLY_STEP drop constraint '||dbms_assert.simple_sql_name(name_value);
end;
/
alter table RRL_ASSEMBLY_STEP add constraint RRL_ASM_STEP_STATE_CK check(STATE in('WAITING_BEFORE','ARMED','READY','APPLIED','DISCREPANCY','CANCELLED'));
