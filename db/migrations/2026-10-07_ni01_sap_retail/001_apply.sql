prompt NI01: SAP Retail ARTMAS10 inbox and SKU receiving policies in RABAEV
declare
 procedure ensure_table(p_name varchar2,p_ddl varchar2) is n number;
 begin
  select count(*) into n from user_tables where table_name=p_name;
  if n=0 then execute immediate p_ddl; end if;
 end;
begin
 if user!='RABAEV' or lower(sys_context('USERENV','SERVICE_NAME'))!='orcl' then
  raise_application_error(-20801,'NI01 targets existing RABAEV/orcl only');
 end if;
 ensure_table('RRL_SKU_RECEIPT_POLICY',q'[
 create table RRL_SKU_RECEIPT_POLICY (
 ARTICUL varchar2(40) not null,POLICY_VERSION number not null,MARKING_REQUIRED number(1) not null,
 UPDATED_AT timestamp default systimestamp not null,UPDATED_BY varchar2(100) not null,
 constraint RRL_SKU_RPOL_PK primary key(ARTICUL),
 constraint RRL_SKU_RPOL_VER_CK check(POLICY_VERSION>0),
 constraint RRL_SKU_RPOL_MARK_CK check(MARKING_REQUIRED in(0,1)))]');
 ensure_table('RRL_SKU_RECEIPT_PROFILE',q'[
 create table RRL_SKU_RECEIPT_PROFILE (
 ARTICUL varchar2(40) not null,SYSTEM_CODE varchar2(40) not null,
 PROFILE_CODE varchar2(80) not null,PROFILE_VERSION varchar2(40) not null,SCAN_MODE varchar2(40) not null,
 constraint RRL_SKU_RPROF_PK primary key(ARTICUL,SYSTEM_CODE,PROFILE_CODE),
 constraint RRL_SKU_RPROF_FK foreign key(ARTICUL) references RRL_SKU_RECEIPT_POLICY(ARTICUL),
 constraint RRL_SKU_RPROF_SCAN_CK check(SCAN_MODE in('UNIT','BOX','PALLET','UNIT_OR_AGGREGATION')))]');
 ensure_table('RRL_SKU_RECEIPT_POLICY_LOG',q'[
 create table RRL_SKU_RECEIPT_POLICY_LOG (
 ARTICUL varchar2(40) not null,POLICY_VERSION number not null,POLICY_JSON clob not null,
 CHANGED_AT timestamp default systimestamp not null,CHANGED_BY varchar2(100) not null,
 constraint RRL_SKU_RPLOG_PK primary key(ARTICUL,POLICY_VERSION),
 constraint RRL_SKU_RPLOG_JSON_CK check(POLICY_JSON is json))]');
 ensure_table('RRL_SAP_IDOC_INBOX',q'[
 create table RRL_SAP_IDOC_INBOX (
 INBOX_ID varchar2(32) not null,SENDER varchar2(100) not null,DOCNUM varchar2(16) not null,
 MESSAGE_TYPE varchar2(30) not null,BASIC_TYPE varchar2(30) not null,EXTENSION_TYPE varchar2(80),
 PAYLOAD_HASH varchar2(64) not null,RAW_XML clob not null,PARSED_JSON clob not null,
 STATUS varchar2(20) default 'RECEIVED' not null,RECEIVED_AT timestamp default systimestamp not null,
 RECEIVED_BY varchar2(100) not null,
 constraint RRL_SAP_IDOC_PK primary key(INBOX_ID),
 constraint RRL_SAP_IDOC_DOC_UK unique(SENDER,DOCNUM),
 constraint RRL_SAP_IDOC_JSON_CK check(PARSED_JSON is json),
 constraint RRL_SAP_IDOC_STATUS_CK check(STATUS in('RECEIVED','APPLIED','ERROR')))]');
end;
/
merge into RRL_SCHEMA_MIGRATIONS d
using(select '2026-10-07-001-ni01-sap-retail' MIGRATION_ID from dual)s
on(d.MIGRATION_ID=s.MIGRATION_ID)
when not matched then insert(MIGRATION_ID,DESCRIPTION,APPLIED_AT,APPLIED_BY,SCRIPT_NAME,ROLLBACK_SCRIPT,STATUS)
values(s.MIGRATION_ID,'NI01 SAP Retail ARTMAS10 inbox and SKU receiving policies',sysdate,user,'001_apply.sql','001_rollback.sql','APPLIED');
commit;