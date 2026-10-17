create table RRL_OPC_SCALE_EVIDENCE(
 CAPTURE_KIND varchar2(30)not null,CAPTURE_DEVICE varchar2(100)not null,CAPTURE_ID varchar2(100)not null,
 CAPTURE_SHA256 varchar2(64)not null,EVIDENCE_SHA256 varchar2(64)not null,
 DEVICE_SCOPE varchar2(255)not null,DEVICE_POST varchar2(100),RECORDED_BY nvarchar2(50)not null,
 RECORDED_AT timestamp with time zone default systimestamp not null,
 SOURCE_JSON clob not null check(SOURCE_JSON is json),
 constraint RRL_OPC_EVIDENCE_PK primary key(CAPTURE_KIND,CAPTURE_DEVICE,CAPTURE_ID),
 constraint RRL_OPC_EVIDENCE_KIND_CK check(CAPTURE_KIND in('STORE_RECEIPT','WAREHOUSE_PICK','WAREHOUSE_FINAL')),
 constraint RRL_OPC_EVIDENCE_SHA_CK check(regexp_like(CAPTURE_SHA256,'^[A-F0-9]{64}$')and regexp_like(EVIDENCE_SHA256,'^[A-F0-9]{64}$'))
);
create or replace package RRL_OPC_EVIDENCE_API authid definer as
 procedure archive(p_source clob,p_actor nvarchar2,p_result out clob);
 procedure describe(p_kind varchar2,p_device varchar2,p_capture varchar2,p_actor nvarchar2,p_result out clob);
end;
/
create context RRL_OPC_EVIDENCE_CTX using RRL_OPC_EVIDENCE_API;
create or replace trigger RRL_OPC_EVIDENCE_GUARD before insert or update or delete on RRL_OPC_SCALE_EVIDENCE for each row
begin
 if not inserting then raise_application_error(-20886,'OPC_EVIDENCE_APPEND_ONLY');end if;
 if sys_context('RRL_OPC_EVIDENCE_CTX','TX_ID')is null
  or sys_context('RRL_OPC_EVIDENCE_CTX','TX_ID')!=dbms_transaction.local_transaction_id(false)
  or sys_context('RRL_OPC_EVIDENCE_CTX','HASH')!=:new.EVIDENCE_SHA256
  or sys_context('RRL_OPC_EVIDENCE_CTX','HASH')is null then raise_application_error(-20882,'OPC_EVIDENCE_NATIVE_CONTEXT_REQUIRED');end if;
end;
/
