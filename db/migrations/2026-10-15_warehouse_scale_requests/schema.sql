-- MIGRATION_ID: 2026-10-15-warehouse-scale-requests
create table RRL_WH_WEIGH_REQUEST(
 REQUEST_ID varchar2(100) primary key,
 DEVICE_ID varchar2(100) not null references RRL_WH_SCALE_DEVICE(DEVICE_ID),
 CASE_PICK_TASK_ID number not null references RRL_CASE_PICK_TASK(CASE_PICK_TASK_ID),
 PURPOSE varchar2(12) not null check(PURPOSE in('PICK','EMPTY_TARE','FINAL_GROSS')),
 REQUESTED_BY nvarchar2(50) not null,
 SOURCE_JSON clob not null check(SOURCE_JSON is json),
 SNAPSHOT_SHA256 varchar2(64) not null,
 SNAPSHOT_JSON clob not null check(SNAPSHOT_JSON is json),
 CAPTURE_CONTEXT clob not null check(CAPTURE_CONTEXT is json),
 CREATED_AT timestamp with time zone not null,
 EXPIRES_AT timestamp with time zone not null,
 constraint RRL_WH_WEIGH_TTL_CK check(EXPIRES_AT=CREATED_AT+interval '120' second)
);
create index RRL_WH_WEIGH_DEVICE_I on RRL_WH_WEIGH_REQUEST(DEVICE_ID,EXPIRES_AT);
create table RRL_WH_WEIGH_CLAIM(
 CLAIM_ID varchar2(100) primary key,
 REQUEST_ID varchar2(100) not null references RRL_WH_WEIGH_REQUEST(REQUEST_ID),
 DEVICE_ID varchar2(100) not null references RRL_WH_SCALE_DEVICE(DEVICE_ID),
 CLAIMED_BY nvarchar2(50) not null,
 SOURCE_JSON clob not null check(SOURCE_JSON is json),
 CREATED_AT timestamp with time zone not null,
 EXPIRES_AT timestamp with time zone not null,
 constraint RRL_WH_CLAIM_TTL_CK check(EXPIRES_AT>CREATED_AT and EXPIRES_AT<=CREATED_AT+interval '30' second)
);
create index RRL_WH_CLAIM_REQUEST_I on RRL_WH_WEIGH_CLAIM(REQUEST_ID,EXPIRES_AT);
create or replace package RRL_WH_WEIGH_REQUEST_API authid definer as
 procedure request_capture(p_source clob,p_actor varchar2,p_result out clob);
 procedure request_status(p_request varchar2,p_actor varchar2,p_result out clob);
 procedure assert_device_available(p_device varchar2);
 procedure devices(p_task number,p_purpose varchar2,p_actor varchar2,p_result out clob);
 procedure pending_requests(p_device varchar2,p_actor varchar2,p_result out clob);
 procedure claim_request(p_request varchar2,p_source clob,p_actor varchar2,p_result out clob);
 procedure before_capture(p_source clob,p_actor varchar2);
 procedure validate_first_capture(p_source clob,p_actor varchar2);
 procedure assert_archived_sender(p_source clob,p_actor varchar2);
 procedure validate_archived(p_source clob,p_actor varchar2);
 procedure clear_capture_context;
 function writing(p_id varchar2,p_kind varchar2) return number;
end;
/
create or replace trigger RRL_WH_WEIGH_REQUEST_GUARD
before insert or update or delete on RRL_WH_WEIGH_REQUEST for each row
begin
 if updating or deleting then raise_application_error(-20886,'WH_WEIGH_REQUEST_APPEND_ONLY');end if;
 if RRL_WH_WEIGH_REQUEST_API.writing(:new.REQUEST_ID,'REQUEST')!=1 then raise_application_error(-20882,'WH_WEIGH_NATIVE_INSERT_REQUIRED');end if;
end;
/
create or replace trigger RRL_WH_WEIGH_CLAIM_GUARD
before insert or update or delete on RRL_WH_WEIGH_CLAIM for each row
begin
 if updating or deleting then raise_application_error(-20886,'WH_WEIGH_CLAIM_APPEND_ONLY');end if;
 if RRL_WH_WEIGH_REQUEST_API.writing(:new.CLAIM_ID,'CLAIM')!=1 then raise_application_error(-20882,'WH_WEIGH_NATIVE_CLAIM_REQUIRED');end if;
end;
/





