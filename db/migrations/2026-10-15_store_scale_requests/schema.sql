-- MIGRATION_ID: 2026-10-15-store-scale-requests
create table RRL_STORE_WEIGH_REQUEST (
 REQUEST_ID varchar2(100) primary key,
 DEVICE_ID varchar2(100) not null references RRL_STORE_SCALE_DEVICE(DEVICE_ID),
 LOAD_OPERATION_ID varchar2(100) not null references RRL_TT_HU_LOAD_FACT(LOAD_OPERATION_ID),
 STORE_ADDR varchar2(255) not null references RRL_STORE_RECEIPT_POLICY(STORE_ADDR),
 REQUESTED_BY nvarchar2(50) not null,
 COMPOSITION_SIGNATURE varchar2(64) not null,
 RECEIPT_POLICY_VERSION number(10) not null,
 DEVICE_POLICY_VERSION number(10) not null,
 CALIBRATION_REF varchar2(100) not null,
 CREATED_AT timestamp with time zone default systimestamp not null,
 EXPIRES_AT timestamp with time zone not null,
 SOURCE_JSON clob not null check(SOURCE_JSON is json),
 constraint RRL_STORE_WEIGH_TTL_CK check(EXPIRES_AT=CREATED_AT+interval '120' second)
);
create index RRL_STORE_WEIGH_DEVICE_IDX on RRL_STORE_WEIGH_REQUEST(DEVICE_ID,EXPIRES_AT);
create or replace package RRL_STORE_WEIGH_API authid definer as
 procedure request_capture(p_source clob,p_actor varchar2,p_result out clob);
 procedure request_status(p_request varchar2,p_actor varchar2,p_result out clob);
 procedure devices(p_load varchar2,p_store varchar2,p_actor varchar2,p_result out clob);
 procedure pending_requests(p_device varchar2,p_actor varchar2,p_result out clob);
end;
/
create context RRL_STORE_WEIGH_CTX using RRL_STORE_WEIGH_API;
create or replace trigger RRL_STORE_WEIGH_GUARD
before insert or update or delete on RRL_STORE_WEIGH_REQUEST for each row
begin
 if updating or deleting then raise_application_error(-20886,'WEIGH_REQUEST_APPEND_ONLY');end if;
 if sys_context('RRL_STORE_WEIGH_CTX','TX_ID') is null
 or sys_context('RRL_STORE_WEIGH_CTX','TX_ID')!=dbms_transaction.local_transaction_id(false)
 or sys_context('RRL_STORE_WEIGH_CTX','REQUEST_ID')!=:new.REQUEST_ID then
  raise_application_error(-20882,'WEIGH_REQUEST_NATIVE_WRITE_REQUIRED');
 end if;
end;
/